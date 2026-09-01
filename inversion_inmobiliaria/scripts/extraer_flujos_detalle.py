import pandas as pd, numpy as np, json

props = pd.DataFrame([
 ("W05.102","Copacabana", 78,2,3,1_150_000,1_100, 2_360,0),
 ("W06.914","Copacabana",170,3,5,1_600_000,2_740, 3_475,0),
 ("W06.931","Copacabana",149,3,4,1_700_000,3_280, 5_862,1),
 ("W06.935","Ipanema",    70,2,2,1_650_000,1_147, 2_370,0),
 ("W06.922","Ipanema",    88,1,1,1_950_000,2_400, 7_113,1),
 ("W06.924","Lagoa",      63,1,1,1_520_000,1_292, 3_607,1),
 ("W06.481","Gávea",     118,3,2,2_100_000,2_143, 5_129,1),
 ("W06.936","Lagoa",      96,3,2,2_550_000,1_700, 6_445,0),
 ("W06.947","Leblon",     85,2,1,2_100_000,  862, 5_952,0),
 ("W06.345","Leblon",     99,3,2,2_100_000,1_200, 4_828,0),
 ("W06.620","Ipanema",   138,4,2,2_945_000,2_199, 9_130,2),
 ("W06.725","Flamengo",  290,4,2,3_220_000,2_689,14_387,1),
], columns=["ref","barrio","m2","dorm","banos","precio","cond_mes","iptu","garaje"])

comp = pd.read_pickle('/home/claude/work/comparables.pkl').rename(columns={'neighbourhood_cleansed':'barrio'})
comp['dorm'] = comp['dorm'].astype(int)
extra = {("Gávea",3): dict(n=8, precio_med=958.0, precio_p75=1425.0, ocup_med=24.0, ocup_p75=52.0),
         ("Flamengo",4): dict(n=4, precio_med=642.0, precio_p75=826.0, ocup_med=36.0, ocup_p75=64.0)}
def buscar_comp(barrio, dorm):
    d = min(dorm,4)
    m = comp[(comp['barrio']==barrio)&(comp['dorm']==d)]
    if len(m):
        r = m.iloc[0]
        return dict(n=int(r['n']), precio_med=r['precio_med'], precio_p75=r['precio_p75'],
                    ocup_med=r['ocup_med'], ocup_p75=r['ocup_p75'])
    return extra[(barrio,d)]

S = dict(itbi=0.03, escritura=0.015, amoblado_por_m2=1_000, comision_airbnb=0.03, gestion=0.20,
         mantenimiento_seguro=0.002, energia_base_mes=40, energia_por_noche=4.0,
         factor_ocup_otros_canales=1.30, ir_renta=0.075, apreciacion=0.055,
         inflacion_costos=0.04, ajuste_tarifa=0.04, horizonte=10, costo_venta=0.06, tasa_desc=0.0712)

def flujo_detallado(p, tarifa, noches_airbnb):
    noches = noches_airbnb * S['factor_ocup_otros_canales']
    inversion = p.precio*(1+S['itbi']+S['escritura']) + p.m2*S['amoblado_por_m2']
    filas = [dict(anio=0, bruto=0, fijos=0, resultado_antes_ir=-inversion, flujo_neto=-inversion,
                  flujo_descontado=-inversion, flujo_acumulado=-inversion)]
    acumulado = -inversion
    for t in range(1, S['horizonte']+1):
        bruto = tarifa*noches*(1+S['ajuste_tarifa'])**t
        energia = (S['energia_base_mes']*12 + S['energia_por_noche']*noches)*(1+S['inflacion_costos'])**t
        fijos = (p.cond_mes*12+p.iptu)*(1+S['inflacion_costos'])**t + energia + p.precio*S['mantenimiento_seguro']
        neto_plataforma = bruto*(1-S['comision_airbnb']-S['gestion'])
        resultado = neto_plataforma - fijos
        flujo_neto = resultado*(1-S['ir_renta']) if resultado > 0 else resultado
        if t == S['horizonte']:
            valor_residual = p.precio*(1+S['apreciacion'])**S['horizonte']*(1-S['costo_venta'])
            flujo_neto += valor_residual
        descontado = flujo_neto/(1+S['tasa_desc'])**t
        acumulado += flujo_neto
        filas.append(dict(anio=t, bruto=round(bruto), fijos=round(fijos),
                          resultado_antes_ir=round(resultado), flujo_neto=round(flujo_neto),
                          flujo_descontado=round(descontado), flujo_acumulado=round(acumulado)))
    return pd.DataFrame(filas), inversion

todas = []
for p in props.itertuples():
    c = buscar_comp(p.barrio, p.dorm)
    df, inv = flujo_detallado(p, c['precio_med'], c['ocup_med'])
    df.insert(0, 'ref', p.ref)
    df.insert(1, 'barrio', p.barrio)
    todas.append(df)
detalle = pd.concat(todas, ignore_index=True)
detalle.to_csv('/home/claude/inversion/flujo_detallado_10_anios.csv', index=False)
print(detalle.head(12).to_string(index=False))
print()
print("Total filas:", len(detalle), "| Propiedades:", detalle['ref'].nunique())
