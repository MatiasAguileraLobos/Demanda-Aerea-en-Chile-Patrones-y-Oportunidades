import streamlit as st
import pandas as pd
import os

# Barra lateral
st.sidebar.page_link('app.py', label='Home', icon='')
st.sidebar.page_link('pages/1_Contexto.py', label='Contexto', icon='')
st.sidebar.page_link('pages/2_EDA.py', label='EDA', icon='')
st.sidebar.page_link('pages/3_Analisis.py', label='Analisis', icon='')

st.title("Demanda Aérea en Chile: Patrones y Oportunidades")

st.subheader("Problematica")
st.write(
    "Las aerolineas operan en un mercado donde la demanda de los " +
    "pasajeros es dinámica y cambia con el tiempo. Esto las obliga " +
    "a adaptar constantemente sus estrategias y planificación para " +
    "para responder a las variaciones del mercado."
)

st.subheader("Motivación")
st.write(
    "Con este proyecto buscamos identificar oportunidades en los patrones " +
    "de la demanda de vuelos que aporten a la toma de desiciones de las " + 
    "aerolineas."
)

root_directory = os.path.dirname(os.path.dirname(__file__))
df = pd.read_csv(root_directory + "/data/raw/trafico_historico.csv", sep=";")

st.session_state["df"] = df