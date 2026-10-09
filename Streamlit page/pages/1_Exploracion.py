import streamlit as st
import plotly.express as px
import sklearn.metrics as sk

st.subheader("Exploración de datos")
st.subheader("Graficos")
if "datos" not in st.session_state:
    st.warning(
        "Primero debe cargar el dataset desde la pagina principal."
    )
    st.stop()

df = st.session_state["datos"]
nodos = df["Nodo"].unique()

# Para mostrar una tabla con los datos
# st.dataframe(df.head(), use_container_width=True)

# Para añadir una linea de separacion
# st.divider()

# Para mostrar una parte de los datos filtrados
# st.write(f"Mostrando {len(df_filtrado)} registros filtrados:")
# st.dataframe(df_filtrado, use_container_width=True)

# Barra lateral -----------------------
st.sidebar.header("Panel de Filtros")

nodos_seleccionados = st.sidebar.multiselect(
    "Seleccione Racks a monitorear:", 
    options=nodos, 
    default=nodos
)

temp_maxima = st.sidebar.slider(
    "Filtrar por Temperatura Máxima (°C)", 
    min_value=0, max_value=200, value=100, step=1
)
# --------------------------------------

# Tablas filtradas
df_filtrado = df[df['Nodo'].isin(nodos_seleccionados)]
df_filtrado = df_filtrado[df_filtrado['Temperatura'] <= temp_maxima]

# Grafico 1
fig_line = px.line(df_filtrado, x='Tiempo', y='Carga_CPU', color='Nodo', 
    title="Evolución de Carga CPU por Rack")
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# Grafico 2
fig_scatter = px.scatter(df_filtrado, x='Temperatura', y='Latencia', 
    color='Nodo', size='Carga_CPU', 
    title="Correlación: Temperatura vs Latencia (Burbuja = CPU)")
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

st.subheader("Breve analisis")

st.markdown(
    "Mientras que cada Rack tiene sus propias capacidades, es decir, su latencia es distinta a los otros Racks con la misma temperatura," \
    " todos comparten el que a mayor sea la temperatura, mayor es la latencia, pero algúnos como el Rack A tienen una mayor resistencia al" \
    " aumento de la temperatura, pues crece a un ritmo mucho más bajo, y empieza con una latencia igualmente baja."
)