import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams['font.family'] = 'DejaVu Sans'
NEGRO='#1a1a1a'; VERDE='#1e5c3a'; ROJO='#7a1f1f'; AZUL='#2a6f97'; GRIS='#888888'

df = pd.read_pickle('/home/claude/work/step6_v2.pkl')

# --- Gráfico 1: distribución de precios ---
fig, ax = plt.subplots(figsize=(7.5,4))
ax.hist(df['price'], bins=80, range=(0,3000), color=AZUL, edgecolor='white', linewidth=0.3)
media, mediana = df['price'].mean(), df['price'].median()
ax.axvline(media, color=ROJO, linestyle='--', linewidth=1.5, label=f'Promedio: R$ {media:,.0f}')
ax.axvline(mediana, color=VERDE, linestyle='-', linewidth=1.5, label=f'Mediana: R$ {mediana:,.0f}')
ax.set_xlabel('Precio por noche (R$)'); ax.set_ylabel('Cantidad de publicaciones')
ax.set_title('Distribución del precio — 43.395 publicaciones de Airbnb en Río de Janeiro', fontsize=11)
ax.legend(frameon=False)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('g1_distribucion_precio.png', dpi=150)
plt.close()

# --- Gráfico 2: comparación de modelos ---
modelos = ['MCO','LASSO','Regresión\nlog-precio','Random\nForest','Gradient\nBoosting']
rmse = [576.29, 578.73, 608.19, 518.26, 481.42]
colores = [GRIS, GRIS, GRIS, '#5a8fb0', VERDE]
fig, ax = plt.subplots(figsize=(7.2,4))
bars = ax.bar(modelos, rmse, color=colores, width=0.6)
for b, v in zip(bars, rmse):
    ax.text(b.get_x()+b.get_width()/2, v+8, f'{v:.0f}', ha='center', fontsize=9.5, fontweight='bold')
ax.set_ylabel('Error típico de predicción (RMSE, en R$)')
ax.set_title('Comparación de modelos — menor error es mejor', fontsize=11)
ax.set_ylim(0, 680)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('g2_comparacion_modelos.png', dpi=150)
plt.close()

# --- Gráfico 3: importancia de variables ---
vars_imp = pd.Series({
    'bedrooms': 110.948788, 'bathrooms': 60.127451, 'accommodates': 53.067341,
    'latitude': 42.240684, 'availability_365': 15.507174, 'availability_90': 15.359761,
    'dist_km_copacabana': 14.414868, 'texto_tfidf (50 vars.)': 12.658269,
    'room_type': 11.875686, 'maximum_minimum_nights': 8.931536,
}).sort_values()
etiquetas = {'bedrooms':'Dormitorios','bathrooms':'Baños','accommodates':'Capacidad (huéspedes)',
             'latitude':'Latitud','availability_365':'Disponibilidad (365d)',
             'availability_90':'Disponibilidad (90d)','dist_km_copacabana':'Distancia a Copacabana',
             'texto_tfidf (50 vars.)':'Texto de la descripción','room_type':'Tipo de habitación',
             'maximum_minimum_nights':'Estadía mínima permitida'}
vars_imp.index = [etiquetas[i] for i in vars_imp.index]
fig, ax = plt.subplots(figsize=(7.5,4.3))
colores_b = [VERDE if v>50 else AZUL if v>20 else '#8ab4c8' for v in vars_imp.values]
ax.barh(vars_imp.index, vars_imp.values, color=colores_b)
ax.set_xlabel('Aumento del error del modelo al anular la variable (importancia)')
ax.set_title('Qué pesa más en el precio de un Airbnb en Río de Janeiro', fontsize=11)
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig('g3_importancia_variables.png', dpi=150)
plt.close()

print("Gráficos de Parte 1 generados")
