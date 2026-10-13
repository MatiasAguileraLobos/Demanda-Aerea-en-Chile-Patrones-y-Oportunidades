import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_clean_data


def formato_numero(valor: float, decimales: int = 0) -> str:
    """Formatea números con separadores usados habitualmente en español."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


# Navegación compartida con el resto de la aplicación.
st.sidebar.page_link("app.py", label="Inicio")
st.sidebar.page_link("pages/1_Contexto.py", label="Contexto y Datos")
st.sidebar.page_link("pages/2_EDA.py", label="EDA")
st.sidebar.page_link("pages/3_Analisis.py", label="Análisis")

st.title("Análisis exploratorio de datos")
st.write(
    "Exploraremos cómo se distribuyen los pasajeros registrados y cómo varían sus "
    "cantidades entre rutas, operadores, tipos de tráfico y distancias. Las observaciones "
    "son registros agregados por ruta, operador y periodo; no corresponden necesariamente "
    "a vuelos individuales. Las comparaciones son descriptivas y no establecen causalidad."
)

# La página trabaja exclusivamente con el dataset preparado.
df = load_clean_data()
columnas_requeridas = {
    "PASAJEROS", "NAC", "Año", "Operador", "ORIG_1", "DEST_1", "Distancia"
}
columnas_ausentes = columnas_requeridas.difference(df.columns)
if columnas_ausentes:
    st.error(
        "No se puede ejecutar el análisis: faltan columnas necesarias en el dataset "
        f"preparado ({', '.join(sorted(columnas_ausentes))})."
    )
    st.stop()

tipos_trafico = sorted(df["NAC"].dropna().unique().tolist())
año_min = int(df["Año"].min())
año_max = int(df["Año"].max())


# -----------------------------------------------------------------------------
# 1. Distribución de pasajeros
# -----------------------------------------------------------------------------
st.header("1. Distribución de pasajeros")
st.markdown(
    "El histograma resume la frecuencia de registros en distintos rangos de `PASAJEROS`. "
    "Se conservan las observaciones con cero pasajeros y los valores altos; las métricas "
    "se calculan en la escala original."
)

col_bins, col_escala = st.columns([1, 1])
with col_bins:
    cantidad_intervalos = st.slider(
        "Intervalos del histograma", min_value=10, max_value=100, value=50, step=5,
        key="eda_hist_bins"
    )
with col_escala:
    escala_histograma = st.radio(
        "Escala de visualización", options=["Original", "log1p"], horizontal=True,
        key="eda_hist_scale",
        help="log1p representa log(1 + pasajeros), mantiene los ceros en cero y comprime la cola alta."
    )

pasajeros = df["PASAJEROS"].dropna()
media_pasajeros = float(pasajeros.mean())
mediana_pasajeros = float(pasajeros.median())
percentil_90_pasajeros = float(pasajeros.quantile(0.90))
cantidad_ceros = int(pasajeros.eq(0).sum())
porcentaje_ceros = cantidad_ceros / len(pasajeros) * 100 if len(pasajeros) else 0.0

metricas_pasajeros = st.columns(3)
metricas_pasajeros[0].metric("Media por registro", formato_numero(media_pasajeros))
metricas_pasajeros[1].metric("Mediana", formato_numero(mediana_pasajeros))
metricas_pasajeros[2].metric("Percentil 90", formato_numero(percentil_90_pasajeros))

if escala_histograma == "log1p":
    datos_histograma = pd.DataFrame({"log(1 + PASAJEROS)": np.log1p(pasajeros)})
    columna_histograma = "log(1 + PASAJEROS)"
    etiqueta_histograma = "log(1 + pasajeros por registro)"
    titulo_histograma = "Distribución de pasajeros por registro (escala log1p)"
else:
    datos_histograma = pd.DataFrame({"PASAJEROS": pasajeros})
    columna_histograma = "PASAJEROS"
    etiqueta_histograma = "Pasajeros por registro"
    titulo_histograma = "Distribución de pasajeros por registro (escala original)"

fig_histograma = px.histogram(
    datos_histograma,
    x=columna_histograma,
    nbins=cantidad_intervalos,
    title=titulo_histograma,
    labels={columna_histograma: etiqueta_histograma, "count": "Registros"},
    color_discrete_sequence=["#3B82A0"],
)
fig_histograma.update_layout(
    xaxis_title=etiqueta_histograma,
    yaxis_title="Cantidad de registros",
    bargap=0.06,
    margin=dict(t=70, l=45, r=25, b=55),
)
fig_histograma.update_traces(
    hovertemplate=f"{etiqueta_histograma}: %{{x:,.2f}}<br>Registros: %{{y:,.0f}}<extra></extra>"
)
st.plotly_chart(fig_histograma, use_container_width=True)

if media_pasajeros > mediana_pasajeros:
    lectura_forma = (
        f"La media ({formato_numero(media_pasajeros)}) supera la mediana "
        f"({formato_numero(mediana_pasajeros)}), consistente con una distribución "
        "asimétrica hacia cantidades altas."
    )
elif media_pasajeros < mediana_pasajeros:
    lectura_forma = (
        f"La media ({formato_numero(media_pasajeros)}) es menor que la mediana "
        f"({formato_numero(mediana_pasajeros)}); la forma debe interpretarse junto "
        "con el histograma y los demás cuantiles."
    )
else:
    lectura_forma = "La media y la mediana coinciden; por sí solas no indican asimetría."
st.caption(
    f"{lectura_forma} {formato_numero(cantidad_ceros)} registros "
    f"({formato_numero(porcentaje_ceros, 2)} %) tienen cero pasajeros. Esos ceros "
    "son parte de la distribución observada y se conservan: el análisis describe cómo "
    "se reparte la demanda registrada entre observaciones agregadas."
)
if escala_histograma == "log1p":
    st.caption(
        "La escala horizontal muestra log(1 + PASAJEROS), no cantidades en unidades "
        "originales. La transformación conserva el cero en cero y no cambia los datos; "
        "las métricas se mantienen en pasajeros."
    )


# -----------------------------------------------------------------------------
# 2. Frecuencia de categorías
# -----------------------------------------------------------------------------
st.header("2. Frecuencia de operadores, orígenes, destinos y rutas")
st.markdown(
    "La frecuencia cuenta registros por categoría en todo el periodo disponible. "
    "Permite conocer qué operadores, puntos de origen, destinos o tramos aparecen "
    "más en el archivo; no mide pasajeros acumulados ni vuelos individuales."
)

col_categoria, col_topn_frecuencia = st.columns([1, 1])
with col_categoria:
    dimension_frecuencia = st.selectbox(
        "Categoría para contar", options=["Operador", "Origen", "Destino", "Ruta direccional"],
        key="eda_frequency_dimension"
    )
with col_topn_frecuencia:
    top_n_frecuencia = st.slider(
        "Categorías a mostrar (Top N)", min_value=5, max_value=30, value=10,
        key="eda_frequency_topn"
    )

if dimension_frecuencia == "Operador":
    frecuencia = df["Operador"].value_counts(dropna=True).rename_axis("Categoría").reset_index(name="Registros")
elif dimension_frecuencia == "Origen":
    frecuencia = df["ORIG_1"].value_counts(dropna=True).rename_axis("Categoría").reset_index(name="Registros")
elif dimension_frecuencia == "Destino":
    frecuencia = df["DEST_1"].value_counts(dropna=True).rename_axis("Categoría").reset_index(name="Registros")
else:
    pares_ruta = df.dropna(subset=["ORIG_1", "DEST_1"])
    frecuencia = (
        pares_ruta.groupby(["ORIG_1", "DEST_1"], observed=True)
        .size()
        .rename("Registros")
        .reset_index()
    )
    frecuencia["Categoría"] = frecuencia["ORIG_1"] + " → " + frecuencia["DEST_1"]
    frecuencia = frecuencia[["Categoría", "Registros"]]

if frecuencia.empty:
    st.info("No hay categorías disponibles para mostrar.")
else:
    top_frecuencia = frecuencia.nlargest(top_n_frecuencia, "Registros").sort_values("Registros")
    fig_frecuencia = px.bar(
        top_frecuencia,
        x="Registros",
        y="Categoría",
        orientation="h",
        text=top_frecuencia["Registros"].map(formato_numero),
        title=f"Categorías con más registros: {dimension_frecuencia.lower()}",
        labels={"Categoría": dimension_frecuencia, "Registros": "Cantidad de registros"},
        color_discrete_sequence=["#3B82A0"],
    )
    fig_frecuencia.update_traces(
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>Registros: %{x:,.0f}<extra></extra>"
    )
    fig_frecuencia.update_yaxes(
        categoryorder="array", categoryarray=top_frecuencia["Categoría"].tolist()
    )
    fig_frecuencia.update_layout(
        xaxis_title="Cantidad de registros",
        yaxis_title=dimension_frecuencia,
        margin=dict(t=70, l=45, r=45, b=55),
    )
    st.plotly_chart(fig_frecuencia, use_container_width=True)
    categoria_mas_frecuente = top_frecuencia.iloc[-1]
    st.caption(
        f"En el conjunto completo, {categoria_mas_frecuente['Categoría']} es la categoría "
        f"más frecuente entre las mostradas ({formato_numero(categoria_mas_frecuente['Registros'])} "
        "registros). Esta frecuencia describe su representación en el dataset, no su "
        "demanda de pasajeros; para eso se usa la suma de `PASAJEROS`."
    )
if dimension_frecuencia == "Ruta direccional":
    st.caption(
        "Las rutas se construyen con `ORIG_1` → `DEST_1`; se mantiene el sentido del tramo. "
        "No se mezclan los campos `_1` y `_2` ni se combinan direcciones opuestas."
    )


# -----------------------------------------------------------------------------
# 3. Comparación por tipo de tráfico
# -----------------------------------------------------------------------------
st.header("3. Comparación entre tráfico nacional e internacional")
st.markdown(
    "Comparamos pasajeros por registro. Como la distribución es asimétrica y contiene "
    "ceros, el boxplot representa el eje vertical como log(1 + PASAJEROS): el cero se "
    "mantiene en cero y la cola alta se comprime. La tabla y la interpretación muestran "
    "estadísticas en la escala original."
)

col_anios_tipo, col_tipos_tipo = st.columns([1, 1])
with col_anios_tipo:
    rango_anios_tipo = st.slider(
        "Rango de años", min_value=año_min, max_value=año_max,
        value=(año_min, año_max), key="eda_box_years"
    )
with col_tipos_tipo:
    seleccion_tipos_tipo = st.multiselect(
        "Tipo de tráfico", options=tipos_trafico, default=tipos_trafico,
        key="eda_box_traffic"
    )

datos_tipo = df.loc[
    df["Año"].between(rango_anios_tipo[0], rango_anios_tipo[1])
    & df["NAC"].isin(seleccion_tipos_tipo)
].copy()

if datos_tipo.empty:
    st.info("La selección no contiene registros. Amplía el rango o selecciona un tipo de tráfico.")
else:
    datos_tipo["log1p(PASAJEROS)"] = np.log1p(datos_tipo["PASAJEROS"])
    orden_tipos = [tipo for tipo in tipos_trafico if tipo in seleccion_tipos_tipo]
    fig_boxplot = px.box(
        datos_tipo,
        x="NAC",
        y="log1p(PASAJEROS)",
        category_orders={"NAC": orden_tipos},
        points=False,
        title=f"Distribución por tipo de tráfico ({rango_anios_tipo[0]}–{rango_anios_tipo[1]})",
        labels={"NAC": "Tipo de tráfico", "log1p(PASAJEROS)": "log(1 + pasajeros por registro)"},
        color="NAC",
        color_discrete_sequence=["#3B82A0", "#E28E4A"],
        custom_data=["PASAJEROS"],
    )
    valores_eje_box = [0, 1, 10, 100, 1_000, 10_000, 50_000]
    fig_boxplot.update_yaxes(
        tickmode="array",
        tickvals=np.log1p(valores_eje_box),
        ticktext=[formato_numero(valor) for valor in valores_eje_box],
        title="Pasajeros por registro (etiquetas originales; caja en escala log1p)",
    )
    fig_boxplot.update_layout(
        xaxis_title="Tipo de tráfico",
        showlegend=False,
        margin=dict(t=70, l=45, r=25, b=50),
    )
    fig_boxplot.update_traces(
        hovertemplate=(
            "Tipo: %{x}<br>log(1 + pasajeros): %{y:.3f}"
            "<br>Pasajeros por registro: %{customdata[0]:,.0f}<extra></extra>"
        )
    )
    st.plotly_chart(fig_boxplot, use_container_width=True)

    estadisticas_tipo = (
        datos_tipo.groupby("NAC", observed=True)
        .agg(
            Registros=("PASAJEROS", "size"),
            Media=("PASAJEROS", "mean"),
            Mediana=("PASAJEROS", "median"),
            Q1=("PASAJEROS", lambda serie: serie.quantile(0.25)),
            Q3=("PASAJEROS", lambda serie: serie.quantile(0.75)),
            Ceros_pct=("PASAJEROS", lambda serie: serie.eq(0).mean() * 100),
        )
        .reindex(orden_tipos)
        .dropna(how="all")
    )
    estadisticas_tipo["IQR"] = estadisticas_tipo["Q3"] - estadisticas_tipo["Q1"]
    tabla_tipo = estadisticas_tipo.rename_axis("Tipo de tráfico").reset_index()
    for columna in ["Media", "Mediana", "Q1", "Q3", "IQR"]:
        tabla_tipo[columna] = tabla_tipo[columna].map(formato_numero)
    tabla_tipo["Registros"] = tabla_tipo["Registros"].map(formato_numero)
    tabla_tipo["Ceros (%)"] = tabla_tipo.pop("Ceros_pct").map(lambda valor: formato_numero(valor, 2) + " %")
    tabla_tipo = tabla_tipo.rename(columns={
        "Media": "Media pasajeros", "IQR": "Rango intercuartílico"
    })
    st.markdown("**Estadísticas en la escala original**")
    st.dataframe(tabla_tipo, hide_index=True, use_container_width=True)

    medianas_tipo = estadisticas_tipo["Mediana"].dropna()
    if len(medianas_tipo) >= 2:
        mayor, menor = medianas_tipo.idxmax(), medianas_tipo.idxmin()
        if mayor != menor:
            iqr_mayor = estadisticas_tipo.loc[mayor, "IQR"]
            iqr_menor = estadisticas_tipo.loc[menor, "IQR"]
            if iqr_mayor > iqr_menor:
                lectura_dispersion = f"El IQR también es mayor en {mayor}."
            elif iqr_mayor < iqr_menor:
                lectura_dispersion = f"El IQR también es mayor en {menor}."
            else:
                lectura_dispersion = "Los IQR de ambos grupos son iguales."
            st.caption(
                f"Con estos filtros, la mediana por registro es mayor en {mayor} "
                f"({formato_numero(medianas_tipo[mayor])}) que en {menor} "
                f"({formato_numero(medianas_tipo[menor])}). {lectura_dispersion} "
                "Esto describe los registros seleccionados, no una diferencia causal entre tráficos."
            )
        else:
            st.caption("Los grupos seleccionados tienen la misma mediana por registro.")
    else:
        tipo = medianas_tipo.index[0]
        porcentaje_ceros_tipo = estadisticas_tipo.loc[tipo, "Ceros_pct"]
        st.caption(
            f"Para {tipo}, la mediana es {formato_numero(medianas_tipo.iloc[0])} pasajeros por registro; "
            f"{formato_numero(porcentaje_ceros_tipo, 2)} % de sus registros tienen cero pasajeros. "
            "Selecciona ambos tipos para compararlos."
        )
    st.caption(
        "Se comparan registros agregados de tráfico, no pasajeros individuales ni necesariamente "
        "vuelos individuales. El eje log1p facilita la lectura sin excluir registros con cero."
    )


# -----------------------------------------------------------------------------
# 4. Distribución de distancias
# -----------------------------------------------------------------------------
st.header("4. Distribución de distancias")
st.markdown(
    "La distancia describe una característica registrada del tramo. El histograma y "
    "los cuantiles permiten examinar su centro, dispersión y posible cola alta; se usa "
    "una etiqueta neutral, sin asignar una unidad no verificada."
)

col_bins_distancia, col_escala_distancia = st.columns([1, 1])
with col_bins_distancia:
    intervalos_distancia = st.slider(
        "Intervalos para Distancia", min_value=10, max_value=100, value=50, step=5,
        key="eda_distance_bins"
    )
with col_escala_distancia:
    escala_distancia = st.radio(
        "Escala para Distancia", options=["Original", "log1p"], horizontal=True,
        key="eda_distance_scale"
    )

distancia = df["Distancia"].dropna()
media_distancia = float(distancia.mean())
mediana_distancia = float(distancia.median())
q1_distancia = float(distancia.quantile(0.25))
q3_distancia = float(distancia.quantile(0.75))
iqr_distancia = q3_distancia - q1_distancia
limite_iqr_distancia = q3_distancia + 1.5 * iqr_distancia
extremos_distancia = int(distancia.gt(limite_iqr_distancia).sum())

metricas_distancia = st.columns(3)
metricas_distancia[0].metric("Mediana", formato_numero(mediana_distancia))
metricas_distancia[1].metric("Media", formato_numero(media_distancia, 2))
metricas_distancia[2].metric("Rango intercuartílico", formato_numero(iqr_distancia))

if escala_distancia == "log1p":
    datos_distancia = pd.DataFrame({"log(1 + Distancia)": np.log1p(distancia)})
    columna_distancia = "log(1 + Distancia)"
    etiqueta_distancia = "log(1 + distancia registrada)"
else:
    datos_distancia = pd.DataFrame({"Distancia": distancia})
    columna_distancia = "Distancia"
    etiqueta_distancia = "Distancia registrada"

fig_distancia = px.histogram(
    datos_distancia,
    x=columna_distancia,
    nbins=intervalos_distancia,
    title=f"Distribución de {etiqueta_distancia.lower()}",
    labels={columna_distancia: etiqueta_distancia, "count": "Registros"},
    color_discrete_sequence=["#4C956C"],
)
fig_distancia.update_layout(
    xaxis_title=etiqueta_distancia,
    yaxis_title="Cantidad de registros",
    bargap=0.06,
    margin=dict(t=70, l=45, r=25, b=55),
)
st.plotly_chart(fig_distancia, use_container_width=True)

if media_distancia > mediana_distancia:
    lectura_distancia = "La media supera la mediana, compatible con una cola hacia distancias registradas mayores."
elif media_distancia < mediana_distancia:
    lectura_distancia = "La media es menor que la mediana; revisa el histograma para caracterizar la forma."
else:
    lectura_distancia = "La media y la mediana coinciden; estos estadísticos no bastan para describir la forma."
st.caption(
    f"{lectura_distancia} El 50 % central abarca {formato_numero(q1_distancia)}–"
    f"{formato_numero(q3_distancia)} (IQR {formato_numero(iqr_distancia)}). "
    f"La regla exploratoria Q3 + 1,5 × IQR marca {formato_numero(extremos_distancia)} "
    "observaciones por encima del umbral; son extremos estadísticos potenciales, no errores confirmados."
)
if escala_distancia == "log1p":
    st.caption("La escala log1p se usa solo para mostrar el histograma; los estadísticos siguen en la escala original.")


# -----------------------------------------------------------------------------
# 5. Relaciones entre variables
# -----------------------------------------------------------------------------
st.header("5. Relaciones entre distancia, pasajeros y operadores")
st.markdown(
    "Estas comparaciones relacionan la cantidad de pasajeros registrada con una medida "
    "del tramo y con las categorías de operador. Una asociación o diferencia observada "
    "no permite atribuir causas."
)

st.subheader("Distancia y pasajeros por registro")
st.markdown(
    "El dispersograma usa una muestra aleatoria reproducible para facilitar la lectura. "
    "La correlación de Pearson se calcula sobre todos los registros que cumplen los filtros, "
    "en las unidades originales de ambas variables."
)

col_anios_relacion, col_tipos_relacion = st.columns([1, 1])
with col_anios_relacion:
    rango_anios_relacion = st.slider(
        "Rango de años", min_value=año_min, max_value=año_max,
        value=(año_min, año_max), key="eda_relation_years"
    )
with col_tipos_relacion:
    seleccion_tipos_relacion = st.multiselect(
        "Tipo de tráfico", options=tipos_trafico, default=tipos_trafico,
        key="eda_relation_traffic"
    )

datos_relacion = df.loc[
    df["Año"].between(rango_anios_relacion[0], rango_anios_relacion[1])
    & df["NAC"].isin(seleccion_tipos_relacion),
    ["Distancia", "PASAJEROS", "NAC"]
].dropna().copy()

if datos_relacion.empty:
    st.info("La selección no contiene registros para relacionar Distancia y PASAJEROS.")
else:
    correlacion = datos_relacion["Distancia"].corr(datos_relacion["PASAJEROS"], method="pearson")
    cantidad_muestra = min(15_000, len(datos_relacion))
    muestra = datos_relacion.sample(n=cantidad_muestra, random_state=42)
    muestra["log1p(PASAJEROS)"] = np.log1p(muestra["PASAJEROS"])

    metrica_correlacion, metrica_muestra = st.columns(2)
    metrica_correlacion.metric(
        "Correlación de Pearson (escala original)",
        "No disponible" if pd.isna(correlacion) else formato_numero(correlacion, 3)
    )
    metrica_muestra.metric(
        "Puntos mostrados", f"{formato_numero(cantidad_muestra)} de {formato_numero(len(datos_relacion))}"
    )

    fig_dispersion = px.scatter(
        muestra,
        x="Distancia",
        y="log1p(PASAJEROS)",
        color="NAC" if len(seleccion_tipos_relacion) > 1 else None,
        opacity=0.35,
        title="Distancia registrada y pasajeros por observación (muestra reproducible)",
        labels={
            "Distancia": "Distancia registrada",
            "log1p(PASAJEROS)": "log(1 + pasajeros por registro)",
            "NAC": "Tipo de tráfico",
        },
        color_discrete_sequence=["#3B82A0", "#E28E4A"],
    )
    ticks_pasajeros = [0, 1, 10, 100, 1_000, 10_000, 50_000]
    fig_dispersion.update_yaxes(
        tickmode="array",
        tickvals=np.log1p(ticks_pasajeros),
        ticktext=[formato_numero(valor) for valor in ticks_pasajeros],
        title="Pasajeros por registro (etiquetas originales; eje log1p)",
    )
    fig_dispersion.update_traces(
        hovertemplate=(
            "Distancia registrada: %{x:,.0f}<br>log(1 + pasajeros): %{y:.3f}"
            "<extra></extra>"
        )
    )
    fig_dispersion.update_layout(margin=dict(t=70, l=45, r=25, b=55))
    st.plotly_chart(fig_dispersion, use_container_width=True)

    if pd.isna(correlacion):
        st.caption(
            "No se pudo calcular Pearson porque una de las variables no presenta variación "
            "en los registros filtrados."
        )
    else:
        if abs(correlacion) < 0.1:
            intensidad = "muy débil"
        elif abs(correlacion) < 0.3:
            intensidad = "débil"
        elif abs(correlacion) < 0.5:
            intensidad = "moderada"
        else:
            intensidad = "marcada"
        sentido = "positiva" if correlacion > 0 else "negativa" if correlacion < 0 else "nula"
        st.caption(
            f"En los registros filtrados, la asociación lineal es {sentido} y {intensidad} "
            f"(r = {formato_numero(correlacion, 3)}). Pearson resume solo una asociación "
            "lineal y puede verse influida por asimetrías y valores extremos; no demuestra "
            "que la distancia cause cambios en pasajeros. El gráfico muestra una muestra "
            f"reproducible de {formato_numero(cantidad_muestra)} registros; la correlación usa "
            "todos los registros filtrados."
        )

st.subheader("Pasajeros acumulados por operador o ruta")
st.markdown(
    "La suma de `PASAJEROS` responde dónde se concentra el volumen registrado en el "
    "periodo filtrado. El total puede depender tanto de los pasajeros por registro como "
    "de la cantidad de observaciones y la cobertura temporal de cada categoría."
)

col_dimension, col_topn = st.columns([1, 1])
with col_dimension:
    dimension_acumulado = st.radio(
        "Agrupar el total por", options=["Operador", "Ruta direccional"], horizontal=True,
        key="eda_bar_dimension"
    )
with col_topn:
    top_n_acumulado = st.slider(
        "Categorías acumuladas a mostrar (Top N)", min_value=5, max_value=30, value=10,
        key="eda_bar_topn"
    )

col_anios_acumulado, col_tipos_acumulado = st.columns([1, 1])
with col_anios_acumulado:
    rango_anios_acumulado = st.slider(
        "Rango de años", min_value=año_min, max_value=año_max,
        value=(año_min, año_max), key="eda_bar_years"
    )
with col_tipos_acumulado:
    seleccion_tipos_acumulado = st.multiselect(
        "Tipo de tráfico", options=tipos_trafico, default=tipos_trafico,
        key="eda_bar_traffic"
    )

datos_acumulados = df.loc[
    df["Año"].between(rango_anios_acumulado[0], rango_anios_acumulado[1])
    & df["NAC"].isin(seleccion_tipos_acumulado)
].copy()

if dimension_acumulado == "Operador":
    datos_acumulados = datos_acumulados.dropna(subset=["Operador"])
    acumulados = (
        datos_acumulados.groupby("Operador", observed=True)["PASAJEROS"]
        .agg(Pasajeros_acumulados="sum", Registros="size")
        .reset_index()
        .rename(columns={"Operador": "Categoría", "Pasajeros_acumulados": "Pasajeros acumulados"})
    )
    nombre_dimension = "operador"
else:
    datos_acumulados = datos_acumulados.dropna(subset=["ORIG_1", "DEST_1"])
    datos_acumulados["Ruta direccional"] = datos_acumulados["ORIG_1"] + " → " + datos_acumulados["DEST_1"]
    acumulados = (
        datos_acumulados.groupby("Ruta direccional", observed=True)["PASAJEROS"]
        .agg(Pasajeros_acumulados="sum", Registros="size")
        .reset_index()
        .rename(columns={"Ruta direccional": "Categoría", "Pasajeros_acumulados": "Pasajeros acumulados"})
    )
    nombre_dimension = "ruta direccional"

if acumulados.empty:
    st.info("La selección no contiene registros para calcular pasajeros acumulados.")
else:
    top_acumulados = (
        acumulados.nlargest(top_n_acumulado, "Pasajeros acumulados")
        .sort_values("Pasajeros acumulados", ascending=True)
        .copy()
    )
    orden_acumulados = top_acumulados["Categoría"].tolist()
    fig_acumulados = px.bar(
        top_acumulados,
        x="Pasajeros acumulados",
        y="Categoría",
        orientation="h",
        text=top_acumulados["Pasajeros acumulados"].map(formato_numero),
        title=(
            f"Top {len(top_acumulados)} {nombre_dimension} por pasajeros acumulados "
            f"({rango_anios_acumulado[0]}–{rango_anios_acumulado[1]})"
        ),
        labels={"Categoría": dimension_acumulado, "Pasajeros acumulados": "Pasajeros acumulados"},
        color_discrete_sequence=["#3B82A0"],
        custom_data=["Registros"],
    )
    fig_acumulados.update_traces(
        textposition="outside", cliponaxis=False,
        hovertemplate=(
            "%{y}<br>Pasajeros acumulados: %{x:,.0f}"
            "<br>Registros: %{customdata[0]:,.0f}<extra></extra>"
        )
    )
    fig_acumulados.update_yaxes(categoryorder="array", categoryarray=orden_acumulados)
    fig_acumulados.update_layout(
        xaxis_title="Pasajeros acumulados en los registros",
        yaxis_title=dimension_acumulado,
        margin=dict(t=75, l=45, r=50, b=55),
    )
    st.plotly_chart(fig_acumulados, use_container_width=True)

    lider_acumulado = top_acumulados.iloc[-1]
    st.caption(
        f"Con estos filtros, {lider_acumulado['Categoría']} tiene el mayor acumulado entre "
        f"las categorías mostradas ({formato_numero(lider_acumulado['Pasajeros acumulados'])} pasajeros) "
        f"en {formato_numero(lider_acumulado['Registros'])} registros. Este total no equivale "
        "a pasajeros únicos, vuelos individuales, eficiencia ni popularidad."
    )

    if dimension_acumulado == "Operador":
        mostrar_distribuciones = st.checkbox(
            "Comparar también la distribución de pasajeros por registro entre estos operadores",
            value=False,
            key="eda_operator_box_toggle",
        )
        if mostrar_distribuciones:
            operadores_top = top_acumulados["Categoría"].tolist()
            datos_operadores_top = datos_acumulados.loc[
                datos_acumulados["Operador"].isin(operadores_top)
            ].copy()
            datos_operadores_top["log1p(PASAJEROS)"] = np.log1p(datos_operadores_top["PASAJEROS"])
            fig_operadores_box = px.box(
                datos_operadores_top,
                x="log1p(PASAJEROS)",
                y="Operador",
                category_orders={"Operador": operadores_top[::-1]},
                points=False,
                title="Distribución de pasajeros por registro en los operadores seleccionados",
                labels={"Operador": "Operador", "log1p(PASAJEROS)": "log(1 + pasajeros por registro)"},
                color="Operador",
                color_discrete_sequence=px.colors.qualitative.Safe,
                custom_data=["PASAJEROS"],
            )
            fig_operadores_box.update_xaxes(
                tickmode="array",
                tickvals=np.log1p([0, 1, 10, 100, 1_000, 10_000, 50_000]),
                ticktext=["0", "1", "10", "100", "1.000", "10.000", "50.000"],
                title="Pasajeros por registro (etiquetas originales; eje log1p)",
            )
            fig_operadores_box.update_traces(
                hovertemplate=(
                    "%{y}<br>log(1 + pasajeros): %{x:.3f}"
                    "<br>Pasajeros por registro: %{customdata[0]:,.0f}<extra></extra>"
                )
            )
            fig_operadores_box.update_layout(
                showlegend=False, margin=dict(t=75, l=45, r=25, b=55)
            )
            st.plotly_chart(fig_operadores_box, use_container_width=True)
            resumen_operadores = (
                datos_operadores_top.groupby("Operador", observed=True)
                .agg(
                    Registros=("PASAJEROS", "size"),
                    Mediana_por_registro=("PASAJEROS", "median"),
                    Ceros_pct=("PASAJEROS", lambda serie: serie.eq(0).mean() * 100),
                )
                .reindex(operadores_top)
            )
            if len(resumen_operadores) >= 2:
                medianas_operadores = resumen_operadores["Mediana_por_registro"].dropna()
                op_mayor, op_menor = medianas_operadores.idxmax(), medianas_operadores.idxmin()
                if op_mayor != op_menor:
                    st.caption(
                        f"Entre los operadores mostrados, la mediana por registro más alta es la de "
                        f"{op_mayor} ({formato_numero(medianas_operadores[op_mayor])}) y la más baja "
                        f"la de {op_menor} ({formato_numero(medianas_operadores[op_menor])}). "
                        "Este resumen complementa los acumulados; cada operador puede tener distinta "
                        "cantidad de registros y cobertura temporal."
                    )
