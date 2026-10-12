import streamlit as st
import pandas as pd
import plotly.express as px

# Barra lateral
st.sidebar.page_link('app.py', label='Home', icon='')
st.sidebar.page_link('pages/1_Contexto.py', label='Contexto', icon='')
st.sidebar.page_link('pages/2_EDA.py', label='EDA', icon='')
st.sidebar.page_link('pages/3_Analisis.py', label='Analisis', icon='')

st.title("EDA")

st.write(
    "Para realizar este proyecto utilizamos un dataset de los vuelos que han" +
    "pasado por Chile desde 1984 hasta 2025, recompilado por la Junta de " +
    "Aeronáutica Civil."
)

st.write(
    "Divideros nuestra estructurá en 3 componentes, X, Y y T:\n" +
    "X: Caracteristicas del vuelo (origen/destino, aerolínea, mes).\n" +
    "Y: Cantidad de pasajeros.\n" +
    "T: Contexto temporal, en este caso, años."
)

st.header("Estructura y calidad de los datos")
st.subheader("Dimensiones del conjunto de datos")
st.write(
    "Primero revisaremos cuántos registros y variables contiene el " +
    "archivo. Esta comprobación permite dimensionar el análisis y " +
    "contrastar la cantidad de observaciones descrita en el README con " +
    "el CSV utilizado, sin modificar los datos."
)

df = st.session_state["df"]

filas, columnas = df.shape

st.write(f"Cantidad de registros: {filas:,}")
st.write(f"Cantidad de variables: {columnas}")

st.subheader("Variables y tipos de datos")
st.write(
    "Revisaremos los nombres originales y los tipos que pandas asignó al cargar " +
    "el archivo completo. Los tipos ayudan a detectar columnas que podrían requerir " +
    "atención antes de analizarlas; en esta etapa solo inspeccionaremos, sin convertirlas."
)

# Construccion de tabla con el nombre de las variables y el tipo de datos
tabla = {"Nombre": [], "Tipo": []}
# Nombre de las variables
for variable in df.columns.tolist():
    tabla["Nombre"].append(variable)
# Tipo de datos
for tipo in df.dtypes.tolist():
    tabla["Tipo"].append(tipo)

st.table(tabla, alt="Nombre de las variables y sus tipos")

st.subheader("Valores faltantes")
st.write(
    "Cuantificaremos los faltantes por variable, tanto en cantidad como en porcentaje. " +
    "Esto permite evaluar qué variables están completas y considerar si los faltantes afectan " +
    "el análisis de demanda o variables contextuales."
)

faltantes = pd.DataFrame({
    "faltantes": df.isna().sum(),
    "porcentaje": (df.isna().mean() * 100).round(2)
})
faltantes = faltantes.sort_values("faltantes", ascending=False)
faltantes[faltantes["faltantes"] > 0]

# Calcular la cantidad de valores faltantes y no faltantes
total_faltantes = df.isna().sum().sum()
total_no_faltantes = df.notna().sum().sum()

# Calcular valores faltantes y no faltantes
total_faltantes = df.isna().sum().sum()
total_no_faltantes = df.notna().sum().sum()

# Crear columnas para mostrar ambos gráficos lado a lado
col1, col2 = st.columns(2)

# Gráfico 1: valores faltantes vs. no faltantes
with col1:
    st.subheader("Proporción de valores faltantes")

    datos_pastel = pd.DataFrame({
        "Estado": ["Valores faltantes", "Valores no faltantes"],
        "Cantidad": [total_faltantes, total_no_faltantes]
    })

    if total_faltantes == 0:
        st.success("No hay valores faltantes en el conjunto de datos.")
    else:
        fig1 = px.pie(
            datos_pastel,
            names="Estado",
            values="Cantidad",
            title="Valores faltantes vs. completos",
            color="Estado",
            color_discrete_map={
                "Valores faltantes": "#EF553B",
                "Valores no faltantes": "#636EFA"
            },
            hole=0.3
        )

        fig1.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: distribución de valores faltantes por columna
with col2:
    st.subheader("Valores faltantes por columna")

    # Calcular los valores faltantes por columna
    faltantes_columna = df.isna().sum()

    # Conservar solo las columnas que tienen valores faltantes
    faltantes_columna = faltantes_columna[faltantes_columna > 0]

    if faltantes_columna.empty:
        st.info("No hay columnas con valores faltantes.")
    else:
        # Crear DataFrame y calcular el porcentaje del total de faltantes
        datos_columnas = pd.DataFrame({
            "Columna": faltantes_columna.index,
            "Cantidad de faltantes": faltantes_columna.values
        })

        total_faltantes = datos_columnas["Cantidad de faltantes"].sum()

        datos_columnas["Porcentaje del total"] = (
            datos_columnas["Cantidad de faltantes"]
            / total_faltantes * 100
        )

        # Crear gráfico circular
        fig2 = px.pie(
            datos_columnas,
            names="Columna",
            values="Cantidad de faltantes",
            title="Distribución de faltantes por columna",
            hole=0.3,
            hover_data=["Porcentaje del total"]
        )

        fig2.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Valores faltantes: %{value:,}<br>"
                "Porcentaje del total: %{percent}"
                "<extra></extra>"
            )
        )

        st.plotly_chart(fig2, use_container_width=True)

# Mostrar resumen numérico
st.write(f"**Total de valores faltantes:** {total_faltantes:,}")
st.write(f"**Total de valores completos:** {total_no_faltantes:,}")

if total_faltantes > 0:
    porcentaje = total_faltantes / (total_faltantes + total_no_faltantes) * 100
    st.write(f"**Porcentaje global de faltantes:** {porcentaje:.2f}%")