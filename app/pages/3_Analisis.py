import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_clean_data


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def formato_numero(valor: float, decimales: int = 0) -> str:
    """Formatea cantidades con separadores usados habitualmente en español."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def etiqueta_periodo(periodo, granularidad: str) -> str:
    if granularidad == "Anual":
        return str(int(periodo))
    return f"{MESES[periodo.month - 1]} {periodo.year}"


# Navegación compartida con el resto de la aplicación.
st.sidebar.page_link("app.py", label="Inicio")
st.sidebar.page_link("pages/1_Contexto.py", label="Contexto y Datos")
st.sidebar.page_link("pages/2_EDA.py", label="EDA")
st.sidebar.page_link("pages/3_Analisis.py", label="Análisis")

st.title("Análisis de la pregunta de investigación")
st.write(
    "¿Qué hemos aprendido hasta ahora sobre la variación de la demanda registrada "
    "por ruta, aerolínea, tipo de tráfico y mes? Esta página conecta los patrones "
    "explorados en el EDA con la evolución temporal y la concentración de pasajeros."
)
st.info(
    "Las cifras de pasajeros corresponden a sumas de `PASAJEROS` en registros agregados "
    "por ruta, operador y periodo. No representan pasajeros únicos ni vuelos individuales."
)

df = load_clean_data()
columnas_requeridas = {"Año", "Mes", "PASAJEROS", "NAC", "Operador", "ORIG_1", "DEST_1"}
columnas_ausentes = columnas_requeridas.difference(df.columns)
if columnas_ausentes:
    st.error(
        "No se puede ejecutar el análisis: faltan columnas necesarias en el dataset "
        f"preparado ({', '.join(sorted(columnas_ausentes))})."
    )
    st.stop()

año_min = int(df["Año"].min())
año_max = int(df["Año"].max())
tipos_trafico = sorted(df["NAC"].dropna().unique().tolist())


# -----------------------------------------------------------------------------
# 1. Evolución temporal
# -----------------------------------------------------------------------------
st.header("1. Evolución del volumen de pasajeros")
st.markdown(
    "¿Cómo cambia la suma de pasajeros registrados a través del tiempo? Elige el "
    "periodo, el tipo de tráfico y la granularidad. La línea incluye los totales por "
    "periodo; el cursor muestra también cuántos registros aportan a cada punto."
)

col_rango_tiempo, col_tipo_tiempo, col_granularidad = st.columns([1.25, 1.25, 1])
with col_rango_tiempo:
    rango_tiempo = st.slider(
        "Periodo para evolución y estacionalidad",
        min_value=año_min,
        max_value=año_max,
        value=(año_min, año_max),
        key="analysis_time_years",
    )
with col_tipo_tiempo:
    tipos_tiempo = st.multiselect(
        "Tipo de tráfico",
        options=tipos_trafico,
        default=tipos_trafico,
        key="analysis_time_traffic",
    )
with col_granularidad:
    granularidad = st.radio(
        "Granularidad",
        options=["Anual", "Mensual"],
        horizontal=True,
        key="analysis_time_granularity",
    )

datos_temporales = df.loc[
    df["Año"].between(rango_tiempo[0], rango_tiempo[1])
    & df["NAC"].isin(tipos_tiempo)
].copy()

texto_evolucion = "No hay registros para describir la evolución con los filtros seleccionados."
texto_estacionalidad = "No hay registros para describir los patrones mensuales con los filtros seleccionados."
resumen_evolucion = texto_evolucion
resumen_mensual = texto_estacionalidad
matriz_pasajeros = pd.DataFrame()
matriz_registros = pd.DataFrame()
matriz_porcentual = pd.DataFrame()

if datos_temporales.empty:
    st.info("La selección no contiene registros. Amplía el periodo o selecciona al menos un tipo de tráfico.")
else:
    if granularidad == "Anual":
        datos_temporales["Periodo"] = datos_temporales["Año"].astype(int)
        periodos_completos = list(range(rango_tiempo[0], rango_tiempo[1] + 1))
        formato_hover_periodo = "%{x:.0f}"
    else:
        datos_temporales["Periodo"] = pd.to_datetime(
            {"year": datos_temporales["Año"], "month": datos_temporales["Mes"], "day": 1}
        )
        periodos_completos = pd.date_range(
            start=f"{rango_tiempo[0]}-01-01",
            end=f"{rango_tiempo[1]}-12-01",
            freq="MS",
        )
        formato_hover_periodo = "%{x|%b %Y}"

    agregados_periodo = (
        datos_temporales.groupby(["Periodo", "NAC"], observed=True)
        .agg(
            Pasajeros_acumulados=("PASAJEROS", "sum"),
            Registros=("PASAJEROS", "size"),
        )
        .reset_index()
    )
    pasajeros_periodo = agregados_periodo.pivot(
        index="Periodo", columns="NAC", values="Pasajeros_acumulados"
    ).reindex(index=periodos_completos, columns=tipos_tiempo)
    registros_periodo = agregados_periodo.pivot(
        index="Periodo", columns="NAC", values="Registros"
    ).reindex(index=periodos_completos, columns=tipos_tiempo)

    lineas = pasajeros_periodo.rename_axis("Periodo").reset_index().melt(
        id_vars="Periodo", var_name="Tipo de tráfico", value_name="Pasajeros acumulados"
    )
    lineas_registros = registros_periodo.rename_axis("Periodo").reset_index().melt(
        id_vars="Periodo", var_name="Tipo de tráfico", value_name="Registros"
    )
    lineas["Registros"] = lineas_registros["Registros"]

    fig_evolucion = px.line(
        lineas,
        x="Periodo",
        y="Pasajeros acumulados",
        color="Tipo de tráfico",
        markers=granularidad == "Anual",
        title=f"Pasajeros registrados por periodo ({granularidad.lower()})",
        labels={
            "Periodo": "Año" if granularidad == "Anual" else "Mes",
            "Pasajeros acumulados": "Pasajeros acumulados en los registros",
            "Tipo de tráfico": "Tipo de tráfico",
        },
        color_discrete_sequence=["#3B82A0", "#E28E4A"],
    )
    fig_evolucion.update_traces(
        connectgaps=False,
        hovertemplate=(
            formato_hover_periodo + "<br>Pasajeros acumulados: %{y:,.0f}"
            "<br>Registros: %{customdata[0]:,.0f}<extra></extra>"
        ),
        customdata=lineas[["Registros"]].to_numpy(),
    )
    fig_evolucion.update_layout(
        xaxis_title="Año" if granularidad == "Anual" else "Mes",
        yaxis_title="Pasajeros acumulados en los registros",
        hovermode="x unified",
        legend_title_text="Tipo de tráfico",
        margin=dict(t=70, l=55, r=25, b=55),
    )
    st.plotly_chart(fig_evolucion, use_container_width=True)

    total_periodo = pasajeros_periodo.sum(axis=1, min_count=1).dropna().sort_index()
    registros_total_periodo = registros_periodo.sum(axis=1, min_count=1).dropna().sort_index()
    texto_media = ""
    if total_periodo.empty:
        texto_evolucion = "No se pudieron obtener totales para el periodo seleccionado."
        resumen_evolucion = texto_evolucion
    elif len(total_periodo) == 1:
        periodo_unico = total_periodo.index[0]
        texto_evolucion = (
            f"En {etiqueta_periodo(periodo_unico, granularidad)}, los filtros reúnen "
            f"{formato_numero(total_periodo.iloc[0])} pasajeros acumulados. "
            "Un solo periodo no permite comparar cambios temporales."
        )
        resumen_evolucion = texto_evolucion
    else:
        primer_periodo, ultimo_periodo = total_periodo.index[0], total_periodo.index[-1]
        total_inicial, total_final = float(total_periodo.iloc[0]), float(total_periodo.iloc[-1])
        cambio = total_final - total_inicial
        media_inicial = total_inicial / registros_total_periodo.loc[primer_periodo]
        media_final = total_final / registros_total_periodo.loc[ultimo_periodo]
        cambio_media = media_final - media_inicial
        if media_inicial > 0:
            cambio_media_pct = cambio_media / media_inicial * 100
            texto_media = (
                f" El promedio por registro pasó de {formato_numero(media_inicial, 1)} "
                f"a {formato_numero(media_final, 1)} pasajeros "
                f"({formato_numero(cambio_media_pct, 1)} %)."
            )
        else:
            texto_media = (
                f" El promedio por registro pasó de {formato_numero(media_inicial, 1)} "
                f"a {formato_numero(media_final, 1)} pasajeros."
            )
        if total_inicial > 0:
            cambio_pct = cambio / total_inicial * 100
            cambio_relativo = f" ({formato_numero(cambio_pct, 1)} % respecto del primer periodo)"
        else:
            cambio_relativo = " (no se calcula variación porcentual porque el valor inicial es cero)"
        variaciones = total_periodo.diff().dropna()
        alzas = variaciones.loc[variaciones > 0]
        bajas = variaciones.loc[variaciones < 0]
        if alzas.empty:
            texto_variaciones = "No se observan aumentos entre periodos consecutivos en esta selección."
        else:
            mayor_alza = alzas.idxmax()
            texto_variacion_positiva = (
                f"La mayor alza consecutiva ocurre al llegar a "
                f"{etiqueta_periodo(mayor_alza, granularidad)} "
                f"(+{formato_numero(alzas.loc[mayor_alza])} pasajeros)."
            )
            texto_variaciones = texto_variacion_positiva
        if bajas.empty:
            texto_variaciones += " No se observan disminuciones entre periodos consecutivos."
        else:
            mayor_baja = bajas.idxmin()
            texto_variaciones += (
                f" La mayor baja consecutiva ocurre al llegar a "
                f"{etiqueta_periodo(mayor_baja, granularidad)} "
                f"(-{formato_numero(abs(bajas.loc[mayor_baja]))} pasajeros)."
            )
        texto_evolucion = (
            f"Entre {etiqueta_periodo(primer_periodo, granularidad)} y "
            f"{etiqueta_periodo(ultimo_periodo, granularidad)}, el total agregado "
            f"{('aumentó' if cambio > 0 else 'disminuyó' if cambio < 0 else 'se mantuvo')}: "
            f"pasó de {formato_numero(total_inicial)} a {formato_numero(total_final)} pasajeros"
            f"{cambio_relativo}. {texto_variaciones}"
        )
        resumen_evolucion = (
            f"De {etiqueta_periodo(primer_periodo, granularidad)} a "
            f"{etiqueta_periodo(ultimo_periodo, granularidad)}, el volumen acumulado "
            f"{('aumentó' if cambio > 0 else 'disminuyó' if cambio < 0 else 'se mantuvo')} "
            f"de {formato_numero(total_inicial)} a {formato_numero(total_final)} pasajeros."
            f"{texto_media} La suma y el promedio por registro describen aspectos distintos."
        )
    st.caption(
        texto_evolucion
        + texto_media
        + " Estas diferencias describen los registros y no permiten atribuir causas."
    )

    if len(tipos_tiempo) > 1 and len(total_periodo) > 1:
        totales_por_tipo = pasajeros_periodo.sum(axis=0, min_count=1).dropna()
        if len(totales_por_tipo) > 1:
            tipo_mayor = totales_por_tipo.idxmax()
            tipo_menor = totales_por_tipo.idxmin()
            st.caption(
                f"En el periodo elegido, {tipo_mayor} reúne el mayor total entre los tipos "
                f"seleccionados ({formato_numero(totales_por_tipo[tipo_mayor])} pasajeros), "
                f"frente a {tipo_menor} ({formato_numero(totales_por_tipo[tipo_menor])}). "
                "La diferencia también depende de cuántos registros y años aporta cada grupo."
            )

    # Totales por año y mes para el mapa de calor y el perfil porcentual.
    matriz_pasajeros = (
        datos_temporales.groupby(["Año", "Mes"], observed=True)["PASAJEROS"]
        .sum()
        .unstack("Mes")
        .reindex(index=range(rango_tiempo[0], rango_tiempo[1] + 1), columns=range(1, 13))
    )
    matriz_registros = (
        datos_temporales.groupby(["Año", "Mes"], observed=True)["PASAJEROS"]
        .size()
        .unstack("Mes")
        .reindex(index=range(rango_tiempo[0], rango_tiempo[1] + 1), columns=range(1, 13))
    )
    totales_anuales = matriz_pasajeros.sum(axis=1, min_count=1)
    matriz_porcentual = matriz_pasajeros.div(totales_anuales.where(totales_anuales.ne(0)), axis=0) * 100

    # -------------------------------------------------------------------------
    # 2. Estacionalidad y patrones mensuales
    # -------------------------------------------------------------------------
    st.header("2. Patrones mensuales y estacionalidad")
    st.markdown(
        "¿Qué meses acumulan más pasajeros registrados y se repiten esas diferencias? "
        "El mapa muestra los totales por año y mes. La vista porcentual compara la "
        "participación de cada mes dentro del total anual y ayuda a separar el perfil "
        "mensual de las diferencias de volumen entre años."
    )
    vista_mapa = st.radio(
        "Vista del mapa de calor",
        options=["Pasajeros acumulados", "Porcentaje del total anual"],
        horizontal=True,
        key="analysis_heatmap_view",
    )
    if vista_mapa == "Pasajeros acumulados":
        valores_mapa = matriz_pasajeros
        titulo_mapa = "Pasajeros acumulados por año y mes"
        colorbar_mapa = "Pasajeros acumulados"
        formato_hover_mapa = "%{z:,.0f} pasajeros"
    else:
        valores_mapa = matriz_porcentual
        titulo_mapa = "Participación de cada mes en el total anual"
        colorbar_mapa = "% del total anual"
        formato_hover_mapa = "%{z:.2f} %"

    matriz_mostrada = valores_mapa.copy()
    matriz_mostrada.columns = [MESES[mes - 1] for mes in matriz_mostrada.columns]
    customdata_mapa = matriz_registros.copy()
    customdata_mapa.columns = matriz_mostrada.columns
    fig_mapa = go.Figure(
        data=go.Heatmap(
            z=matriz_mostrada.to_numpy(),
            x=matriz_mostrada.columns.tolist(),
            y=matriz_mostrada.index.tolist(),
            customdata=customdata_mapa.to_numpy(),
            colorscale="YlOrRd",
            colorbar={"title": colorbar_mapa},
            hovertemplate=(
                "Año: %{y}<br>Mes: %{x}<br>" + formato_hover_mapa
                + "<br>Registros: %{customdata:,.0f}<extra></extra>"
            ),
            connectgaps=False,
        )
    )
    fig_mapa.update_layout(
        title=titulo_mapa,
        xaxis_title="Mes",
        yaxis_title="Año",
        yaxis={"autorange": "reversed"},
        margin=dict(t=70, l=55, r=30, b=55),
    )
    st.plotly_chart(fig_mapa, use_container_width=True)

    totales_mensuales = matriz_pasajeros.sum(axis=0, min_count=1).dropna()
    porcentajes_promedio_mes = matriz_porcentual.mean(axis=0, skipna=True).dropna()
    años_con_perfil = int(matriz_porcentual.notna().any(axis=1).sum())
    máximos_por_año = matriz_porcentual.dropna(how="all").idxmax(axis=1)
    conteo_máximos = máximos_por_año.value_counts()
    if totales_mensuales.empty or porcentajes_promedio_mes.empty:
        st.info("No hay combinaciones año-mes con valores para resumir en esta selección.")
    else:
        mes_total_máximo = int(totales_mensuales.idxmax())
        mes_total_mínimo = int(totales_mensuales.idxmin())
        mes_share_máximo = int(porcentajes_promedio_mes.idxmax())
        mes_share_mínimo = int(porcentajes_promedio_mes.idxmin())
        repeticiones_máximo = int(conteo_máximos.get(mes_share_máximo, 0))
        if años_con_perfil < 2:
            texto_repeticion = " Hay menos de dos años con datos, por lo que no se puede evaluar repetición entre años."
        else:
            texto_repeticion = (
                f" {MESES[mes_share_máximo - 1]} tuvo la mayor participación mensual en "
                f"{repeticiones_máximo} de {años_con_perfil} años con datos."
            )
        texto_estacionalidad = (
            f"En el periodo filtrado, {MESES[mes_total_máximo - 1]} reúne el mayor total "
            f"acumulado ({formato_numero(totales_mensuales[mes_total_máximo])}) y "
            f"{MESES[mes_total_mínimo - 1]} el menor "
            f"({formato_numero(totales_mensuales[mes_total_mínimo])}). Al comparar la "
            f"participación mensual promedio dentro de cada año, {MESES[mes_share_máximo - 1]} "
            f"tiene la mayor y {MESES[mes_share_mínimo - 1]} la menor. "
            f"La participación promedio compara el perfil mensual sin mezclarlo con el "
            f"volumen anual.{texto_repeticion}"
        )
        st.caption(
            texto_estacionalidad
            + " Esta repetición describe el periodo seleccionado; por sí sola no identifica "
            "una causa ni permite generalizar fuera de él."
        )
        resumen_mensual = (
            f"En totales absolutos destaca {MESES[mes_total_máximo - 1]} y el menor volumen "
            f"corresponde a {MESES[mes_total_mínimo - 1]}. Al comparar la participación "
            f"dentro de cada año, {MESES[mes_share_máximo - 1]} presenta el promedio más alto;"
            f"{texto_repeticion}"
        )


# -----------------------------------------------------------------------------
# 3. Evolución temporal de rutas direccionales
# -----------------------------------------------------------------------------
st.header("3. Evolución anual de las principales rutas direccionales")
st.markdown(
    "¿Cómo cambian año a año las rutas con más pasajeros acumulados en el periodo "
    "seleccionado? Las rutas principales se identifican sumando `PASAJEROS` dentro de "
    "ese periodo. El trayecto origen → destino se conserva; su dirección inversa es "
    "una ruta distinta."
)

col_rango_rutas, col_tipo_rutas, col_cantidad_rutas = st.columns([1.25, 1.25, 1])
with col_rango_rutas:
    rango_categoria = st.slider(
        "Periodo para comparar rutas",
        min_value=año_min,
        max_value=año_max,
        value=(año_min, año_max),
        key="analysis_route_years",
    )
with col_tipo_rutas:
    tipos_categoria = st.multiselect(
        "Tipo de tráfico",
        options=tipos_trafico,
        default=tipos_trafico,
        key="analysis_route_traffic",
    )
with col_cantidad_rutas:
    cantidad_rutas = st.slider(
        "Rutas principales a comparar",
        min_value=1,
        max_value=8,
        value=5,
        key="analysis_route_topn",
    )

datos_categoria = df.loc[
    df["Año"].between(rango_categoria[0], rango_categoria[1])
    & df["NAC"].isin(tipos_categoria)
].copy()
resumen_rutas = "No hay registros para comparar rutas con los filtros seleccionados."
if datos_categoria.empty:
    st.info("La selección no contiene registros. Amplía el periodo o selecciona al menos un tipo de tráfico.")
else:
    datos_categoria = datos_categoria.dropna(subset=["ORIG_1", "DEST_1"])
    datos_categoria["Ruta direccional"] = (
        datos_categoria["ORIG_1"].astype(str) + " → " + datos_categoria["DEST_1"].astype(str)
    )
    totales_ruta = (
        datos_categoria.groupby("Ruta direccional", observed=True)["PASAJEROS"]
        .sum()
        .sort_values(ascending=False)
    )
    if totales_ruta.empty:
        st.info("No hay rutas completas para comparar con los filtros seleccionados.")
    else:
        rutas_seleccionadas = totales_ruta.head(cantidad_rutas).index.tolist()
        st.caption(
            f"Se comparan las {len(rutas_seleccionadas)} rutas con mayor suma de pasajeros "
            f"entre {rango_categoria[0]} y {rango_categoria[1]} para los tipos de tráfico elegidos."
        )

        datos_anuales = datos_categoria.loc[
            datos_categoria["Ruta direccional"].isin(rutas_seleccionadas)
        ]
        agregados_anuales = (
            datos_anuales.groupby(["Año", "Ruta direccional"], observed=True)
            .agg(
                Pasajeros_acumulados=("PASAJEROS", "sum"),
                Registros=("PASAJEROS", "size"),
            )
            .reset_index()
        )
        años_categoria = list(range(rango_categoria[0], rango_categoria[1] + 1))
        matriz_rutas = agregados_anuales.pivot(
            index="Año", columns="Ruta direccional", values="Pasajeros_acumulados"
        ).reindex(index=años_categoria, columns=rutas_seleccionadas)
        matriz_registros_rutas = agregados_anuales.pivot(
            index="Año", columns="Ruta direccional", values="Registros"
        ).reindex(index=años_categoria, columns=rutas_seleccionadas)
        lineas_rutas = matriz_rutas.rename_axis("Año").reset_index().melt(
            id_vars="Año", var_name="Ruta direccional", value_name="Pasajeros registrados"
        )
        registros_rutas = matriz_registros_rutas.rename_axis("Año").reset_index().melt(
            id_vars="Año", var_name="Ruta direccional", value_name="Registros"
        )
        lineas_rutas["Registros"] = registros_rutas["Registros"]

        fig_rutas = px.line(
            lineas_rutas,
            x="Año",
            y="Pasajeros registrados",
            color="Ruta direccional",
            markers=False,
            title="Evolución anual de pasajeros registrados por ruta",
            labels={
                "Año": "Año",
                "Pasajeros registrados": "Suma de pasajeros registrados",
                "Ruta direccional": "Ruta (origen → destino)",
            },
            category_orders={"Ruta direccional": rutas_seleccionadas},
            color_discrete_sequence=px.colors.qualitative.Safe,
            custom_data=["Registros"],
        )
        fig_rutas.update_traces(
            connectgaps=False,
            hovertemplate=(
                "%{fullData.name}<br>Año: %{x:.0f}"
                "<br>Pasajeros registrados: %{y:,.0f}"
                "<br>Registros: %{customdata[0]:,.0f}<extra></extra>"
            ),
        )
        fig_rutas.update_layout(
            xaxis_title="Año",
            yaxis_title="Suma de pasajeros registrados",
            hovermode="x unified",
            legend_title_text="Ruta (origen → destino)",
            margin=dict(t=70, l=55, r=25, b=55),
        )
        st.plotly_chart(fig_rutas, use_container_width=True)

        # Interpretar por separado el acumulado del periodo y las variaciones anuales.
        ruta_lider = rutas_seleccionadas[0]
        total_lider = float(totales_ruta.loc[ruta_lider])
        cambios_extremos = []
        for ruta in rutas_seleccionadas:
            observaciones = matriz_rutas[ruta].dropna()
            if len(observaciones) >= 2:
                primer_año, último_año = int(observaciones.index[0]), int(observaciones.index[-1])
                cambios_extremos.append(
                    {
                        "Ruta": ruta,
                        "Cambio": float(observaciones.iloc[-1] - observaciones.iloc[0]),
                        "Primer año": primer_año,
                        "Último año": último_año,
                    }
                )

        texto_cambios = (
            "No hay suficientes años observados por ruta para comparar sus puntos inicial y final."
        )
        if cambios_extremos:
            positivos = [cambio for cambio in cambios_extremos if cambio["Cambio"] > 0]
            negativos = [cambio for cambio in cambios_extremos if cambio["Cambio"] < 0]
            if positivos:
                mayor_aumento = max(positivos, key=lambda cambio: cambio["Cambio"])
                texto_cambios = (
                    f"La mayor diferencia positiva entre el primer y último año con datos "
                    f"corresponde a {mayor_aumento['Ruta']}: "
                    f"+{formato_numero(mayor_aumento['Cambio'])} pasajeros "
                    f"({mayor_aumento['Primer año']}–{mayor_aumento['Último año']})."
                )
            else:
                texto_cambios = "Ninguna de las rutas seleccionadas termina por encima de su primer año observado."
            if negativos:
                mayor_descenso = min(negativos, key=lambda cambio: cambio["Cambio"])
                texto_cambios += (
                    f" La mayor diferencia negativa corresponde a {mayor_descenso['Ruta']}: "
                    f"-{formato_numero(abs(mayor_descenso['Cambio']))} pasajeros "
                    f"({mayor_descenso['Primer año']}–{mayor_descenso['Último año']})."
                )
            else:
                texto_cambios += " Ninguna termina por debajo de su primer año observado."

        st.caption(
            f"La ruta con mayor volumen acumulado en la selección es {ruta_lider}, con "
            f"{formato_numero(total_lider)} pasajeros registrados. {texto_cambios} "
            "La comparación temporal usa para cada ruta su primer y último año con registros; "
            "por ello, los periodos comparados pueden diferir y no se atribuyen causas."
        )
        resumen_rutas = (
            f"{ruta_lider} concentra el mayor acumulado entre las rutas comparadas "
            f"({formato_numero(total_lider)} pasajeros). {texto_cambios}"
        )


# -----------------------------------------------------------------------------
# 4. Síntesis dinámica
# -----------------------------------------------------------------------------
st.header("4. ¿Qué hemos aprendido hasta ahora?")
st.markdown(
    "Con los filtros actuales, la evidencia apunta a lo siguiente:"
)
st.markdown(
    f"- **Evolución:** {resumen_evolucion}\n"
    f"- **Meses:** {resumen_mensual}\n"
    f"- **Rutas y evolución:** {resumen_rutas}\n"
    "- **Límite:** son sumas de pasajeros pagados en registros agregados por ruta, operador y "
    "periodo. No equivalen necesariamente a personas únicas ni a vuelos individuales; las "
    "diferencias observadas son descriptivas y no demuestran causas."
)
