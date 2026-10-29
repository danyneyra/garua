"""Prompts MCP para flujos habituales de análisis en Garúa."""

from typing import Annotated

from pydantic import Field


def register_prompts(mcp) -> None:
    """Registra prompts de workflow sin duplicar la lógica de las tools."""

    @mcp.prompt(
        name="analizar_periodo_estacion",
        title="Analizar periodo de una estación",
        description=(
            "Orquesta la búsqueda, disponibilidad, archivos locales, descarga y "
            "resumen de un periodo SENAMHI."
        ),
        tags={"analysis", "summary", "senamhi"},
    )
    def analizar_periodo_estacion(
        station: Annotated[
            str,
            Field(description="Código o nombre de la estación SENAMHI."),
        ],
        period: Annotated[
            str,
            Field(description="Periodo, por ejemplo 'julio de 2025' o '2020-2025'."),
        ],
        objective: Annotated[
            str,
            Field(description="Qué se desea conocer del periodo."),
        ] = "Resume las métricas disponibles y señala advertencias de calidad.",
    ) -> str:
        return f"""Quiero analizar el periodo {period} de la estación {station}.

Objetivo: {objective}

Sigue este flujo usando las capacidades MCP de Garúa:
1. Si recibiste un nombre, usa search_stations y confirma el código antes de analizar.
2. Consulta garua://catalog/stations o get_station_info para validar la estación.
3. Usa check_data_availability para comprobar que el periodo esté cubierto.
4. Usa list_downloaded_files para buscar un CSV local que cubra el periodo.
5. Si falta el archivo, usa scrape_station_data solo para descargar los datos solicitados.
6. Usa summarize_station_data_tool para calcular las métricas; no hagas cálculos manuales.
7. Conserva las advertencias de calidad y explica la interpretación de S/D y T.

Responde en español con: estación y código, periodo, esquema detectado, métricas,
calidad de datos, advertencias, fuente/archivo utilizado y una conclusión breve."""

    @mcp.prompt(
        name="comparar_periodos_estacion",
        title="Comparar periodos de una estación",
        description=(
            "Orquesta la preparación y comparación de dos o más periodos de una "
            "estación SENAMHI."
        ),
        tags={"analysis", "comparison", "senamhi"},
    )
    def comparar_periodos_estacion(
        station: Annotated[
            str,
            Field(description="Código o nombre de la estación SENAMHI."),
        ],
        periods: Annotated[
            str,
            Field(description="Periodos a comparar, por ejemplo 'marzo 2025 vs marzo 2026'."),
        ],
        objective: Annotated[
            str,
            Field(description="Aspecto principal de la comparación."),
        ] = "Compara las métricas disponibles y explica las diferencias.",
    ) -> str:
        return f"""Quiero comparar {periods} para la estación {station}.

Objetivo: {objective}

Sigue este flujo usando las capacidades MCP de Garúa:
1. Si recibiste un nombre, usa search_stations y confirma el código.
2. Consulta garua://catalog/stations o get_station_info para identificar tipo y estado.
3. Convierte los periodos a la estructura periods requerida por compare_periods_tool,
   con label, year y month cuando corresponda.
4. Revisa disponibilidad y archivos locales para todos los periodos.
5. Si faltan meses, usa una sola llamada a scrape_station_data con periods cuando sea posible.
6. Ejecuta compare_periods_tool con deduplicate=True; no calcules diferencias manualmente.
7. Considera warnings, datos faltantes, S/D y T antes de sacar conclusiones.

Responde en español con: estación y código, periodos, esquema detectado, tabla de
métricas, diferencias absolutas y porcentuales cuando existan, advertencias, archivos
        utilizados y una conclusión que distinga datos observados de inferencias."""

    @mcp.prompt(
        name="auditar_calidad_datos",
        title="Auditar calidad de datos",
        description=(
            "Guía una auditoría de calidad de un periodo de datos SENAMHI y "
            "prioriza las anomalías que requieren revisión."
        ),
        tags={"quality", "anomalies", "senamhi"},
    )
    def auditar_calidad_datos(
        station: Annotated[
            str,
            Field(description="Código o nombre de la estación SENAMHI."),
        ],
        period: Annotated[
            str,
            Field(description="Periodo a auditar, por ejemplo 'julio de 2025'."),
        ],
        focus: Annotated[
            str,
            Field(description="Aspecto de calidad que debe priorizarse."),
        ] = "Revisa todas las anomalías disponibles.",
    ) -> str:
        return f"""Quiero auditar la calidad del periodo {period} de la estación {station}.

Prioridad de la auditoría: {focus}

Sigue este flujo usando las capacidades MCP de Garúa:
1. Resuelve el nombre a código con search_stations si es necesario.
2. Consulta la ficha de estación en garua://catalog/stations/{{station_code}}.
3. Verifica cobertura con check_data_availability y localiza el CSV con list_downloaded_files.
4. Si no existe el archivo, descarga únicamente el periodo solicitado con scrape_station_data.
5. Ejecuta detect_anomalies_tool para el diagnóstico; no inspecciones ni calcules la calidad manualmente.
6. Reporta por separado duplicados, fechas faltantes, S/D, T, filas inválidas y problemas de esquema.
7. Clasifica cada hallazgo como bloqueante, advertencia o informativo y explica su impacto.

Responde en español con: estación y código, periodo, archivo analizado, cobertura,
hallazgos, severidad, limitaciones y una recomendación concreta para usar o revisar
los datos."""

    @mcp.prompt(
        name="seleccionar_estacion",
        title="Seleccionar estación para un análisis",
        description=(
            "Guía la selección de una estación SENAMHI según ubicación, altitud, "
            "tipo y disponibilidad histórica."
        ),
        tags={"stations", "recommendation", "senamhi"},
    )
    def seleccionar_estacion(
        location: Annotated[
            str,
            Field(description="Ubicación, coordenadas o zona de interés."),
        ],
        objective: Annotated[
            str,
            Field(description="Qué análisis se quiere realizar con la estación."),
        ],
        constraints: Annotated[
            str,
            Field(description="Restricciones como altitud, radio, tipo o antigüedad."),
        ] = "Sin restricciones adicionales.",
    ) -> str:
        return f"""Necesito seleccionar una estación SENAMHI para {objective}.

Ubicación de interés: {location}
Restricciones: {constraints}

Sigue este flujo usando las capacidades MCP de Garúa:
1. Convierte la ubicación a latitud/longitud y extrae las restricciones explícitas.
2. Usa recommend_station_for_point_tool como ranking principal cuando haya coordenadas.
3. Usa find_stations_near o filter_stations_advanced para ampliar o verificar candidatos.
4. Consulta garua://catalog/stations/{{station_code}} para cada candidato final.
5. Usa check_data_availability para comprobar que la historia cubre el análisis solicitado.
6. No elijas solo por distancia: considera tipo, estado, altitud, antigüedad y disponibilidad.

Responde en español con los mejores candidatos ordenados, una puntuación o criterio
comparable, distancia, altitud, tipo, estado, años disponibles, ventajas, riesgos y
una recomendación final. Si faltan coordenadas o una restricción esencial, pide solo
ese dato antes de recomendar."""
