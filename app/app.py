import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

st.title("Demanda de vuelos en Chile")

# Barra lateral
st.sidebar.page_link('app.py', label='Home', icon='')
st.sidebar.page_link('pages/1_Contexto.py', label='Contexto', icon='')
st.sidebar.page_link('pages/2_EDA.py', label='EDA', icon='')
st.sidebar.page_link('pages/3_Analisis.py', label='Analisis', icon='')

archivo = st.file_uploader(
    "Seleccione el archivo dataset.csv",
    type=["csv"]
)

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