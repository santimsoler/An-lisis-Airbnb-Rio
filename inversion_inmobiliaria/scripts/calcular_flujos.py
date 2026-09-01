import pandas as pd, numpy as np, json

# ---------------------------------------------------------------
# 1. Propiedades relevadas
# ---------------------------------------------------------------
props = pd.DataFrame([
 ("W05.102","Copacabana", 78,2,3,1_150_000,1_100, 2_360,0,"78 m2 ficha"),
 ("W06.914","Copacabana",170,3,5,1_600_000,2_740, 3_475,0,"unidad independiente, entrada privada"),
 ("W06.931","Copacabana",149,3,4,1_700_000,3_280, 5_862,1,"ficha 149 m2 / descripción 155 m2"),
 ("W06.935","Ipanema",    70,2,2,1_650_000,1_147, 2_370,0,"recepción 24h"),
 ("W06.922","Ipanema",    88,1,1,1_950_000,2_400, 7_113,1,""),
 ("W06.924","Lagoa",      63,1,1,1_520_000,1_292, 3_607,1,""),
 ("W06.481","Gávea",     118,3,2,2_100_000,2_143, 5_129,1,"edificio de 1957; comparables escasos (n=8)"),
 ("W06.936","Lagoa",      96,3,2,2_550_000,1_700, 6_445,0,"seguridad 24h"),
 ("W06.947","Leblon",     85,2,1,2_100_000,  862, 5_952,0,"sin ascensor, sin garaje"),
 ("W06.345","Leblon",     99,3,2,2_100_000,1_200, 4_828,0,"Rua Dias Ferreira, sin garaje"),
 ("W06.620","Ipanema",   138,4,2,2_945_000,2_199, 9_130,2,"reformado"),
 ("W06.725","Flamengo",  290,4,2,3_220_000,2_689,14_387,1,"vista al mar; comparables escasos (n=4)"),
], columns=["ref","barrio","m2","dorm","banos","precio","cond_mes","iptu","garaje","notas"])

# ---------------------------------------------------------------
# 2. Comparables Inside Airbnb (barrio x dormitorios, listados activos)
# ---------------------------------------------------------------
comp = pd.read_pickle('/home/claude/work/comparables.pkl').rename(columns={'neighbourhood_cleansed':'barrio'})
comp['dorm'] = comp['dorm'].astype(int)

# Gávea 3d y Flamengo 4d: muestra insuficiente en el corte exacto, se usan directamente
# los valores ya inspeccionados manualmente (n=8 y n=4)
extra = {
    ("Gávea",3):     dict(n=8, precio_med=958.0,  precio_p75=1425.0, ocup_med=24.0, ocup_p75=52.0),
    ("Flamengo",4):  dict(n=4, precio_med=642.0,  precio_p75=826.0,  ocup_med=36.0, ocup_p75=64.0),
}

def buscar_comp(barrio, dorm):
    d = min(dorm, 4)
    m = comp[(comp['barrio']==barrio) & (comp['dorm']==d)]
    if len(m):
        r = m.iloc[0]
        return dict(n=int(r['n']), precio_med=r['precio_med'], precio_p75=r['precio_p75'],
                    ocup_med=r['ocup_med'], ocup_p75=r['ocup_p75'])
    return extra.get((barrio, d))

# ---------------------------------------------------------------
# 3. Supuestos finales (definidos junto al usuario)
# ---------------------------------------------------------------
S = dict(
    itbi=0.03, escritura=0.015, amoblado_por_m2=1_000,
    comision_airbnb=0.03, gestion=0.20,
    mantenimiento_seguro=0.002,      # 0,2% anual del valor del inmueble (mantenimiento + seguro)
    energia_base_mes=40, energia_por_noche=4.0,
    factor_ocup_otros_canales=1.30,  # +30% de noches por canales fuera de Airbnb
    ir_renta=0.075,                  # 7,5% promedio de escalas brasileñas
    apreciacion=0.055,                # revalorización nominal anual (histórico Río 20 años, dato del autor) -> precio residual = precio actual x (1+5,5%)^10
    inflacion_costos=0.04,
    ajuste_tarifa=0.04,
    horizonte=10,
    costo_venta=0.06,
    tasa_desc=0.0712,                # IPCA+ (Tesouro), tasa libre de riesgo real, sin prima de riesgo adicional
)

def npv(fc, r):
    return sum(f/(1+r)**i for i, f in enumerate(fc))

def tir_biseccion(fc):
    lo, hi = -0.9, 2.0
    if npv(fc, lo) * npv(fc, hi) > 0:
        return np.nan
    for _ in range(200):
        mid = (lo+hi)/2
        if npv(fc, lo) * npv(fc, mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2

def flujo(p, tarifa, noches_airbnb, S=S):
    noches = noches_airbnb * S['factor_ocup_otros_canales']
    inversion = p.precio*(1+S['itbi']+S['escritura']) + p.m2*S['amoblado_por_m2']

    bruto_y1 = tarifa*noches
    energia_y1 = S['energia_base_mes']*12 + S['energia_por_noche']*noches
    fijos_y1 = p.cond_mes*12 + p.iptu + energia_y1 + p.precio*S['mantenimiento_seguro']
    neto_plat_y1 = bruto_y1*(1-S['comision_airbnb']-S['gestion'])
    noi_y1 = neto_plat_y1 - fijos_y1

    fc = [-inversion]
    for t in range(1, S['horizonte']+1):
        bruto_t = tarifa*noches*(1+S['ajuste_tarifa'])**t
        energia_t = (S['energia_base_mes']*12 + S['energia_por_noche']*noches)*(1+S['inflacion_costos'])**t
        fijos_t = (p.cond_mes*12+p.iptu)*(1+S['inflacion_costos'])**t + energia_t + p.precio*S['mantenimiento_seguro']
        n = bruto_t*(1-S['comision_airbnb']-S['gestion']) - fijos_t
        fc.append(n*(1-S['ir_renta']) if n > 0 else n)
    valor_residual = p.precio*(1+S['apreciacion'])**S['horizonte']*(1-S['costo_venta'])
    fc[-1] += valor_residual

    return dict(
        inversion=inversion, noches_efectivas=noches,
        bruto_y1=bruto_y1, fijos_y1=fijos_y1, noi_y1=noi_y1,
        cap_rate=noi_y1/inversion,
        van=npv(fc, S['tasa_desc']), tir=tir_biseccion(fc),
        valor_residual=valor_residual, flujos=fc,
    )

# ---------------------------------------------------------------
# 4. Cálculo — escenario base (mediana de mercado) y alto (percentil 75)
# ---------------------------------------------------------------
filas = []
for p in props.itertuples():
    c = buscar_comp(p.barrio, p.dorm)
    base = flujo(p, c['precio_med'], c['ocup_med'])
    alto = flujo(p, c['precio_p75'], c['ocup_p75'])
    # punto de equilibrio (noches Airbnb necesarias, antes del factor de otros canales)
    fijos_sin_energia_var = p.cond_mes*12 + p.iptu + S['energia_base_mes']*12 + p.precio*S['mantenimiento_seguro']
    ingreso_neto_x_noche = c['precio_med']*(1-S['comision_airbnb']-S['gestion']) - S['energia_por_noche']
    be_noches = fijos_sin_energia_var / ingreso_neto_x_noche

    filas.append(dict(
        ref=p.ref, barrio=p.barrio, m2=p.m2, dorm=p.dorm, precio=p.precio,
        cond_mes=p.cond_mes, iptu=p.iptu, notas=p.notas, n_comparables=c['n'],
        tarifa_med=c['precio_med'], noches_airbnb_med=c['ocup_med'],
        tarifa_p75=c['precio_p75'], noches_airbnb_p75=c['ocup_p75'],
        be_noches_airbnb=be_noches,
        inversion=base['inversion'],
        bruto_base=base['bruto_y1'], fijos_base=base['fijos_y1'], noi_base=base['noi_y1'],
        cap_base=base['cap_rate'], van_base=base['van'], tir_base=base['tir'],
        bruto_alto=alto['bruto_y1'], fijos_alto=alto['fijos_y1'], noi_alto=alto['noi_y1'],
        cap_alto=alto['cap_rate'], van_alto=alto['van'], tir_alto=alto['tir'],
        valor_residual=base['valor_residual'],
    ))

res = pd.DataFrame(filas).sort_values('van_base', ascending=False).reset_index(drop=True)
res.to_pickle('resultados_finales.pkl')
res.to_csv('resultados_finales.csv', index=False)
json.dump(S, open('supuestos.json','w'), indent=2)

pd.set_option('display.width', 220)
cols_show = ['ref','barrio','dorm','precio','inversion','noi_base','cap_base','van_base','tir_base']
show = res[cols_show].copy()
show['cap_base'] = (show['cap_base']*100).round(2)
show['tir_base'] = (show['tir_base']*100).round(2)
show['van_base'] = show['van_base'].round(0)
print(show.to_string(index=False))
