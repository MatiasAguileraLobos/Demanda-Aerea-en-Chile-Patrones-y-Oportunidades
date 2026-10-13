import pandas as pd
import streamlit as st

from data_loader import load_clean_data, load_raw_data


@st.cache_data(show_spinner=False)
def obtener_resumen_datos() -> dict:
    """Calcula indicadores de estructura y reproduce en memoria el resumen de limpieza."""
    original = load_raw_data()
    preparado = load_clean_data()

    columnas_excluir = ["PAX_LIB", "CAR_LIB", "CORREO"]
    columnas_excluidas = [col for col in columnas_excluir if col in original.columns]

    # Reproduce los pasos documentados sobre una copia; no modifica ni guarda los CSV.
    copia = original.copy()
    columnas_texto = copia.select_dtypes(include=["object", "string"]).columns
    for columna in columnas_texto:
        copia[columna] = copia[columna].str.strip()
    copia = copia.drop(columns=columnas_excluidas)

    mascara_nulos = copia.isna().any(axis=1)
    filas_con_nulos = copia.loc[mascara_nulos]
    filas_eliminadas_por_nulos = int(mascara_nulos.sum())
    columnas_codigo_geografico = [
        col for col in ["ORIG_1", "DEST_1", "ORIG_2", "DEST_2"]
        if col in filas_con_nulos.columns
    ]
    filas_con_awc = (
        int(filas_con_nulos[columnas_codigo_geografico].eq("AWC").any(axis=1).sum())
        if columnas_codigo_geografico
        else 0
    )
    operadores_afectados = sorted(
        filas_con_nulos["Operador"].dropna().astype(str).unique().tolist()
    ) if "Operador" in filas_con_nulos.columns else []

    sin_nulos = copia.loc[~mascara_nulos].copy()
    filas_eliminadas_por_duplicados = int(sin_nulos.duplicated().sum())
    resultado_reproducido = sin_nulos.drop_duplicates().copy()

    def periodo(df: pd.DataFrame) -> str:
        if "Año" not in df.columns or df["Año"].dropna().empty:
            return "No disponible"
        return f"{int(df['Año'].min())}–{int(df['Año'].max())}"

    columnas_ausentes = [col for col in columnas_excluir if col not in preparado.columns]
    dimensiones_coinciden = (
        resultado_reproducido.shape == preparado.shape
        and resultado_reproducido.columns.tolist() == preparado.columns.tolist()
    )
    validacion_correcta = (
        dimensiones_coinciden
        and int(preparado.isna().sum().sum()) == 0
        and int(preparado.duplicated().sum()) == 0
        and len(columnas_ausentes) == len(columnas_excluir)
    )

    return {
        "original_filas": len(original),
        "original_columnas": len(original.columns),
        "original_periodo": periodo(original),
        "preparado_filas": len(preparado),
        "preparado_columnas": len(preparado.columns),
        "preparado_periodo": periodo(preparado),
        "columnas_excluidas": columnas_excluidas,
        "filas_nulas": filas_eliminadas_por_nulos,
        "filas_duplicadas": filas_eliminadas_por_duplicados,
        "filas_awc_con_nulos": filas_con_awc,
        "operadores_con_nulos": operadores_afectados,
        "nulos_restantes": int(preparado.isna().sum().sum()),
        "duplicados_restantes": int(preparado.duplicated().sum()),
        "validacion_correcta": validacion_correcta,
    }


def formato_entero(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


# Navegación existente de la aplicación.
st.sidebar.page_link("app.py", label="Inicio")
st.sidebar.page_link("pages/1_Contexto.py", label="Contexto y Datos")
st.sidebar.page_link("pages/2_EDA.py", label="EDA")
st.sidebar.page_link("pages/3_Analisis.py", label="Análisis")

st.title("Demanda Aérea en Chile: Patrones y Oportunidades")
st.write(
    "La demanda de pasajeros cambia entre rutas, aerolíneas y periodos. "
    "Explorar sus patrones puede aportar contexto para la planificación "
    "del transporte aéreo, sin que los datos por sí solos expliquen las causas de esas variaciones."
)

st.subheader("Pregunta de investigación")
st.info(
    "¿Cómo varía la demanda de pasajeros según el origen, destino, aerolínea y mes, "
    "y qué patrones pueden identificarse en el tráfico aéreo de Chile?"
)

st.subheader("Fuente, periodo y unidad de observación")
st.write(
    "La fuente es el dataset **Tráfico aéreo histórico** del Portal de Datos Abiertos "
    "del Gobierno de Chile, publicado por la Junta de Aeronáutica Civil (JAC). "
    "Los archivos disponibles cubren el periodo que se resume más abajo."
)
st.caption(
    "Cada registro corresponde a una combinación registrada de ruta, aerolínea y periodo "
    "(año y mes); no representa automáticamente un vuelo individual."
)

st.subheader("Variables del proyecto")
col_y, col_x, col_t = st.columns(3)
with col_y:
    st.markdown("**Y · Variable objetivo**")
    st.write("`PASAJEROS`: número de pasajeros que pagaron su pasaje y quedaron registrados en cada observación.")
with col_x:
    st.markdown("**X · Variables explicativas**")
    st.write(
        "Origen y destino (`ORIG_1`, `DEST_1`), aerolínea (`Operador`), "
        "tipo de tráfico (`NAC`) y distancia registrada (`Distancia`)."
    )
with col_t:
    st.markdown("**T · Contexto temporal**")
    st.write("Año (`Año`) y mes (`Mes`).")

resumen = obtener_resumen_datos()
st.subheader("Estructura de los archivos")
col_original, col_preparado = st.columns(2)
with col_original:
    st.markdown("**Dataset original**")
    st.metric("Filas", formato_entero(resumen["original_filas"]))
    st.metric("Columnas", formato_entero(resumen["original_columnas"]))
    st.metric("Periodo", resumen["original_periodo"])
with col_preparado:
    st.markdown("**Dataset preparado para el análisis**")
    st.metric("Filas", formato_entero(resumen["preparado_filas"]))
    st.metric("Columnas", formato_entero(resumen["preparado_columnas"]))
    st.metric("Periodo", resumen["preparado_periodo"])

st.info(
    "**Dataset preparado:** "
    f"{formato_entero(resumen['preparado_filas'])} registros · "
    f"{formato_entero(resumen['preparado_columnas'])} columnas · "
    f"{formato_entero(resumen['nulos_restantes'])} valores nulos · "
    f"{formato_entero(resumen['duplicados_restantes'])} duplicados exactos."
)

st.subheader("Preparación documentada")
metricas_limpieza = st.columns(3)
metricas_limpieza[0].metric(
    "Columnas excluidas", formato_entero(len(resumen["columnas_excluidas"]))
)
metricas_limpieza[1].metric(
    "Filas retiradas por nulos", formato_entero(resumen["filas_nulas"])
)
metricas_limpieza[2].metric(
    "Duplicados exactos retirados", formato_entero(resumen["filas_duplicadas"])
)

st.markdown(
    "Se excluyeron `PAX_LIB`, `CAR_LIB` y `CORREO` por no ser centrales para el análisis "
    "principal. Las filas con valores faltantes en las columnas conservadas se retiraron "
    "sin imputación. El notebook documenta que esos registros corresponden a "
    "AEROVIAS DAP y contienen el código geográfico `AWC`; su significado y una corrección "
    "fiable no pudieron verificarse, por lo que el código no se reemplazó."
)
st.markdown(
    "Los duplicados se eliminaron solo cuando las filas eran exactamente iguales, después "
    "de retirar las filas incompletas. En los campos de texto se recortaron espacios externos; "
    "no se cambiaron códigos, nombres ni mayúsculas de forma arbitraria."
)
st.caption(
    f"Entre las {formato_entero(resumen['filas_nulas'])} filas retiradas por datos faltantes, "
    f"{formato_entero(resumen['filas_awc_con_nulos'])} contienen `AWC` en los códigos de ruta. "
    "Como no fue posible verificar qué representa el código ni establecer una corrección fiable, "
    "se mantuvo sin reemplazar. Los conteos se calculan desde los archivos y la limpieza se "
    "reproduce en memoria; los CSV originales no se modifican."
)

if resumen["validacion_correcta"]:
    st.success(
        "El conjunto preparado conserva las variables y el periodo necesarios para explorar "
        "la demanda por ruta, operador, tipo de tráfico y tiempo. Los registros incompletos "
        "y duplicados exactos se trataron según los criterios descritos arriba."
    )
else:
    st.warning(
        "La comprobación del proceso reproducido no coincide completamente con el dataset "
        "preparado. Revisa los archivos antes de interpretar estos indicadores."
    )
