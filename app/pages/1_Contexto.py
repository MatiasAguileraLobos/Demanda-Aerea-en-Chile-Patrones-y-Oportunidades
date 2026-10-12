import streamlit as st
import pandas as pd

# Barra lateral
st.sidebar.page_link('app.py', label='Inicio', icon='')
st.sidebar.page_link('pages/1_Contexto.py', label='Contexto', icon='')
st.sidebar.page_link('pages/2_EDA.py', label='EDA', icon='')
st.sidebar.page_link('pages/3_Analisis.py', label='Analisis', icon='')

st.title("Contexto")

st.write(
    "Cada día, cientos de vuelos conectan ciudades y regiones de Chile con " + 
    "destinos nacionales e internacionales, movilizando aerolíneas, " + 
    "tripulaciones y pasajeros en un mercado que evoluciona constantemente " + 
    "a través de los años."
)

df = st.session_state["df"]

# Suma de la cantidad de filas por año
años = df["Año"].value_counts().sort_index()

st.subheader("Evolución de la cantidad de vuelos en Chile")
# Grafico de barras
st.bar_chart(años, color="#3498DB")

st.subheader("Evolución de la cantidad de pasajeros de vuelos en Chile")
# Suma de la cantidad de pasajeros por año 
pasajeros_por_año = df.groupby("Año")["PASAJEROS"].sum().sort_index()

# Grafico de barras
st.bar_chart(pasajeros_por_año, color="#2ECC71")