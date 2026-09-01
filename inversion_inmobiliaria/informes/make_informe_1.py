import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                ListFlowable, ListItem, PageBreak, Image)

G = '/home/claude/repo_final/inversion_inmobiliaria/graficos'
R = '/home/claude/inversion'

res = pd.read_pickle(f'{R}/resultados_finales.pkl').sort_values('van_base', ascending=False).reset_index(drop=True)

doc = SimpleDocTemplate("/home/claude/repo_final/inversion_inmobiliaria/informes/1_informe_ejecutivo.pdf",
                        pagesize=letter, topMargin=1.8*cm, bottomMargin=1.8*cm, leftMargin=2.2*cm, rightMargin=2.2*cm)

s = getSampleStyleSheet()
NEGRO = colors.HexColor('#1a1a1a'); GRIS = colors.HexColor('#666666')
VERDE = colors.HexColor('#1e5c3a'); ROJO = colors.HexColor('#7a1f1f'); AZUL = colors.HexColor('#1e3f5c')
FONDO_VERDE = colors.HexColor('#eaf4ee'); FONDO_ROJO = colors.HexColor('#f7eaea'); FONDO_AZUL = colors.HexColor('#eaf1f7')

name_style = ParagraphStyle('name', parent=s['Normal'], fontSize=12, alignment=TA_CENTER, textColor=GRIS, spaceAfter=4)
title_style = ParagraphStyle('title', parent=s['Title'], fontSize=18, leading=22, spaceAfter=4, textColor=NEGRO)
sub_style = ParagraphStyle('sub', parent=s['Normal'], fontSize=10.5, alignment=TA_CENTER, textColor=GRIS, spaceAfter=16)
parte_style = ParagraphStyle('parte', parent=s['Normal'], fontSize=10.5, alignment=TA_CENTER, textColor=colors.white,
                             backColor=NEGRO, borderPadding=8, spaceAfter=16, spaceBefore=6)
h1 = ParagraphStyle('h1', parent=s['Heading1'], fontSize=14.5, spaceBefore=16, spaceAfter=9, textColor=NEGRO)
h2 = ParagraphStyle('h2', parent=s['Heading2'], fontSize=12, spaceBefore=13, spaceAfter=7, textColor=NEGRO)
body = ParagraphStyle('body', parent=s['Normal'], fontSize=10, leading=14.8, spaceAfter=8, alignment=TA_JUSTIFY)
bullet = ParagraphStyle('bullet', parent=body, spaceAfter=6)
nota = ParagraphStyle('nota', parent=s['Normal'], fontSize=8.4, leading=12, textColor=GRIS, spaceAfter=6)
caption = ParagraphStyle('cap', parent=s['Normal'], fontSize=8.6, leading=11, textColor=GRIS, alignment=TA_CENTER, spaceAfter=12, spaceBefore=2)
destacado_rojo = ParagraphStyle('dr', parent=body, fontSize=10.3, textColor=ROJO, backColor=FONDO_ROJO, borderPadding=9, spaceAfter=11)
destacado_azul = ParagraphStyle('da', parent=body, fontSize=10, textColor=AZUL, backColor=FONDO_AZUL, borderPadding=9, spaceAfter=11)

def img(path, width_cm, caption_text=None):
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    ratio = h/w
    im = Image(path, width=width_cm*cm, height=width_cm*cm*ratio)
    out = [im]
    if caption_text:
        out.append(Paragraph(caption_text, caption))
    return out

st = []

# PORTADA
st.append(Spacer(1, 15))
st.append(Paragraph("Pablo Santiago Martínez Soler", name_style))
st.append(Paragraph("Qué determina el precio de un Airbnb en Río de Janeiro,<br/>"
                    "y qué propiedades conviene comprar hoy", title_style))
st.append(Paragraph("Informe 1 de 2 — Resumen ejecutivo, con gráficos. "
                    "El detalle completo de datos y tablas está en el Informe 2 (anexo).", sub_style))
st.append(Paragraph(
    "Este informe tiene dos partes. La primera analiza más de 43.000 publicaciones reales de Airbnb en "
    "Río de Janeiro para entender qué hace que un alojamiento valga más o menos. La segunda toma esa "
    "base de conocimiento —los precios y la ocupación reales del mercado, no estimaciones— y la usa para "
    "evaluar si conviene comprar cada una de 12 propiedades concretas que están hoy en venta.", body))

# =========================================================================
# PARTE 1
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("PARTE 1", parte_style))
st.append(Paragraph("Qué determina el precio de un Airbnb en Río de Janeiro", h1))

st.append(Paragraph("El punto de partida: los datos", h2))
st.append(Paragraph(
    "Se analizaron 43.395 publicaciones activas de Airbnb en Río de Janeiro, con datos públicos del "
    "relevamiento independiente Inside Airbnb. Cada publicación trae más de 90 datos: precio, ubicación "
    "exacta, tamaño, cantidad de dormitorios y baños, tipo de anfitrión, calendario de disponibilidad, "
    "reseñas de huéspedes y el texto completo de la descripción.", body))

st.extend(img(f'{G}/g1_distribucion_precio.png', 14,
    "El alojamiento promedio cuesta R$ 673 por noche, pero la mitad cuesta menos de R$ 449 — "
    "una franja chica de alojamientos de lujo estira el promedio hacia arriba."))

st.append(Paragraph(
    "Copacabana concentra casi un tercio de toda la oferta relevada (13.555 publicaciones), seguida por "
    "Ipanema (3.492). El 82% de los alojamientos son \"casa/apartamento entero\" —la modalidad relevante "
    "para este análisis— y el 67% tiene un solo dormitorio.", body))

st.append(Paragraph("Se probaron varios modelos, no uno solo", h2))
st.append(Paragraph(
    "Para estimar qué explica el precio, no alcanza con mirar promedios: hay que aislar el efecto de "
    "cada característica controlando por las demás. Se entrenaron y compararon cinco modelos, de menor "
    "a mayor complejidad.", body))

st.extend(img(f'{G}/g2_comparacion_modelos.png', 13.5,
    "Gradient Boosting fue el modelo con menor error: se equivoca en promedio R$ 481 por noche, "
    "y explica el 63% de la variación del precio (R<super>2</super>=0,63)."))

st.append(Paragraph(
    "Superó claramente a los modelos lineales, lo que indica que el precio no depende de una simple "
    "suma de características: hay combinaciones que valen más juntas que separadas (tamaño grande y "
    "buena ubicación se potencian entre sí, más de lo que cada uno aporta por separado).", body))

st.append(Paragraph("Qué es lo que más pesa en el precio", h2))
st.extend(img(f'{G}/g3_importancia_variables.png', 14,
    "El tamaño (dormitorios, baños, capacidad) pesa más del doble que cualquier otro factor. "
    "La distancia a Copacabana entra en el modelo pero, en una prueba de especificación, no mejoró "
    "la precisión por encima de lo que ya aporta la latitud — se mantiene por valor interpretativo."))

st.append(Paragraph(
    "Esta Parte 1 responde \"qué determina el precio de un Airbnb\" en general, para el mercado de Río "
    "de Janeiro completo. La Parte 2 usa esa misma base de datos —ahora enfocada en las tarifas y la "
    "ocupación real de cada barrio— para responder una pregunta distinta y más concreta: si alguien "
    "compra una de estas 12 propiedades puntuales, ¿le conviene?", destacado_azul))

# =========================================================================
# PARTE 2
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("PARTE 2", parte_style))
st.append(Paragraph("Rentabilidad de comprar: 12 propiedades evaluadas", h1))

st.append(Paragraph(
    "Se evaluaron 12 apartamentos en oferta en Copacabana, Ipanema, Leblon, Lagoa, Gávea y Flamengo. "
    "Para cada uno se proyectó el ingreso esperado con las tarifas y la ocupación reales del mercado de "
    "su barrio y su tamaño —las mismas que sustentan el modelo de la Parte 1—, se descontaron todos los "
    "costos, y se calculó si el proyecto genera valor a 10 años frente a la alternativa de no arriesgar "
    "el dinero (invertirlo a la tasa libre de riesgo de Brasil, 7,12% real anual).", body))

st.append(Paragraph(
    "<b>De las 12 propiedades, una sola genera valor claro en el escenario esperado.</b> Las otras once "
    "dan VAN negativo frente a esa vara de comparación en el escenario de mercado típico.", destacado_rojo))

st.extend(img(f'{G}/g4_van_por_propiedad.png', 14.5,
    "VAN a 10 años de las 12 propiedades. Solo Ref. W06.620 (Ipanema, 4 dormitorios) resulta positiva."))

st.append(Paragraph("Ganadora clara: Ref. W06.620 (Ipanema, 4 dormitorios, 138 m<super>2</super>, R$ 2.945.000)", h2))
st.append(Paragraph(
    "Es la única con VAN positivo en el escenario esperado (+R$ 584.393), con 5,6% de renta anual sobre "
    "la inversión total y 9,3% de tasa interna de retorno a 10 años. La razón conecta con lo que mostró "
    "la Parte 1: tiene el tamaño (la variable que más pesa) y la ubicación a favor al mismo tiempo, y "
    "puede cobrar una tarifa alta (~R$ 2.460/noche) en una zona con demanda turística fuerte (90 noches "
    "ocupadas al año es lo típico).", body))

st.extend(img(f'{G}/g7_flujo_acumulado_10anios.png', 13.8,
    "Flujo de fondos descontado acumulado. El valor del año 10 de cada línea es el VAN reportado; "
    "solo la línea verde termina por encima de cero."))

st.append(Paragraph("Grupo de las que casi cierran y las no recomendadas", h2))
st.append(Paragraph(
    "Tres propiedades (Copacabana 2 dorm., Ipanema 2 dorm., Leblon 3 dorm.) tienen TIR positiva (5-6%) "
    "pero por debajo de la tasa libre de riesgo. Si el alquiler rinde en la banda alta del mercado "
    "(percentil 75), pasan a ser rentables. Lagoa, Gávea y el apartamento de Flamengo no se recuperan "
    "ni en el mejor escenario: son barrios con muy poca demanda de alquiler turístico (24-36 noches/año "
    "típicas, contra 78-90 en Copacabana, Ipanema y Leblon).", body))

# =========================================================================
# TABLA COMPARATIVA RESUMEN
# =========================================================================
st.append(PageBreak())
st.append(Paragraph("Tabla resumen de las 12 propiedades", h1))
data = [["Ref.", "Barrio", "Dorm.", "Precio (R$)", "VAN 10 años (R$)", "TIR"]]
for _, r in res.iterrows():
    data.append([r['ref'], r['barrio'], str(int(r['dorm'])), f"{r['precio']:,.0f}",
                f"{r['van_base']:,.0f}", f"{r['tir_base']*100:.1f}%"])
t = Table(data, colWidths=[2*cm, 2.6*cm, 1.5*cm, 3*cm, 3.5*cm, 1.8*cm], repeatRows=1)
tstyle = [
    ('BACKGROUND', (0,0), (-1,0), NEGRO), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 5.5), ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
    ('BACKGROUND', (0,1), (-1,1), FONDO_VERDE), ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
]
t.setStyle(TableStyle(tstyle))
st.append(t)
st.append(Spacer(1, 10))
st.append(Paragraph(
    "El detalle año a año del flujo de fondos de cada una de las 12 propiedades, las tres matrices de "
    "sensibilidad completas (tasa de descuento, ocupación, gestión y precio de compra) y toda la ficha "
    "técnica están en el <b>Informe 2 (anexo de datos)</b>, que acompaña a este documento.", body))

st.append(Paragraph("Qué tan firme es esta conclusión", h1))
st.extend(img(f'{G}/g5_heatmap_tasa_ocupacion.png', 12,
    "Cantidad de propiedades viables cruzando tasa de descuento y nivel de ocupación."))
st.append(Paragraph(
    "Salvo en combinaciones poco realistas (tasa de descuento muy baja junto con ocupación muy por "
    "encima de lo típico), nunca conviene comprar más de 1 o 2 de las 12 propiedades a la vez. La "
    "conclusión no depende de un supuesto frágil.", body))

st.extend(img(f'{G}/g6_heatmap_tasa_descuento.png', 12,
    "Cantidad de propiedades viables cruzando tasa de descuento y rebaja negociada sobre el precio de lista."))
st.append(Paragraph(
    "Ni una rebaja de hasta 20% sobre el precio de lista cambia cuántas propiedades convienen — las "
    "columnas son prácticamente idénticas. Negociar el precio mejora la rentabilidad de cualquier "
    "propiedad, pero no es la palanca que decide si conviene comprarla.", body))

st.append(Paragraph(
    "Una salvedad importante: la tasa de comparación (7,12%) es la tasa libre de riesgo pura, sin "
    "prima por el riesgo propio de esta inversión (vacancia, gestión a distancia, tipo de cambio). Para "
    "que la compra se justifique frente al riesgo real que se está tomando, el retorno debería superar "
    "ese 7,12% por un margen adicional, no apenas igualarlo.", nota))

doc.build(st)
print("Informe 1 generado")
