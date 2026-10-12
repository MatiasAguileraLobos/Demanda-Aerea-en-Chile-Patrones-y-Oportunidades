import streamlit as st
import pandas as pd
import plotly.express as px

# Barra lateral
st.sidebar.page_link('app.py', label='Inicio', icon='')
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
    "Divideros nuestra estructurá en 3 componentes, X, Y y T:\n\n" +
    "X: Caracteristicas del vuelo (origen/destino, aerolínea, mes).\n\n" +
    "Y: Cantidad de pasajeros.\n\n" +
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
tabla = {"Nombre": [], "Tipo": [], 
         "Descripción": [
             "Año de la información del registro.",
             "Mes de la información del registro.",
             "Código de operador utilizado por las aerolíneas.",
             "Nombre del operador.",
             "Grupo empresarial al que pertenece el operador.",
             "Código del aeropuerto de origen (direccional) en formato IATA.",
             "Código del aeropuerto de destino (direccional) en formato IATA.",
             "Nombre de ciudad que el aeropuerto de origen (direccional) sirve.",
             "Nombre de ciudad que el aeropuerto de destino (direccional) sirve.",
             "Nombre de país del aeropuerto de origen (direccional).",
             "Nombre de país del aeropuerto de destino (direccional).",
             "Código del aeropuerto de origen (por ruta) en formato IATA.",
             "Código del aeropuerto de destino (por ruta) en formato IATA.",
             "Nombre de ciudad que el aeropuerto de origen (por ruta) sirve.",
             "Nombre de ciudad que el aeropuerto de destino (por ruta) sirve.",
             "Nombre de país del aeropuerto de origen (por ruta).",
             "Nombre de país del aeropuerto de destino (por ruta).",
             "Identificador de llegada/salida, con referencia al origen de la ruta.",
             "Identificador de tipo de tráfico (nacional o internacional).",
             "Número de pasajeros libres de pago.",
             "Número de pasajeros de pago.",
             "Carga libre de pago (Kg).",
             "Carga total (Ton).",
             "Correo de pago (Kg).",
             "Distancia lineal entre el origen y el destino."
         ]
}
# Nombre de las variables
for variable in df.columns.tolist():
    tabla["Nombre"].append(variable)
# Tipo de datos
for tipo in df.dtypes.tolist():
    tabla["Tipo"].append(tipo)
#---------------------------

st.table(tabla, alt="Nombre de las variables, sus tipos y descripción")

st.subheader("Valores faltantes")
st.write(
    "Cuantificaremos los faltantes por variable, tanto en cantidad como en porcentaje. " +
    "Esto permite evaluar qué variables están completas y considerar si los faltantes afectan " +
    "el análisis de demanda o variables contextuales."
)

# Calculo de datos faltantes
total_faltantes = df.isna().sum().sum()
total_no_faltantes = df.notna().sum().sum()

col1, col2 = st.columns(2)

# Grafico 1: valores faltantes vs no faltantes --
with col1:
    datos_pastel = pd.DataFrame({
        "Estado": ["Valores faltantes", "Valores no faltantes"],
        "Cantidad": [total_faltantes, total_no_faltantes]
    })

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

    fig1.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig1, use_container_width=True)
#---------------------------------------------------------
# Grafico 2: Valores faltantes por columna
with col2:
    faltantes_columna = df.isna().sum()
    faltantes_columna = faltantes_columna[faltantes_columna > 0]

    # Crear DataFrame y calcular el porcentaje del total de faltantes
    datos_columnas = pd.DataFrame({
        "Columna": faltantes_columna.index,
        "Cantidad de faltantes": faltantes_columna.values
    })

    total_faltantes = datos_columnas["Cantidad de faltantes"].sum()
    datos_columnas["Porcentaje del total"] = (
        datos_columnas["Cantidad de faltantes"] / total_faltantes * 100
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
#--------------------------------------------
st.subheader("Registros duplicados")
st.write(
    "Contaremos filas completamente idénticas, sin eliminarlas. Los duplicados exactos pueden inflar " +
    "los conteos de pasajeros si son errores de registro; aun así, primero hay que revisar su cantidad " +
    "y contexto antes de decidir qué hacer."
)

duplicados_exactos = df.duplicated().sum()
porcentaje_duplicados = (duplicados_exactos / len(df) * 100) if len(df) else 0
st.write(f"Filas completamente duplicadas: {duplicados_exactos:,}")
st.write(f"Porcentaje del dataset: {porcentaje_duplicados:.2f}%")

mascara_duplicados = df.duplicated(keep=False)
ejemplos_duplicados = df.loc[mascara_duplicados].drop_duplicates().head(5)
st.write(f"Filas que forman parte de grupos duplicados: {mascara_duplicados.sum():,}")
st.write(ejemplos_duplicados)

st.write("El conteo confirma **18 filas duplicadas exactas** (0,01 % al redondear a dos decimales). " +
         "La tabla muestra ejemplos de filas que aparecen más de una vez; en total, 36 filas participan "+ 
         "en esos pares. Como son idénticas en todas las columnas, podrían inflar agregaciones si " +
         "representan duplicaciones de registro. Conviene investigar su procedencia antes de eliminarlas, " +
         "pues el conteo por sí solo no explica cómo se generaron. Se conservan todas."
)

#-------------------------------------------
st.subheader("Rangos y categorías")
st.write("Comprobaremos condiciones básicas para variables cuyo dominio es interpretable —por ejemplo, meses " +
         "entre 1 y 12 y pasajeros no negativos— y revisaremos etiquetas categóricas con espacios o " +
         "diferencias de mayúsculas. Estas señales identifican valores para investigar; no corrigen ni descartan " +
         "registros."
)

columnas_numericas = df.select_dtypes(include="number").columns
st.write("Rangos observados en variables numéricas:")
st.write(df[columnas_numericas].agg(["min", "max"]).T)

# Validacion de meses
if "Mes" in df.columns:
    meses_invalidos = df.loc[~df["Mes"].between(1, 12), "Mes"]
    st.write(f"\n\nRegistros con Mes fuera de 1–12: {len(meses_invalidos):,}")
    if len(meses_invalidos):
        st.write("Valores observados:", sorted(meses_invalidos.dropna().unique().tolist()))

# Busqueda de columnas con pasajeros negativos
for columna in ["PASAJEROS", "Distancia"]:
    if columna in df.columns:
        cantidad_negativos = (df[columna] < 0).sum()
        st.write(f"Registros con {columna} negativo: {cantidad_negativos:,}")

columnas_categoricas = df.select_dtypes(include=["object", "string"]).columns
resumen_categorias = pd.DataFrame({
    "categorias_distintas": df[columnas_categoricas].nunique(dropna=True),
    "con_espacios_exteriores": pd.Series({
        col: df[col].dropna().astype(str).str.strip().ne(df[col].dropna().astype(str)).sum()
        for col in columnas_categoricas
    })
}, index=columnas_categoricas)

st.write("Resumen de categorías y etiquetas con espacios exteriores:")
st.write(resumen_categorias.sort_values("categorias_distintas", ascending=False))

# Busqueda de variantes
posibles_variantes = {}
for columna in columnas_categoricas:
    etiquetas = df[columna].dropna().astype(str)
    grupos = etiquetas.groupby(etiquetas.str.strip().str.upper()).unique()
    variantes = {etiqueta: valores.tolist() for etiqueta, valores in grupos.items() if len(valores) > 1}
    if variantes:
        posibles_variantes[columna] = variantes

if posibles_variantes:
    st.write("Etiquetas distintas que coinciden al ignorar espacios exteriores y mayúsculas:")
    for columna, variantes in posibles_variantes.items():
        st.write(f"{columna}: {variantes}")
else:
    st.write("No se han encontrado etiquetas distintas que coinciden al ignorar espacios exteriores y mayúsculas.")

# Busqueda de espacios exteriores
tabla_espacios = {"Columna": ["Operador", "ORIG_1_N", "DEST_2_N"], "Valor": [], "Frecuencia": [], 
         "Frecuencia del valor sin espacios": [
         ]
}

st.write("Valores con espacios exteriores y posibles categorías equivalentes tras quitar esos espacios:")
for columna in ["Operador", "ORIG_1_N", "DEST_2_N"]:
    if columna in df.columns:
        valores = df[columna].dropna().astype(str)
        con_espacios = valores[valores.str.strip().ne(valores)]
        for valor, frecuencia in con_espacios.value_counts().head(10).items():
            equivalente = valores[valores.eq(valor.strip())].shape[0]
            tabla_espacios["Valor"].append(valor)
            tabla_espacios["Frecuencia"].append(frecuencia)
            tabla_espacios["Frecuencia del valor sin espacios"].append(equivalente)

st.table(tabla_espacios, alt="Valores con espacios exteriores y posibles categorías equivalentes tras quitar esos espacios")

st.write("La inspección confirma **128 registros de `Operador`**, **2 de `ORIG_1_N`** y **2 de `DEST_2_N`** " +
         "con espacios exteriores. Los valores visibles son `JETSMART PERÚ ` y `TOCOPILLA/AD BARRILES / CHILE `. "+
         "En este archivo no aparece una categoría idéntica a la versión sin esos espacios (`JETSMART " +
         "PERÚ` o `TOCOPILLA/AD BARRILES / CHILE`), así que no se observó una división actual entre ambas " +
         "formas. Aun así, los espacios invisibles pueden dificultar filtros y coincidencias exactas; si hubiera " +
         "versiones equivalentes en otros datos, también podrían fragmentar conteos por operador, origen o destino. " +
         "No se normalizaron las etiquetas."
)
#-----------------------------
st.subheader("Revisión de valores negativos en CARGA (Ton)")
st.write("Aunque se espera revisar rangos, un valor negativo de carga requiere contexto. Contaremos estos " +
         "registros y mostraremos algunos campos asociados para investigar el caso sin asumir que sea un error " +
         "ni cambiar el dato."
)

negativos_carga = df["CARGA (Ton)"] < 0
columnas_contexto = ["Año", "Mes", "Operador", "ORIG_1", "DEST_1", "CARGA (Ton)", "CORREO", "PASAJEROS", "NAC"]
columnas_contexto = [col for col in columnas_contexto if col in df.columns]
st.write(f"Registros con CARGA (Ton) negativa: {negativos_carga.sum():,}")
st.write(df.loc[negativos_carga, columnas_contexto].head(10))

st.write("En los datos observados, el mínimo de `CARGA (Ton)` leído por pandas es **−1.726** (valor decimal) " +
         "y se encontró **1 registro negativo**. Corresponde a diciembre de 2024, LATAM CARGO, ruta SCL–BOG; " +
         "el registro muestra 0 pasajeros y 0 en `CORREO`. Esto merece revisión con la fuente o definición de " +
         "la variable, pero el signo no basta para concluir que sea un error. El dato se conserva."
)
#------------------------------

st.subheader("Revisión de valores altos en CORREO")
st.write("Inspeccionaremos los registros con mayores valores de `CORREO` junto con su contexto de ruta, " +
         "periodo, operador y pasajeros. La comparación ayuda a señalar valores que merecen verificación sin " +
         "clasificarlos automáticamente como erróneos."
)

columnas_correo = [col for col in ["Año", "Mes", "Operador", "ORIG_1", "DEST_1", "ORIG_1_N", "DEST_1_N", "CORREO", "CARGA (Ton)", "PASAJEROS", "NAC"] if col in df.columns]
st.write("Diez registros con mayor valor de CORREO:")
st.write(df.nlargest(10, "CORREO")[columnas_correo])

st.write("Los dos valores más altos de `CORREO` son **4.148.245.086** (AEROLINEAS ARGENTINAS, POA–SCL, " +
         "octubre de 2007) y **2.457.561.050** (AEROLINEAS ARGENTINAS, NYC–SCL, octubre de 2007); el tercer " +
         "valor es 635.589. Además, los dos registros máximos muestran 0 pasajeros. La diferencia de magnitud " +
         "justifica revisar unidades, codificación o fuente, pero no demuestra que los valores sean incorrectos. " +
         "No se modifican ni descartan."
)
#------------------------------
st.subheader("Posibles valores atípicos en PASAJEROS")

st.write("Como la demanda es la variable objetivo, cuantificaremos valores que superan el umbral superior del " +
         "rango intercuartílico (Q3 + 1.5 × RIC). Este criterio sirve para señalar observaciones extremas para " +
         "revisión; no implica que sean errores, especialmente en datos de demanda agregados."
)

q1 = df["PASAJEROS"].quantile(0.25)
q3 = df["PASAJEROS"].quantile(0.75)
ric = q3 - q1
umbral_inferior = q1 - 1.5 * ric
umbral_superior = q3 + 1.5 * ric

mascara_atipicos_superiores = df["PASAJEROS"] > umbral_superior
st.write(f"Umbral superior (Q3 + 1.5 × RIC): {umbral_superior:,.2f}")
st.write(f"Observaciones sobre el umbral superior: {mascara_atipicos_superiores.sum():,} ({mascara_atipicos_superiores.mean() * 100:.2f}%)")
st.write("\n\nResumen de PASAJEROS:")
lista_mascara_atipicos_superiores = (df["PASAJEROS"].describe().tolist())

st.table(
    {"Cantidad": [int(lista_mascara_atipicos_superiores[0])],
     "Media": [int(lista_mascara_atipicos_superiores[1])],
     "Desviación estandar": [lista_mascara_atipicos_superiores[2]],
     "Minimo": [int(lista_mascara_atipicos_superiores[3])],
     "25%": [int(lista_mascara_atipicos_superiores[4])],
     "50%": [int(lista_mascara_atipicos_superiores[5])],
     "75%": [int(lista_mascara_atipicos_superiores[6])],
     "Maximo": [int(lista_mascara_atipicos_superiores[7])],
     "Umbral superior": [umbral_superior],
     "Observaciones sobre el umbral superior": [mascara_atipicos_superiores.sum()],
     "%": [mascara_atipicos_superiores.mean() * 100]
     }
)

st.write("El criterio IQR identifica observaciones estadísticamente extremas, pero no demuestra que sean " +
         "errores. Parte de la variabilidad puede corresponder a diferencias reales entre rutas, operadores " +
         "y periodos. La distribución de `PASAJEROS` se estudiará con más detalle en la sección 2; por ahora " +
         "no se modifica ni descarta ningún registro."
)
#-----------------------------------
st.subheader("Cobertura temporal y geográfica")

st.write("Verificaremos los años y meses presentes y el alcance geográfico usando las variables de origen, " +
         "destino y país disponibles. Esto permite confirmar si el periodo descrito en el README coincide " +
         "con el archivo y si hay cobertura útil para comparar rutas nacionales e internacionales."
)

if "Año" in df.columns:
    st.write(f"Años observados: {df['Año'].min()}–{df['Año'].max()}")
    st.write(f"Cantidad de años distintos: {df['Año'].nunique()}")
if "Mes" in df.columns:
    st.write("Meses observados:", str(sorted(df["Mes"].dropna().unique().tolist())))

if {"ORIG_1", "DEST_1"}.issubset(df.columns):
    rutas_distintas = df[["ORIG_1", "DEST_1"]].drop_duplicates().shape[0]
    st.write(f"Pares origen-destino distintos: {rutas_distintas:,}")

tabla_cobertura = {
    "Columna": [],
    "Categorias distintas": [],
}

for columna in ["NAC", "ORIG_1", "DEST_1", "ORIG_1_PAIS", "DEST_1_PAIS"]:
    if columna in df.columns:
        tabla_cobertura["Columna"].append(columna)
        tabla_cobertura["Categorias distintas"].append(df[columna].nunique(dropna=True))

st.table(tabla_cobertura, alt="Tabla de cantidad de pares origen-destinos distintos")
#--------------------------------------

st.subheader("Combinaciones de año y mes sin registros")

st.write("Que aparezcan los 12 meses en el dataset no garantiza que cada año tenga observaciones " +
         "en todos ellos. Compararemos todas las combinaciones año-mes posibles entre el primer y el " +
         "último año observados con las combinaciones presentes en los datos."
)

periodo_anios = range(int(df["Año"].min()), int(df["Año"].max()) + 1)
combinaciones_esperadas = pd.MultiIndex.from_product([periodo_anios, range(1, 13)], names=["Año", "Mes"])
combinaciones_observadas = pd.MultiIndex.from_frame(df[["Año", "Mes"]].drop_duplicates())
meses_ausentes = combinaciones_esperadas.difference(combinaciones_observadas)
st.write(f"Combinaciones año-mes sin registros: {len(meses_ausentes):,}")
if len(meses_ausentes):
    st.write(meses_ausentes.to_frame(index=False))
else:
    st.write("No se encontraron meses ausentes dentro del periodo observado.")

st.write("La cobertura agregada de años y meses se verifica con esta tabla de combinaciones. Si existen " +
         "meses ausentes, podrían interrumpir series temporales y afectar comparaciones mensuales; su " +
         "ausencia también puede responder a la disponibilidad histórica del registro y debe considerarse " +
         "al interpretar tendencias. Si no aparecen combinaciones ausentes, eso confirma continuidad mensual " +
         "en el periodo evaluado, aunque no garantiza que cada ruta u operador tenga datos todos los meses."
)

#--------------------------------------------
st.subheader("Síntesis de estructura y calidad")

st.write("El archivo contiene **251.117 registros y 25 variables**, con cobertura observada entre **1984 y " +
         "2025**. Se encuentran los 12 meses y no se detectaron combinaciones año-mes ausentes en el periodo " +
         "observado."
)

st.write("La unidad de análisis corresponde a registros agregados de tráfico; origen, destino, " +
         "operador, periodo y `PASAJEROS` son relevantes para la pregunta del proyecto."
)

st.write("Se confirmaron **57.062 valores faltantes en `PAX_LIB` y 57.062 en `CORREO` (22,72 % en cada " +
         "variable)**. Esto limita análisis que dependan de esas variables y puede hacer que las muestras " +
         "analizadas difieran. No se imputaron datos. También se confirmaron **18 filas duplicadas exactas " +
         "(0,01 % del dataset)**; conviene revisar su procedencia e impacto potencial antes de decidir si son " +
         "duplicados de carga o registros legítimos repetidos."
)

st.write("En las etiquetas categóricas se detectaron **128 registros de `Operador`**, **2 de `ORIG_1_N`** y " +
         "**2 de `DEST_2_N`** con espacios exteriores."
)

st.write("La revisión de equivalencias indicará si hay versiones " +
         "sin espacios que colisionan al normalizarlas. Estos casos podrían fragmentar conteos por categoría " +
         "si se agrupan literalmente; no se aplicó `strip()` ni otra normalización."
)

st.write("En `CARGA (Ton)` se observó un valor negativo (mínimo aproximado **−1,726**) que requiere contexto; " +
         "el valor se conserva. Los valores máximos de `CORREO` también se señalaron para verificación " +
         "contextual."
)

st.write("El criterio IQR identificó **35.514 observaciones por encima del umbral superior " +
         "(14,14 %)**: son extremos estadísticos potenciales, no errores confirmados. Diferencias reales entre " +
         "rutas, operadores y periodos pueden explicar parte de esta variabilidad; su distribución se analizará " +
         "en la sección 2."
)

st.write("Quedan pendientes de justificación —sin aplicar cambios en esta etapa— la interpretación del valor " +
         "negativo de carga, los valores muy altos de correo, el origen e impacto de las filas duplicadas y el " +
         "tratamiento futuro de las etiquetas con espacios. Los recuentos y conclusiones deben contrastarse con " +
         "las salidas de las celdas de esta sección antes de tomar decisiones de limpieza."
)