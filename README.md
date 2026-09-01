# Demanda Aérea en Chile: Patrones y Oportunidades

## Integrantes

- Matías Aguilera
- Maximiliano Duarte

## Descripción del problema

Las aerolíneas operan en un mercado donde la demanda de los pasajeros es dinámica y cambia con el tiempo. Esto las obliga a adaptar constantemente sus estrategias y planificación para responder a las variaciones del mercado.

El análisis del tráfico aéreo puede permitir identificar patrones en el comportamiento de la demanda y entregar información útil para apoyar la planificación y toma de decisiones de las aerolíneas.

## Motivación

El proyecto busca identificar oportunidades en la demanda de pasajeros que puedan aportar a la toma de decisiones de las aerolíneas.

## Pregunta inicial

> ¿Cómo varía la demanda de pasajeros según el origen, destino, aerolínea y mes, y qué patrones pueden identificarse en el tráfico aéreo de Chile?

## Alcance

### Fenómeno

La variación y distribución de la demanda de pasajeros en el tráfico aéreo de Chile.

### Conocimiento a apoyar

Identificar patrones que puedan aportar a la planificación y toma de decisiones de las aerolíneas.

### Unidad de observación

Ruta operada por una aerolínea en un determinado mes y año.

La demanda será medida mediante la cantidad de pasajeros transportados para cada combinación de ruta, aerolínea, mes y año.

### Población y contexto

Vuelos con origen o destino en Chile, tanto nacionales como internacionales.

### Periodo

1984–2025.

### Límites iniciales

- El análisis se centrará en la cantidad de pasajeros como indicador de demanda.
- No se analizarán vuelos individuales, sino la demanda agregada por ruta, aerolínea, mes y año.
- No se buscará explicar las razones por las que los pasajeros eligen una determinada ruta o aerolínea.
- No se considerarán factores externos que no estén disponibles en los datos.
- Las variables de carga y correo no serán parte del análisis principal debido a la presencia de datos faltantes.

## Dataset

### Fuente

Portal de Datos Abiertos del Gobierno de Chile.

Dataset: **Tráfico aéreo histórico**.

### Descripción de los datos

El dataset contiene registros históricos del tráfico aéreo nacional e internacional asociado a Chile.

El conjunto de datos contiene **251.117 registros**, con una cobertura temporal entre **1984 y 2025**.

Entre las principales variables disponibles se encuentran:

- Año
- Mes
- Operador / aerolínea
- Origen
- Destino
- País de origen
- País de destino
- Tipo de tráfico (nacional / internacional)
- Cantidad de pasajeros
- Distancia
- Otras variables asociadas al tráfico aéreo

La variable principal del proyecto es `PASAJEROS`, utilizada como indicador de la demanda.

## Análisis inicial

El proyecto busca explorar patrones y variaciones en la demanda de pasajeros, considerando principalmente:

- Demanda según origen y destino.
- Pasajeros transportados por aerolínea.
- Variación mensual y estacionalidad.
- Evolución de la demanda a través de los años.
- Diferencias entre tráfico nacional e internacional.
- Relación entre distancia y cantidad de pasajeros.

El componente temporal también permitirá evaluar posteriormente la posibilidad de desarrollar modelos para estimar la demanda en periodos futuros.

## Estructura del repositorio

```text
Proyecto_Visualizacion/
│
├── app/
│
├── data/
│   ├── processed/
│   └── raw/
│       └── trafico_historico.csv
│
├── figures/
│
├── notebooks/
│   └── notebook_inicial.ipynb
│
├── src/
│
├── .gitignore
└── README.md