import streamlit as st

# Barra lateral
st.sidebar.page_link('app.py', label='Home', icon='')
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