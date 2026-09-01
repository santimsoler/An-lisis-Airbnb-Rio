import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Sans'
NEGRO='#1a1a1a'; VERDE='#1e5c3a'; ROJO='#7a1f1f'; AZUL='#2a6f97'; GRIS='#888888'

res = pd.read_pickle('/home/claude/inversion/resultados_finales.pkl').sort_values('van_base', ascending=True)

# --- Gráfico 4: VAN por propiedad, escenario base ---
fig, ax = plt.subplots(figsize=(7.8,5))
etiquetas = [f"{r.ref}\n{r.barrio} · {int(r.dorm)}d" for r in res.itertuples()]
colores = [VERDE if v>0 else ROJO for v in res['van_base']]
valores_miles = res['van_base']/1000
bars = ax.barh(etiquetas, valores_miles, color=colores)
xmin, xmax = valores_miles.min(), valores_miles.max()
margen = (xmax - xmin) * 0.03
for b, v in zip(bars, valores_miles):
    ax.text(v + (margen if v>=0 else -margen), b.get_y()+b.get_height()/2, f'R$ {v:,.0f} mil',
            va='center', ha='left' if v>=0 else 'right', fontsize=8.5)
ax.axvline(0, color=NEGRO, linewidth=0.8)
ax.set_xlim(xmin*1.25, xmax*1.32)
ax.set_xlabel('VAN a 10 años (miles de R$)')
ax.set_title('VAN por propiedad — escenario esperado (tasa 7,12%, ocupación típica del barrio)', fontsize=10.5)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('g4_van_por_propiedad.png', dpi=150)
plt.close()

# --- Gráfico 5: heatmap cantidad viables tasa x ocupación ---
m2 = pd.read_csv('/home/claude/inversion/sens_cantidad_viables.csv', index_col=0)
fig, ax = plt.subplots(figsize=(6.5,4))
im = ax.imshow(m2.values.astype(float), cmap='RdYlGn', vmin=0, vmax=8, aspect='auto')
ax.set_xticks(range(len(m2.columns))); ax.set_xticklabels(m2.columns)
ax.set_yticks(range(len(m2.index))); ax.set_yticklabels(m2.index)
ax.set_xlabel('Ocupación (% de la proyectada)'); ax.set_ylabel('Tasa de descuento')
ax.set_title('Cantidad de propiedades (de 12) con VAN positivo', fontsize=11)
for i in range(len(m2.index)):
    for j in range(len(m2.columns)):
        v = m2.values[i,j]
        ax.text(j, i, str(v), ha='center', va='center', fontsize=10,
                color='white' if v<2 or v>6 else 'black', fontweight='bold')
plt.colorbar(im, ax=ax, label='Propiedades viables')
plt.tight_layout()
plt.savefig('g5_heatmap_tasa_ocupacion.png', dpi=150)
plt.close()

# --- Gráfico 6: heatmap cantidad viables tasa x descuento de compra ---
m3 = pd.read_csv('/home/claude/inversion/sens_descuento_cantidad.csv', index_col=0)
fig, ax = plt.subplots(figsize=(6.5,4))
im = ax.imshow(m3.values.astype(float), cmap='RdYlGn', vmin=0, vmax=8, aspect='auto')
ax.set_xticks(range(len(m3.columns))); ax.set_xticklabels(m3.columns)
ax.set_yticks(range(len(m3.index))); ax.set_yticklabels(m3.index)
ax.set_xlabel('Rebaja sobre el precio de lista'); ax.set_ylabel('Tasa de descuento')
ax.set_title('Cantidad de propiedades (de 12) con VAN positivo', fontsize=11)
for i in range(len(m3.index)):
    for j in range(len(m3.columns)):
        v = m3.values[i,j]
        ax.text(j, i, str(v), ha='center', va='center', fontsize=10,
                color='white' if v<2 or v>6 else 'black', fontweight='bold')
plt.colorbar(im, ax=ax, label='Propiedades viables')
plt.tight_layout()
plt.savefig('g6_heatmap_tasa_descuento.png', dpi=150)
plt.close()

# --- Gráfico 7: flujo DESCONTADO acumulado a 10 años (coincide con el VAN reportado) ---
det = pd.read_csv('/home/claude/inversion/flujo_detallado_10_anios.csv')
det = det.sort_values(['ref','anio'])
det['flujo_descontado_acum'] = det.groupby('ref')['flujo_descontado'].cumsum()
fig, ax = plt.subplots(figsize=(7.5,4.3))
for ref, grp in det.groupby('ref'):
    color = VERDE if ref == 'W06.620' else '#cccccc'
    lw = 2.5 if ref == 'W06.620' else 1
    zorder = 5 if ref == 'W06.620' else 1
    ax.plot(grp['anio'], grp['flujo_descontado_acum']/1000, color=color, linewidth=lw, zorder=zorder)
ax.axhline(0, color=NEGRO, linewidth=0.8, linestyle=':')
ax.set_xlabel('Año'); ax.set_ylabel('Flujo descontado acumulado (miles de R$)')
ax.set_title('Flujo de fondos descontado, acumulado a 10 años — las 12 propiedades\n'
            '(el valor del año 10 es el VAN de cada propiedad; en verde, la única que termina positiva)', fontsize=10)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('g7_flujo_acumulado_10anios.png', dpi=150)
plt.close()

print("Gráficos de Parte 2 generados")
