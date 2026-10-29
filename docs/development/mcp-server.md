---
icon: lucide/server
title: "Desarrollar el servidor MCP de Garúa"
description: "Consulta la estructura del servidor MCP de Garúa, el registro de herramientas y las convenciones para implementar respuestas y flujos de análisis."
---

# Servidor MCP

Garúa expone un servidor MCP local sobre `stdio`. El comando instalado es:

```bash
garua-mcp
```

También puede ejecutarse como módulo cuando trabajas desde un entorno virtual:

```bash
python -m garua_mcp
```

## Punto de entrada

El servidor se define en `src/garua/mcp_server.py`. Ahí se crea la instancia de
FastMCP, se carga el catálogo de estaciones y se registran los módulos de tools.

La migración a FastMCP 4.1.4, los límites de dependencias y las pruebas del
protocolo están descritos en [Compatibilidad MCP](fastmcp-4.md).

| Módulo | Grupo funcional |
| --- | --- |
| `station_tools.py` | Búsqueda, filtros, disponibilidad y ficha de estaciones. |
| `stats_tools.py` | Conteos y resúmenes del inventario de estaciones. |
| `file_tools.py` | Archivos CSV descargados, previews y extracción mensual. |
| `download_tools.py` | Descarga o extracción de datos SENAMHI. |
| `recommendation_tools.py` | Recomendación de estaciones para un punto geográfico. |
| `comparison_tools.py` | Comparación de meses, años o periodos. |
| `anomaly_tools.py` | Validación de calidad y anomalías. |
| `summary_tools.py` | Resumen de datos para un periodo individual. |

## Principios

- Usa la tool más específica para la intención del usuario.
- No recalcules métricas en el cliente MCP si Garúa ya ofrece una tool para eso.
- No descargues datos si el usuario solo pidió explorar archivos locales.
- No resumas, compares o valides dentro de la tool de descarga.
- No inventes códigos de estación: busca, filtra o confirma primero.

## Anatomía de una tool

Una tool MCP debe tener:

- Parámetros tipados con `Annotated[..., Field(description=...)]`.
- Docstring orientado al cliente MCP, no solo al desarrollador.
- Delegación clara hacia `services/` cuando haya lógica de negocio.
- Respuesta consistente usando los helpers de respuesta del proyecto.
- Ejemplos o notas de flujo suficientes para la referencia generada.

Ejemplo de estructura:

```python
@mcp.tool()
def search_stations(
    query: Annotated[
        str,
        Field(description="Código exacto o nombre parcial de la estación."),
    ],
) -> ToolResult:
    """
    Busca estaciones SENAMHI por código o por nombre.

    Úsala cuando el usuario mencione una estación específica pero no esté claro
    si proporcionó código interno, código anterior o solo una parte del nombre.
    """
    ...
```

## Agregar una tool

1. Define si la tool pertenece a un módulo existente o necesita un grupo nuevo.
2. Implementa la lógica compartida en `src/garua/services/` si no existe.
3. Agrega la función MCP en `src/garua/mcp_tools/`.
4. Registra el módulo en `src/garua/mcp_server.py` si es un grupo nuevo.
5. Escribe un docstring con cuándo usarla, cuándo no usarla y qué devuelve.
6. Regenera la referencia:

    ```bash
    python scripts/generate_tools_reference.py
    ```

7. Valida la documentación:

    ```bash
    zensical build --clean --strict
    ```

## Calidad de docstrings

Los docstrings MCP son parte del contrato con los clientes. Deben ayudar al
modelo a elegir la tool correcta.

Incluye:

- intención principal;
- restricciones importantes;
- diferencia frente a tools parecidas;
- dependencias de flujo, por ejemplo buscar estación antes de descargar;
- advertencias sobre datos locales, scraping o calidad.

Evita:

- explicar detalles internos que el cliente no necesita;
- prometer descargas automáticas si el flujo requiere datos locales;
- duplicar instrucciones contradictorias entre tools similares.

## Validación local

Para revisar que el servidor arranca:

```bash
garua-mcp
```

En clientes como VS Code, Claude Desktop o Codex, configura el comando
`garua-mcp` o una ruta absoluta al Python de tu entorno virtual. La configuración
de usuario está documentada en [Instalación](../installation.md#configurar-mcp){data-preview}.

## Referencia relacionada

- [Arquitectura](architecture.md){data-preview}
- [Referencia de tools MCP](../reference/tools.md){data-preview}
- [Uso MCP](../usage/mcp.md){data-preview}
## Progreso de descargas

La entrega de CSV, los límites de contenido embebido y la integración opcional
con Filesystem se describen en [Entrega de archivos](file-delivery.md).

`scrape_station_data` recibe `Context` mediante `CurrentContext()`; este parámetro
no forma parte del esquema público de argumentos. El servicio y el scraper
aceptan un callback asíncrono opcional `on_progress(message)`, sin depender de MCP.
La tool convierte los eventos en `ctx.report_progress()`.

Los mensajes incluyen preparación, extracción local, conexión, periodos
identificados, periodo actual y estación, reintentos, pausas entre años,
periodos procesados o fallidos, guardado consolidado y resultado final. La
finalización se emite después de que el scraper libere el navegador.

El valor numérico cuenta eventos y aumenta durante una llamada; `total` se omite
porque preparación y reintentos no tienen un número predecible de pasos. No es
un porcentaje de tiempo ni un contador de descargas exitosas. El mensaje indica
el periodo actual y el total de opciones disponibles. Los errores parciales se
conservan en el resultado estructurado final.

El cliente debe enviar `progressToken` y representar las notificaciones para
mostrarlas. Sin token, FastMCP omite el envío. El progreso no garantiza mensajes
intermedios en el chat ni elimina los timeouts del cliente. No se crean tareas
persistentes ni se continúa la operación después de una desconexión por este mecanismo.

Pruebas sin red ni navegador:

```bash
python -m unittest discover -s scripts -p "test_scraping*.py"
```

Incluyen una descarga simulada a través de stdio con ambos protocolos,
progreso creciente, reintentos, resultado parcial, extracción local y ausencia
de token. `scraping_progress_fixture.py` es exclusivamente un servidor de prueba.
