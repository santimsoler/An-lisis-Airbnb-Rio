# Río de Janeiro: qué determina el precio de un Airbnb, y qué propiedades conviene comprar

**Pablo Santiago Martínez Soler**

Este repositorio tiene dos proyectos conectados:

1. **`/notebooks`** — Análisis de más de 43.000 publicaciones reales de Airbnb en Río de Janeiro para identificar qué determina el precio de un alojamiento. Cinco modelos comparados (regresión lineal, LASSO, Random Forest, Gradient Boosting), selección del mejor e importancia de cada variable.
2. **`/inversion_inmobiliaria`** — Usa esa misma base de datos de mercado (tarifas y ocupación reales por barrio) para evaluar si conviene comprar cada una de 12 propiedades concretas en oferta hoy, proyectando el flujo de fondos a 10 años.

## Resultado principal

El mejor modelo de precios (Gradient Boosting) explica el 63% de la variación del precio (R² = 0,63, RMSE = R$ 481). El tamaño del alojamiento (dormitorios, baños, capacidad) es el factor más determinante, seguido por la ubicación.

De las 12 propiedades evaluadas para inversión, **solo una (Ref. W06.620, Ipanema, 4 dormitorios) genera VAN positivo** en el escenario esperado de mercado — el resto no supera el retorno de invertir el dinero sin riesgo. El resultado es robusto: se sensibilizó contra tasa de descuento, nivel de ocupación, costo de gestión y margen de negociación sobre el precio de compra, y la conclusión no cambia en la enorme mayoría de los escenarios razonables.

## Estructura

```
├── notebooks/
│   └── analisis_precios_airbnb_rio.ipynb      # Parte 1: modelo de precios completo
├── data/
│   └── listings.csv.gz                        # dataset (Inside Airbnb)
├── informe.pdf                                # evaluación académica del modelo de precios
├── inversion_inmobiliaria/
│   ├── informes/
│   │   ├── 1_informe_ejecutivo.pdf            # informe principal, con gráficos (para el inversor)
│   │   ├── 2_anexo_datos_detallado.pdf        # flujo de fondos año a año + sensibilidad completa
│   │   ├── make_informe_1.py
│   │   └── make_informe_2.py
│   ├── scripts/
│   │   ├── calcular_flujos.py                 # cálculo de VAN/TIR de las 12 propiedades
│   │   ├── sensibilidad.py                    # sensibilidad a tasa, ocupación y gestión
│   │   ├── sens_descuento.py                  # sensibilidad al precio de compra
│   │   ├── extraer_flujos_detalle.py          # flujo de fondos año a año
│   │   ├── graficos_parte1.py                 # gráficos del modelo de precios
│   │   └── graficos_parte2.py                 # gráficos de la evaluación de inversión
│   ├── resultados/                            # CSVs y JSON con todos los resultados numéricos
│   └── graficos/                              # PNGs usados en los informes
├── requirements.txt
└── LICENSE
```

## Cómo leer esto

- Si solo tenés tiempo para un documento: **`inversion_inmobiliaria/informes/1_informe_ejecutivo.pdf`**. Cuenta toda la historia — el modelo de precios y la evaluación de las 12 propiedades — con gráficos, sin necesidad de leer código.
- Si necesitás auditar un número puntual (el flujo de fondos completo de una propiedad, una celda de una matriz de sensibilidad, un supuesto): **`inversion_inmobiliaria/informes/2_anexo_datos_detallado.pdf`**.
- Si querés reproducir o modificar el análisis: los notebooks y scripts en `/notebooks` y `/inversion_inmobiliaria/scripts`.

## Metodología, en síntesis

**Parte 1 — Modelo de precios.** Fuente: Inside Airbnb (Río de Janeiro). 44.542 publicaciones con precio válido, 43.395 tras tratamiento de outliers (percentil 99 combinado de precio y precio por persona). Se compararon 5 modelos; ganó Gradient Boosting por histogramas. Importancia de variables por permutación.

**Parte 2 — Evaluación de inversión.** Para cada una de las 12 propiedades relevadas, se buscaron comparables reales (mismo barrio, misma cantidad de dormitorios) entre los alojamientos activos de Airbnb, se tomó su tarifa y ocupación típica, se proyectó el flujo de fondos a 10 años descontando todos los costos (comisión de plataforma, administración, expensas, IPTU, energía, mantenimiento, impuesto a la renta), y se comparó el VAN resultante contra la tasa libre de riesgo de Brasil (7,12% real, Tesouro IPCA+).

Todos los supuestos completos están en la ficha técnica del Informe 2 y en `inversion_inmobiliaria/resultados/supuestos.json`.

## Limitaciones principales

- No se modeló financiamiento (compra de contado) ni riesgo cambiario.
- Dos propiedades (Gávea y Flamengo) tienen muy pocos comparables directos en los datos.
- El impuesto a la renta (7,5%) es un promedio general; conviene confirmarlo con un contador en Brasil.
- La tasa de descuento usada es la tasa libre de riesgo pura, sin prima por el riesgo específico de la inversión.

Detalle completo en la ficha técnica de `2_anexo_datos_detallado.pdf`.

## Cómo correrlo

```bash
pip install -r requirements.txt
jupyter notebook notebooks/analisis_precios_airbnb_rio.ipynb
python inversion_inmobiliaria/scripts/calcular_flujos.py
```

## Herramientas

Python, pandas, scikit-learn, matplotlib, seaborn, ReportLab.
