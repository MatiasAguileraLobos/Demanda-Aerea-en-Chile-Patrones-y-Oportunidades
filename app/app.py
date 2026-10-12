import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
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

"""
if archivo is not None:
    # Leer dataset
    df = pd.read_csv(archivo)
    # Guardar datos en la sesion
    st.session_state["datos"] = df
    # Diccionario para guardar los modelos
    modelos = {}
    for rack in df["Nodo"].unique():
        df_rack = df[df["Nodo"] == rack]
        X = df_rack[
            ["Temperatura", "Carga_CPU"]
        ]
        y = df_rack["Latencia"]
        modelo = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        modelo.fit(X, y)
        modelos[rack] = modelo

    # Guardar los modelos entrenados
    st.session_state["modelos"] = modelos
    st.success("Datos y modelos cargados correctamente.")
"""