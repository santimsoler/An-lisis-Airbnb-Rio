import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                ListFlowable, ListItem, PageBreak, Image, KeepTogether)

R = '/home/claude/inversion'

props_info = pd.DataFrame([
 ("W05.102","Copacabana", 78,2,3,1_150_000,1_100, 2_360,0,""),
 ("W06.914","Copacabana",170,3,5,1_600_000,2_740, 3_475,0,"Unidad independiente, entrada privada"),
 ("W06.931","Copacabana",149,3,4,1_700_000,3_280, 5_862,1,"Ficha 149 m2 / descripción 155 m2; sin dato de baños en ficha"),
 ("W06.935","Ipanema",    70,2,2,1_650_000,1_147, 2_370,0,"Recepción 24h"),
 ("W06.922","Ipanema",    88,1,1,1_950_000,2_400, 7_113,1,""),
 ("W06.924","Lagoa",      63,1,1,1_520_000,1_292, 3_607,1,""),
 ("W06.481","Gávea",     118,3,2,2_100_000,2_143, 5_129,1,"Edificio de 1957; comparables escasos (n=8)"),
 ("W06.936","Lagoa",      96,3,2,2_550_000,1_700, 6_445,0,"Seguridad 24h"),
 ("W06.947","Leblon",     85,2,1,2_100_000,  862, 5_952,0,"Sin ascensor, sin garaje"),
 ("W06.345","Leblon",     99,3,2,2_100_000,1_200, 4_828,0,"Rua Dias Ferreira, sin garaje"),
 ("W06.620","Ipanema",   138,4,2,2_945_000,2_199, 9_130,2,"Reformado"),
 ("W06.725","Flamengo",  290,4,2,3_220_000,2_689,14_387,1,"Vista al mar; comparables escasos (n=4)"),
], columns=["ref","barrio","m2","dorm","banos","precio","cond_mes","iptu","garaje","notas"])

res = pd.read_pickle(f'{R}/resultados_finales.pkl').sort_values('van_base', ascending=False).reset_index(drop=True)
det = pd.read_csv(f'{R}/flujo_detallado_10_anios.csv')
det = det.sort_values(['ref','anio'])
det['flujo_descontado_acum'] = det.groupby('ref')['flujo_descontado'].cumsum()

doc = SimpleDocTemplate("/home/claude/repo_final/inversion_inmobiliaria/informes/2_anexo_datos_detallado.pdf",
                        pagesize=letter, topMargin=1.8*cm, bottomMargin=1.8*cm, leftMargin=2*cm, rightMargin=2*cm)

s = getSampleStyleSheet()
NEGRO = colors.HexColor('#1a1a1a'); GRIS = colors.HexColor('#666666')
VERDE = colors.HexColor('#1e5c3a'); ROJO = colors.HexColor('#7a1f1f')
FONDO_VERDE = colors.HexColor('#eaf4ee'); FONDO_ROJO = colors.HexColor('#f7eaea')

name_style = ParagraphStyle('name', parent=s['Normal'], fontSize=12, alignment=TA_CENTER, textColor=GRIS, spaceAfter=4)
title_style = ParagraphStyle('title', parent=s['Title'], fontSize=17, leading=21, spaceAfter=4, textColor=NEGRO)
sub_style = ParagraphStyle('sub', parent=s['Normal'], fontSize=10.5, alignment=TA_CENTER, textColor=GRIS, spaceAfter=16)
h1 = ParagraphStyle('h1', parent=s['Heading1'], fontSize=14, spaceBefore=14, spaceAfter=8, textColor=NEGRO)
h2 = ParagraphStyle('h2', parent=s['Heading2'], fontSize=11.5, spaceBefore=10, spaceAfter=6, textColor=NEGRO)
h3 = ParagraphStyle('h3', parent=s['Heading3'], fontSize=10.5, spaceBefore=10, spaceAfter=5, textColor=NEGRO)
body = ParagraphStyle('body', parent=s['Normal'], fontSize=9.6, leading=13.8, spaceAfter=7, alignment=TA_JUSTIFY)
nota = ParagraphStyle('nota', parent=s['Normal'], fontSize=8.2, leading=11.5, textColor=GRIS, spaceAfter=6)
ficha_val = ParagraphStyle('fv', parent=s['Normal'], fontSize=8.3, leading=10.8)

st = []

# PORTADA
st.append(Spacer(1, 15))
st.append(Paragraph("Pablo Santiago Martínez Soler", name_style))
st.append(Paragraph("Anexo de datos: detalle completo", title_style))
st.append(Paragraph("Informe 2 de 2 — Acompaña al Informe 1 (resumen ejecutivo).<br/>"
                    "Flujo de fondos año a año, matrices de sensibilidad completas y ficha técnica.", sub_style))
st.append(Paragraph(
    "Este documento contiene el respaldo completo de datos del Informe 1: el flujo de fondos proyectado "
    "año por año para cada una de las 12 propiedades evaluadas, las cuatro matrices de sensibilidad "
    "completas (tasa de descuento, ocupación, costo de gestión y precio de compra), y la ficha técnica "
    "con la metodología de ambas partes del análisis. Ningún número de este documento fue estimado "
    "aparte — todos surgen de los mismos scripts que generaron el Informe 1.", body))

# =========================================================================
# FLUJO DE FONDOS DETALLADO POR PROPIEDAD
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("1. Flujo de fondos proyectado, año a año — las 12 propiedades", h1))
st.append(Paragraph(
    "Para cada propiedad: ingreso bruto proyectado, gastos fijos (expensas, IPTU, energía, mantenimiento "
    "y seguro), resultado antes de impuesto a la renta, flujo neto (después de 7,5% de impuesto a la "
    "renta cuando el resultado es positivo), flujo descontado a la tasa de 7,12% anual, y flujo "
    "descontado acumulado. El año 0 es la inversión inicial; el año 10 incluye el valor de reventa "
    "proyectado del inmueble. El flujo descontado acumulado del año 10 es el VAN de la propiedad.", body))

col_widths = [1.1*cm, 2.3*cm, 2.3*cm, 2.7*cm, 2.3*cm, 2.5*cm, 2.7*cm]
header = ["Año", "Ingreso\nbruto (R$)", "Gastos\nfijos (R$)", "Resultado\nantes IR (R$)",
          "Flujo\nneto (R$)", "Flujo\ndescontado (R$)", "Acumulado\ndescontado (R$)"]

for _, prop in res.iterrows():
    ref = prop['ref']
    info = props_info[props_info.ref == ref].iloc[0]
    grp = det[det.ref == ref].sort_values('anio')

    titulo = (f"Ref. {ref} — {info['barrio']}, {int(info['dorm'])} dormitorios, {info['m2']} m<super>2</super> — "
             f"R$ {info['precio']:,.0f}")
    van_txt = f"VAN a 10 años: R$ {prop['van_base']:,.0f}  |  TIR: {prop['tir_base']*100:.2f}%  |  Cap rate año 1: {prop['cap_base']*100:.2f}%"

    data = [header]
    for _, row in grp.iterrows():
        if row['anio'] == 0:
            data.append(["0", "—", "—", "—", f"{row['flujo_neto']:,.0f}", f"{row['flujo_descontado']:,.0f}",
                        f"{row['flujo_descontado_acum']:,.0f}"])
        else:
            data.append([str(int(row['anio'])), f"{row['bruto']:,.0f}", f"{row['fijos']:,.0f}",
                        f"{row['resultado_antes_ir']:,.0f}", f"{row['flujo_neto']:,.0f}",
                        f"{row['flujo_descontado']:,.0f}", f"{row['flujo_descontado_acum']:,.0f}"])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    tstyle = [
        ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 7.6),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')), ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3.2), ('BOTTOMPADDING', (0,0), (-1,-1), 3.2),
    ]
    ultimo_valor = grp[grp.anio==10]['flujo_descontado_acum'].values[0]
    color_final = FONDO_VERDE if ultimo_valor > 0 else FONDO_ROJO
    tstyle.append(('BACKGROUND', (-1,-1), (-1,-1), color_final))
    tstyle.append(('FONTNAME', (-1,-1), (-1,-1), 'Helvetica-Bold'))
    t.setStyle(TableStyle(tstyle))

    color_van = VERDE if prop['van_base'] > 0 else ROJO
    bloque = [
        Paragraph(titulo, h3),
        Paragraph(van_txt, ParagraphStyle('vt', parent=nota, textColor=color_van, fontSize=9, spaceAfter=5)),
        t,
        Spacer(1, 10),
    ]
    if info['notas']:
        bloque.insert(2, Paragraph(f"<i>{info['notas']}</i>", nota))
    st.append(KeepTogether(bloque))

# =========================================================================
# SENSIBILIDAD COMPLETA
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("2. Matrices de sensibilidad completas", h1))

st.append(Paragraph("2.1 — Cantidad de propiedades viables, tasa de descuento x ocupación", h2))
m1 = pd.read_csv(f'{R}/sens_cantidad_viables.csv', index_col=0)
data1 = [["Tasa \\ Ocupación"] + list(m1.columns)]
for idx, row in m1.iterrows():
    data1.append([idx] + [str(v) for v in row.values])
t1 = Table(data1, colWidths=[3.2*cm]+[2.1*cm]*5)
t1.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'), ('BACKGROUND', (3,3), (3,3), FONDO_VERDE),
]))
st.append(t1)
st.append(Spacer(1, 12))

st.append(Paragraph("2.2 — VAN de la propiedad recomendada (Ref. W06.620), tasa x ocupación", h2))
m2 = pd.read_csv(f'{R}/sens_van_ganadora_W06620.csv', index_col=0)
data2 = [["Tasa \\ Ocupación"] + list(m2.columns)]
for idx, row in m2.iterrows():
    data2.append([idx] + [f"{v:,.0f}" for v in row.values])
t2 = Table(data2, colWidths=[3.2*cm]+[2.35*cm]*5)
t2style = [
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.3),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
]
for i in range(1, len(data2)):
    for j in range(1, len(data2[0])):
        val = float(data2[i][j].replace(',',''))
        t2style.append(('BACKGROUND', (j,i), (j,i), FONDO_VERDE if val>0 else FONDO_ROJO))
t2.setStyle(TableStyle(t2style))
st.append(t2)
st.append(Spacer(1, 12))

st.append(Paragraph("2.3 — VAN de las 12 propiedades según costo de gestión", h2))
m3 = pd.read_csv(f'{R}/sens_gestion.csv').sort_values('VAN_gestion_20%', ascending=False)
data3 = [["Ref.", "Barrio", "VAN (0%\nautogestión)", "VAN (20%\nbase)", "VAN (30%\nagencia)"]]
for _, r in m3.iterrows():
    data3.append([r['ref'], r['barrio'], f"{r['VAN_gestion_0%']:,.0f}",
                 f"{r['VAN_gestion_20%']:,.0f}", f"{r['VAN_gestion_30%']:,.0f}"])
t3 = Table(data3, colWidths=[2*cm, 2.8*cm, 3.2*cm, 2.8*cm, 3*cm], repeatRows=1)
t3style = [
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.6),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 4.5), ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
]
for i in range(1, len(data3)):
    for j in [2,3,4]:
        val = float(data3[i][j].replace(',',''))
        t3style.append(('BACKGROUND', (j,i), (j,i), FONDO_VERDE if val>0 else FONDO_ROJO))
t3.setStyle(TableStyle(t3style))
st.append(t3)

st.append(PageBreak())
st.append(Paragraph("2.4 — VAN de las 12 propiedades según rebaja sobre el precio de lista", h2))
m4 = pd.read_csv(f'{R}/sens_descuento_van.csv').sort_values('VAN_desc_0', ascending=False)
data4 = [["Ref.", "Barrio", "0%\n(lista)", "5%", "10%", "15%", "20%"]]
for _, r in m4.iterrows():
    data4.append([r['ref'], r['barrio'], f"{r['VAN_desc_0']:,.0f}", f"{r['VAN_desc_5']:,.0f}",
                 f"{r['VAN_desc_10']:,.0f}", f"{r['VAN_desc_15']:,.0f}", f"{r['VAN_desc_20']:,.0f}"])
t4 = Table(data4, colWidths=[1.9*cm, 2.4*cm, 2.3*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.1*cm], repeatRows=1)
t4style = [
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.1),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 4.5), ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
]
for i in range(1, len(data4)):
    for j in range(2,7):
        val = float(data4[i][j].replace(',',''))
        t4style.append(('BACKGROUND', (j,i), (j,i), FONDO_VERDE if val>0 else FONDO_ROJO))
t4.setStyle(TableStyle(t4style))
st.append(t4)
st.append(Spacer(1, 12))

st.append(Paragraph("2.5 — Cantidad de propiedades viables, tasa de descuento x rebaja de compra", h2))
m5 = pd.read_csv(f'{R}/sens_descuento_cantidad.csv', index_col=0)
data5 = [["Tasa \\ Rebaja"] + list(m5.columns)]
for idx, row in m5.iterrows():
    data5.append([idx] + [str(v) for v in row.values])
t5 = Table(data5, colWidths=[3.2*cm]+[2.1*cm]*5)
t5.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
]))
st.append(t5)

# =========================================================================
# FICHA TÉCNICA
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("3. Ficha técnica", h1))

st.append(Paragraph("3.1 — Parte 1: Modelo de precios", h2))
st.append(Paragraph(
    "<b>Fuente:</b> Inside Airbnb, listings de Río de Janeiro. 44.542 publicaciones con precio válido; "
    "tras tratamiento de outliers (percentil 99 combinado de precio y precio por persona) y filtros de "
    "coherencia interna, 43.395 observaciones finales.", body))
st.append(Paragraph(
    "<b>Variables utilizadas:</b> tamaño y capacidad (dormitorios, baños, huéspedes), ubicación "
    "(latitud, longitud, distancia a Copacabana, cluster geográfico por K-Means), tipo de propiedad y "
    "habitación, antigüedad y reputación del anfitrión, disponibilidad de calendario, reseñas, y texto "
    "de la descripción (TF-IDF, 50 términos). Se excluyeron variables con fuga de información.", body))
st.append(Paragraph(
    "<b>Modelos comparados:</b> regresión lineal (MCO), LASSO, regresión sobre logaritmo del precio, "
    "Random Forest y Gradient Boosting (histogramas). Evaluados sobre 20% de datos de prueba. Ganador: "
    "Gradient Boosting, RMSE R$ 481, MAE R$ 252, R<super>2</super> 0,6252.", body))
st.append(Paragraph(
    "<b>Importancia de variables:</b> calculada por permutación. Prueba adicional de especificación: "
    "el modelo sin `dist_km_copacabana` obtiene RMSE 480,12 (mejor que con la variable, 481,42) — se "
    "conserva por interpretabilidad, no por aporte a la precisión.", body))

st.append(Paragraph("3.2 — Parte 2: Supuestos del flujo de fondos", h2))
sup_data = [
    ["Concepto", "Valor"],
    ["Horizonte de proyección", "10 años"],
    ["Tasa de descuento (VAN)", "7,12% real anual — Tesouro IPCA+ (tasa libre de riesgo Brasil, sin prima de riesgo adicional)"],
    ["ITBI (impuesto de transferencia)", "3,0% sobre el precio de compra"],
    ["Escritura y registro", "1,5% sobre el precio de compra"],
    ["Amoblado / puesta a punto", "R$ 1.000 por m<super>2</super>"],
    ["Comisión de la plataforma (Airbnb)", "3,0% del ingreso bruto"],
    ["Administración / gestión", "20% del ingreso bruto (escenario base; sensibilizado 0%-30%)"],
    ["Mantenimiento y seguro", "0,2% anual sobre el valor del inmueble"],
    ["Energía eléctrica", "R$ 40/mes fijo + R$ 4 por noche ocupada"],
    ["Ocupación adicional por otros canales", "+30% sobre las noches estimadas vía Airbnb"],
    ["Impuesto a la renta", "7,5% sobre el resultado neto (promedio de escalas brasileñas)"],
    ["Ajuste anual de tarifa", "4,0% nominal"],
    ["Inflación de costos fijos", "4,0% anual"],
    ["Revalorización del inmueble", "5,5% nominal anual — histórico de Río de Janeiro en los últimos 20 años (dato del autor)"],
    ["Costo de venta al final del horizonte", "6,0% (comisión inmobiliaria + gastos)"],
    ["Condominio e IPTU", "Valor real informado en cada ficha de la propiedad"],
]
sup_data = [sup_data[0]] + [[row[0], Paragraph(row[1], ficha_val)] for row in sup_data[1:]]
ts = Table(sup_data, colWidths=[5.8*cm, 10.4*cm])
ts.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.6),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 4.5), ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
    ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
]))
st.append(ts)
st.append(Spacer(1, 10))

st.append(Paragraph("3.3 — Características de las 12 propiedades evaluadas", h2))
data_props = [["Ref.", "Barrio", "m²", "Dorm.", "Baños", "Precio (R$)", "Cond./mes (R$)", "IPTU/año (R$)"]]
for p in props_info.itertuples():
    data_props.append([p.ref, p.barrio, str(p.m2), str(p.dorm), str(p.banos),
                       f"{p.precio:,.0f}", f"{p.cond_mes:,.0f}", f"{p.iptu:,.0f}"])
tp = Table(data_props, colWidths=[1.8*cm, 2.3*cm, 1.3*cm, 1.4*cm, 1.4*cm, 2.7*cm, 2.7*cm, 2.5*cm])
tp.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8.4),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 4.5), ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
]))
st.append(tp)
st.append(Spacer(1, 10))

st.append(Paragraph("3.4 — Limitaciones a tener en cuenta", h2))
limitaciones = [
    "No se modeló financiamiento: el cálculo asume compra de contado.",
    "No se modeló riesgo cambiario. Todo el análisis está en reales.",
    "Ref. W06.481 (Gávea) y Ref. W06.725 (Flamengo) tienen muy pocos comparables directos en los datos "
    "(8 y 4 publicaciones respectivamente), así que sus proyecciones son menos confiables que las del resto.",
    "El impuesto a la renta de 7,5% es un promedio general; el régimen efectivo puede variar y debería "
    "confirmarse con un contador en Brasil.",
    "La revalorización de 5,5% anual es un promedio histórico de 20 años; no garantiza el desempeño futuro.",
    "La tasa de descuento usada es la tasa libre de riesgo pura, sin prima por el riesgo específico de "
    "la inversión inmobiliaria/turística.",
    "La distancia a Copacabana no mejoró la capacidad predictiva del modelo de precios por encima de "
    "lo que ya aportan latitud y longitud (Parte 1); se mantuvo por su valor interpretativo.",
]
st.append(ListFlowable([ListItem(Paragraph(l, nota), bulletColor=GRIS) for l in limitaciones],
                       bulletType='bullet', leftIndent=13))

doc.build(st)
print("Informe 2 generado")
