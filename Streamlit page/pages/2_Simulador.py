import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go

st.subheader("Simulador")

if "datos" not in st.session_state:
    st.warning(
        "Primero debe cargar el dataset desde la pagina principal."
    )
    st.stop()

if "modelos" not in st.session_state:
    st.warning(
        "Los modelos aun no han sido entrenados."
    )
    st.stop()

modelos = st.session_state["modelos"]
df = st.session_state["datos"]
nodos = df["Nodo"].unique()

# Barra lateral -----------------------
st.sidebar.header("Panel de Filtros")

temp_maxima = st.sidebar.slider(
    "Filtrar por Temperatura Máxima (°C)", 
    min_value=0, max_value=200, value=100, step=1
)

carga_cpu = st.sidebar.slider(
    "Filtrar por carga CPU (%)", 
    min_value=0, max_value=100, value=50, step=1
)
# --------------------------------------

df_filtrado = df[df['Temperatura'] <= temp_maxima]
df_filtrado = df[df['Carga_CPU'] <= carga_cpu]

# Datos de entrada para los modelos
datos_entrada = [[temp_maxima, carga_cpu]]

# Predicción para cada Rack
predicciones = {}

for rack in nodos:
    modelo = modelos[rack]
    predicciones[rack] = float(modelo.predict(datos_entrada)[0])

# Mostrar resultados
st.subheader("Tiempo de cómputo estimado")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Rack A",
    f"{predicciones['Rack A']:.1f} s"
)

col2.metric(
    "Rack B",
    f"{predicciones['Rack B']:.1f} s"
)

col3.metric(
    "Rack C",
    f"{predicciones['Rack C']:.1f} s"
)

col4.metric(
    "Rack D",
    f"{predicciones['Rack D']:.1f} s"
)

# Buscar rack recomendado
rack_recomendado = min(predicciones, key=predicciones.get)

# Mensaje en caso de exito
st.success(f"Rack recomendado: {rack_recomendado}")

st.divider()

# Grafico de barras ----------------
st.subheader("Comparación de tiempos")

racks = list(predicciones.keys())
tiempos = list(predicciones.values())

colores = [
    "#2E86DE" if rack == rack_recomendado else "#BDBDBD"
    for rack in racks
]

fig = go.Figure(
    data=[
        go.Bar(
            x=racks,
            y=tiempos,
            marker_color=colores,
            text=[f"{tiempo:.1f} s" for tiempo in tiempos],
            textposition="auto"
        )
    ]
)

fig.update_layout(
    title="Tiempo de cómputo estimado por Rack",
    xaxis_title="Servidor",
    yaxis_title="Tiempo estimado (s)",
    showlegend=False
)
# ------------------------------------

st.plotly_chart(fig, use_container_width=True)