import pandas as pd, numpy as np, json

props = pd.DataFrame([
 ("W05.102","Copacabana", 78,2,1_150_000,1_100, 2_360),
 ("W06.914","Copacabana",170,3,1_600_000,2_740, 3_475),
 ("W06.931","Copacabana",149,3,1_700_000,3_280, 5_862),
 ("W06.935","Ipanema",    70,2,1_650_000,1_147, 2_370),
 ("W06.922","Ipanema",    88,1,1_950_000,2_400, 7_113),
 ("W06.924","Lagoa",      63,1,1_520_000,1_292, 3_607),
 ("W06.481","Gávea",     118,3,2_100_000,2_143, 5_129),
 ("W06.936","Lagoa",      96,3,2_550_000,1_700, 6_445),
 ("W06.947","Leblon",     85,2,2_100_000,  862, 5_952),
 ("W06.345","Leblon",     99,3,2_100_000,1_200, 4_828),
 ("W06.620","Ipanema",   138,4,2_945_000,2_199, 9_130),
 ("W06.725","Flamengo",  290,4,3_220_000,2_689,14_387),
], columns=["ref","barrio","m2","dorm","precio","cond_mes","iptu"])

comp = pd.read_pickle('/home/claude/work/comparables.pkl').rename(columns={'neighbourhood_cleansed':'barrio'})
comp['dorm'] = comp['dorm'].astype(int)
extra = {
    ("Gávea",3):    dict(precio_med=958.0,  ocup_med=24.0),
    ("Flamengo",4): dict(precio_med=642.0,  ocup_med=36.0),
}
def tarifa_ocup(barrio, dorm):
    d = min(dorm,4)
    m = comp[(comp['barrio']==barrio)&(comp['dorm']==d)]
    if len(m):
        r = m.iloc[0]; return r['precio_med'], r['ocup_med']
    e = extra[(barrio,d)]; return e['precio_med'], e['ocup_med']

S0 = dict(itbi=0.03, escritura=0.015, amoblado_por_m2=1_000, comision_airbnb=0.03,
          energia_base_mes=40, energia_por_noche=4.0, apreciacion=0.055,
          inflacion_costos=0.04, ajuste_tarifa=0.04, horizonte=10, costo_venta=0.06,
          mantenimiento_seguro=0.002)

def van(p, tarifa, noches_airbnb, tasa_desc, factor_otros_canales, gestion):
    noches = noches_airbnb * factor_otros_canales
    inv = p.precio*(1+S0['itbi']+S0['escritura']) + p.m2*S0['amoblado_por_m2']
    fc = [-inv]
    for t in range(1, S0['horizonte']+1):
        bruto = tarifa*noches*(1+S0['ajuste_tarifa'])**t
        energia = (S0['energia_base_mes']*12 + S0['energia_por_noche']*noches)*(1+S0['inflacion_costos'])**t
        fijos = (p.cond_mes*12+p.iptu)*(1+S0['inflacion_costos'])**t + energia + p.precio*S0['mantenimiento_seguro']
        n = bruto*(1-S0['comision_airbnb']-gestion) - fijos
        fc.append(n*(1-0.075) if n>0 else n)
    fc[-1] += p.precio*(1+S0['apreciacion'])**S0['horizonte']*(1-S0['costo_venta'])
    return sum(f/(1+tasa_desc)**i for i,f in enumerate(fc))

tasas = [0.05, 0.06, 0.0712, 0.08, 0.09]
ocup_factores = [0.7, 0.85, 1.0, 1.15, 1.3]   # % sobre la ocupación de mercado proyectada
gestiones = [0.0, 0.10, 0.20, 0.30]

# ---- 1) Matriz tasa x ocupación: VAN de la propiedad ganadora (W06.620) ----
p_win = props[props.ref=="W06.620"].iloc[0]
tar, ocu = tarifa_ocup(p_win.barrio, p_win.dorm)
M1 = pd.DataFrame(index=[f"{t*100:.2f}%" for t in tasas],
                   columns=[f"{round(f*100)}%" for f in ocup_factores])
for t in tasas:
    for f in ocup_factores:
        M1.loc[f"{t*100:.2f}%", f"{round(f*100)}%"] = round(van(p_win, tar, ocu, t, f*1.30, 0.20))
M1.index.name = "Tasa de descuento \\ Ocupación (% del proyectado)"
M1.to_csv('sens_van_ganadora_W06620.csv')
print("=== VAN de W06.620 (Ipanema, 4d) según tasa x ocupación ===")
print(M1.to_string())
print()

# ---- 2) Matriz tasa x ocupación: cantidad de propiedades con VAN positivo ----
M2 = pd.DataFrame(index=[f"{t*100:.2f}%" for t in tasas],
                   columns=[f"{round(f*100)}%" for f in ocup_factores])
detalle = {}
for t in tasas:
    for f in ocup_factores:
        positivas = []
        for p in props.itertuples():
            tar, ocu = tarifa_ocup(p.barrio, p.dorm)
            v = van(p, tar, ocu, t, f*1.30, 0.20)
            if v > 0:
                positivas.append(p.ref)
        M2.loc[f"{t*100:.2f}%", f"{round(f*100)}%"] = len(positivas)
        detalle[(round(t,4), f)] = positivas
M2.index.name = "Tasa de descuento \\ Ocupación (% del proyectado)"
M2.to_csv('sens_cantidad_viables.csv')
print("=== Cantidad de propiedades (de 12) con VAN positivo, según tasa x ocupación ===")
print(M2.to_string())
print()
json.dump({f"{t}|{f}": v for (t,f),v in detalle.items()}, open('sens_detalle_viables.json','w'), indent=1)

# ---- 3) Sensibilidad a la gestión (tasa y ocupación base) ----
rows = []
for p in props.itertuples():
    tar, ocu = tarifa_ocup(p.barrio, p.dorm)
    fila = {'ref': p.ref, 'barrio': p.barrio, 'dorm': p.dorm}
    for g in gestiones:
        fila[f"VAN_gestion_{int(g*100)}%"] = round(van(p, tar, ocu, 0.0712, 1.30, g))
    rows.append(fila)
M3 = pd.DataFrame(rows)
M3.to_csv('sens_gestion.csv', index=False)
print("=== VAN según % de gestión (0% = autogestión, 20% = base, 30% = agencia) ===")
pd.set_option('display.width',150)
print(M3.to_string(index=False))
