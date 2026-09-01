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
], columns=["ref","barrio","m2","dorm","precio_lista","cond_mes","iptu"])

comp = pd.read_pickle('/home/claude/work/comparables.pkl').rename(columns={'neighbourhood_cleansed':'barrio'})
comp['dorm'] = comp['dorm'].astype(int)
extra = {("Gávea",3): dict(precio_med=958.0, ocup_med=24.0),
         ("Flamengo",4): dict(precio_med=642.0, ocup_med=36.0)}
def tarifa_ocup(barrio, dorm):
    d = min(dorm,4)
    m = comp[(comp['barrio']==barrio)&(comp['dorm']==d)]
    if len(m):
        r = m.iloc[0]; return r['precio_med'], r['ocup_med']
    e = extra[(barrio,d)]; return e['precio_med'], e['ocup_med']

S0 = dict(itbi=0.03, escritura=0.015, amoblado_por_m2=1_000, comision_airbnb=0.03,
          energia_base_mes=40, energia_por_noche=4.0, apreciacion=0.055,
          inflacion_costos=0.04, ajuste_tarifa=0.04, horizonte=10, costo_venta=0.06,
          mantenimiento_seguro=0.002, gestion_base=0.20, ir=0.075)

def van(p, tarifa, noches_airbnb, tasa_desc, descuento, gestion=S0['gestion_base'], factor_otros=1.30):
    precio_compra = p.precio_lista * (1 - descuento)
    noches = noches_airbnb * factor_otros
    inv = precio_compra*(1+S0['itbi']+S0['escritura']) + p.m2*S0['amoblado_por_m2']
    fc = [-inv]
    for t in range(1, S0['horizonte']+1):
        bruto = tarifa*noches*(1+S0['ajuste_tarifa'])**t
        energia = (S0['energia_base_mes']*12 + S0['energia_por_noche']*noches)*(1+S0['inflacion_costos'])**t
        fijos = (p.cond_mes*12+p.iptu)*(1+S0['inflacion_costos'])**t + energia + precio_compra*S0['mantenimiento_seguro']
        n = bruto*(1-S0['comision_airbnb']-gestion) - fijos
        fc.append(n*(1-S0['ir']) if n>0 else n)
    fc[-1] += precio_compra*(1+S0['apreciacion'])**S0['horizonte']*(1-S0['costo_venta'])
    return sum(f/(1+tasa_desc)**i for i,f in enumerate(fc))

descuentos = [0.0, 0.05, 0.10, 0.15, 0.20]
tasas = [0.05, 0.06, 0.0712, 0.08, 0.09]

# ---- 1) VAN por propiedad según descuento de compra (tasa y ocupación base) ----
rows = []
for p in props.itertuples():
    tar, ocu = tarifa_ocup(p.barrio, p.dorm)
    fila = {'ref': p.ref, 'barrio': p.barrio, 'dorm': p.dorm}
    for d in descuentos:
        fila[f"VAN_desc_{int(d*100)}"] = round(van(p, tar, ocu, 0.0712, d))
    rows.append(fila)
M1 = pd.DataFrame(rows)
M1.to_csv('sens_descuento_van.csv', index=False)
pd.set_option('display.width',160)
print("=== VAN según descuento de compra (0-20%), tasa y ocupación base ===")
print(M1.to_string(index=False))
print()

# ---- 2) Cantidad de propiedades viables: descuento x tasa (ocupación base 100%) ----
M2 = pd.DataFrame(index=[f"{t*100:.2f}%" for t in tasas],
                   columns=[f"{int(d*100)}%" for d in descuentos])
for t in tasas:
    for d in descuentos:
        cnt = 0
        for p in props.itertuples():
            tar, ocu = tarifa_ocup(p.barrio, p.dorm)
            if van(p, tar, ocu, t, d) > 0:
                cnt += 1
        M2.loc[f"{t*100:.2f}%", f"{int(d*100)}%"] = cnt
M2.index.name = "Tasa de descuento \\ Rebaja sobre el precio de lista"
M2.to_csv('sens_descuento_cantidad.csv')
print("=== Cantidad de propiedades (de 12) con VAN positivo, según tasa x descuento de compra ===")
print(M2.to_string())
