import streamlit as st

from data_loader import load_clean_data


st.set_page_config(
    page_title="Demanda Aérea en Chile",
    page_icon="✈️",
    layout="wide",
)

# Navegación compartida con el resto de la aplicación.
st.sidebar.page_link("app.py", label="Inicio")
st.sidebar.page_link("pages/1_Contexto.py", label="Contexto y Datos")
st.sidebar.page_link("pages/2_EDA.py", label="EDA")
st.sidebar.page_link("pages/3_Analisis.py", label="Análisis")

df = load_clean_data()
columnas_indicadores = {"Año", "Operador", "ORIG_1", "DEST_1"}
columnas_ausentes = columnas_indicadores.difference(df.columns)

st.title("Demanda Aérea en Chile: Patrones y Oportunidades")
st.subheader("Una mirada a la evolución y distribución de los pasajeros registrados")
st.write(
    "Exploramos cómo varía el tráfico aéreo de Chile a través del tiempo y entre "
    "rutas, operadores y tipos de tráfico, usando registros históricos de la Junta "
    "de Aeronáutica Civil (JAC)."
)

with st.container(border=True):
    st.markdown("#### Pregunta de investigación")
    st.markdown(
        "> ¿Cómo varía la demanda de pasajeros según el origen, destino, aerolínea "
        "y mes, y qué patrones pueden identificarse en el tráfico aéreo de Chile?"
    )

st.header("El proyecto")
col_problema, col_motivacion = st.columns(2, gap="large")
with col_problema:
    with st.container(border=True):
        st.markdown("#### Problemática")
        st.write(
            "La demanda aérea cambia entre periodos, rutas y operadores. Comprender "
            "cómo se distribuye y evoluciona el tráfico registrado permite describir "
            "esas diferencias con mayor claridad."
        )
with col_motivacion:
    with st.container(border=True):
        st.markdown("#### Motivación")
        st.write(
            "Identificar patrones de demanda puede aportar contexto para analizar "
            "el tráfico aéreo y apoyar futuras decisiones de planificación, sin "
            "atribuir causas que estos datos no permiten comprobar."
        )

st.header("Los datos en cifras")
if columnas_ausentes:
    st.warning(
        "No fue posible calcular todos los indicadores: al dataset preparado le "
        f"faltan las columnas {', '.join(sorted(columnas_ausentes))}."
    )
else:
    años = df["Año"].dropna()
    periodo = f"{int(años.min())}–{int(años.max())}" if not años.empty else "Sin dato"
    cantidad_registros = len(df)
    cantidad_operadores = df["Operador"].nunique(dropna=True)
    pares_ruta = df[["ORIG_1", "DEST_1"]].dropna().drop_duplicates()
    cantidad_rutas = len(pares_ruta)

    metricas = st.columns(4, gap="medium")
    metricas[0].metric("Periodo disponible", periodo)
    metricas[1].metric("Registros preparados", f"{cantidad_registros:,}".replace(",", "."))
    metricas[2].metric("Operadores distintos", f"{cantidad_operadores:,}".replace(",", "."))
    metricas[3].metric("Rutas direccionales", f"{cantidad_rutas:,}".replace(",", "."))

st.caption(
    "Fuente: Junta de Aeronáutica Civil (JAC). Los registros representan combinaciones "
    "de ruta, operador y periodo; no equivalen necesariamente a vuelos individuales. "
    "Una ruta direccional se cuenta como un par único de origen (ORIG_1) y destino "
    "(DEST_1), por lo que el trayecto inverso se considera aparte."
)

st.header("Recorrido de la aplicación")
st.write("Cada página aborda una parte distinta de la pregunta del proyecto.")
col_contexto, col_eda, col_analisis = st.columns(3, gap="large")

with col_contexto:
    with st.container(border=True):
        st.markdown("#### 1. Contexto y Datos")
        st.write("Conoce la fuente, el periodo, las variables y la preparación del dataset.")
        st.page_link("pages/1_Contexto.py", label="Ir a Contexto y Datos", icon=":material/info:")

with col_eda:
    with st.container(border=True):
        st.markdown("#### 2. EDA")
        st.write("Explora distribuciones, categorías, comparaciones y relaciones entre variables.")
        st.page_link("pages/2_EDA.py", label="Ir al EDA", icon=":material/insights:")

with col_analisis:
    with st.container(border=True):
        st.markdown("#### 3. Análisis")
        st.write("Revisa la evolución temporal, los patrones mensuales y la concentración por operador y ruta.")
        st.page_link("pages/3_Analisis.py", label="Ir al Análisis", icon=":material/trending_up:")
