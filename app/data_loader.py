from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "trafico_historico.csv"
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "trafico_limpio.csv"


@st.cache_data
def load_raw_data() -> pd.DataFrame:
    """Carga el CSV original sin modificar su contenido."""
    return pd.read_csv(RAW_DATA_PATH, sep=";")


@st.cache_data
def load_clean_data() -> pd.DataFrame:
    """Carga el dataset preparado para los análisis principales."""
    return pd.read_csv(CLEAN_DATA_PATH, sep=";")
