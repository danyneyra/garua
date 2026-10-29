# Comparación de estaciones

Guardar el listado actual de SENAMHI como `src/garua/data/stations.json`
(ignorado por Git). `estaciones.json` sigue siendo el catálogo publicado.
Ambos deben ser listas JSON; cada registro requiere `cod`, `nom`, `cate` e
`ico` como texto no vacío. Los códigos conservan sus ceros iniciales.

Desde la raíz del repositorio:

```console
python scripts/compare_stations.py --output reports/station-comparison.json
```

Sin `--output`, el informe se muestra solamente en consola. Se pueden elegir
otras fuentes mediante `--published RUTA` y `--current RUTA`. Las rutas
predeterminadas funcionan incluso desde otro directorio.

La identidad es `cod`, normalizado en memoria quitando espacios de los extremos
y convirtiéndolo a mayúsculas. Se rechazan códigos duplicados o inválidos.
El informe contiene totales, registros agregados y ausentes, y cambios en
`nom`, `cate`, `ico`, `estado`, `lat` y `lon` cuando el campo existe en ambas
fuentes. En textos se ignoran mayúsculas y espacios repetidos; las coordenadas
se comparan como números, sin redondeo. No se exigen los campos enriquecidos de
Garúa ni se interpretan como eliminados cuando faltan en el listado actual.

Una ausencia no confirma una baja: puede corresponder a un cambio de código o
a un listado incompleto. No se fusionan registros por nombre ni se añaden
etiquetas de descontinuación. Esa revisión corresponde a la siguiente fase.
Ninguna fuente se modifica, y se rechaza usarlas como destino del informe.
Un cambio de código se presenta como una ausencia y un alta para revisión.

Salida 0 significa comparación válida, aunque existan diferencias; salida 1
indica un error de entrada o salida. Pruebas:

```console
python -m unittest discover -s scripts -p test_compare_stations.py
```

## Auditoría de estaciones ausentes

```console
python scripts/audit_absent_stations.py
python scripts/audit_absent_stations.py --resume
```

Recalcula los ausentes desde las dos fuentes y consulta su ficha con las mismas
URLs que Garúa. No llama a `scraping_station_by_code`, para no actualizar objetos
del catálogo en memoria ni reutilizar accidentalmente una fecha antigua.
Requiere las dependencias instaladas del proyecto. El resultado predeterminado
es `reports/absent-stations-audit.json`, ignorado por Git.

Cada ficha debe confirmar nombre o código conocido y contener `CBOFiltro`.
Se validan, deduplican y ordenan todos sus meses; se comparan la primera fecha
anunciada y el `data_since` publicado. No se interpreta el intervalo como meses
continuos ni como observaciones confirmadas. El informe incluye el listado
completo de meses, su cantidad, la primera y última fecha anunciadas.

Solo se consulta la ficha HTTP de cada estación, con reintentos limitados.
No se abre un navegador ni se solicitan o analizan tablas mensuales.

Resultados:

- `ausente_con_periodos_anunciados`: la ficha anuncia uno o más meses.
- `ausente_sin_periodos_anunciados`: selector válido sin meses anunciados;
  no demuestra ausencia total de datos ni una baja oficial.
- `no_verificable`: selector ausente, fecha inválida, error HTTP o identidad
  no confirmada.

Opciones: `--limit 3` limita estaciones por ejecución; `--delay 1` establece
la pausa entre peticiones; `--timeout 30` y `--retries 2` controlan las consultas
HTTP de fichas. `--published`, `--current` y `--output` aceptan otras rutas.
Se guarda el informe después de cada estación mediante un archivo temporal.
`--resume` conserva los éxitos y reintenta los casos no verificables; exige las
mismas huellas SHA-256 de fuentes y la misma versión de informe. Los informes
anteriores con verificación de tablas no se reutilizan. No reanuda dentro de
una estación. Para una auditoría de otra fecha, usar un informe nuevo.

El informe conserva fecha UTC de consulta, URL, estado HTTP, huella del HTML,
identidad extraída, periodos, comparación de fecha inicial y errores. No afirma
una baja oficial ni modifica las fuentes. Salida 0 indica ejecución completada,
incluso si quedan pendientes o casos no verificables; revisar el resumen.

Pruebas sin red:

```console
python -m unittest discover -s scripts -p "test_*.py"
```

## Enriquecimiento de estaciones agregadas

Desde PowerShell en la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe scripts\enrich_added_stations.py
```

Consulta únicamente las fichas de los códigos presentes en `stations.json`
y ausentes de `estaciones.json`. Una consulta por estación, salvo reintentos
HTTP limitados; no abre navegador ni solicita tablas mensuales.
Guarda `reports/added-stations-enrichment.json` sin modificar las fuentes.

Cada `candidata` contiene los campos del catálogo publicado. Conserva los
campos base de la fuente actual y obtiene de la ficha `cod_ui`, `dep`, `prov`,
`dist` y `alt`. Los valores desconocidos quedan como `null`. No deduce
`cod_old` a partir de `cod_ui`. `data_since` es el menor mes válido del selector
`CBOFiltro`, después de ordenar y eliminar duplicados; también conserva todos
los periodos, cantidad, primera y última fecha anunciadas. No confirma que las
tablas contengan observaciones.

Evalúa por separado:

- `ficha`: `completa`, `incompleta` o `no_verificable`. Se comprueban los campos
  base, ubicación, código de interfaz y altitud. `cod_old` es opcional y la
  disponibilidad de fechas se evalúa por separado.
- `disponibilidad`: `con_periodos_anunciados`, `sin_periodos_anunciados` o
  `no_verificable`. Un selector ausente o inválido no equivale a cero meses;
  conserva los datos de una ficha cuya identidad pudo confirmarse.
- `revision`: `candidata_incorporacion` si tiene ficha completa y periodos;
  `pendiente_disponibilidad` si la ficha está completa y no anuncia meses;
  `pendiente_revision` en los demás casos.

Todas las agregadas quedan en el informe, sin eliminar ni incorporar ninguna
automáticamente. Incluye campos faltantes, errores y evidencia de consulta.

```powershell
.\.venv\Scripts\python.exe scripts\enrich_added_stations.py --limit 3
.\.venv\Scripts\python.exe scripts\enrich_added_stations.py --resume
```

`--resume` conserva fichas completas o incompletas con disponibilidad evaluada
y reintenta los casos no verificables. Para revisar de nuevo estaciones que
antes no anunciaban periodos, ejecutar sin `--resume` o usar otro `--output`.
Admite `--published`, `--current`, `--output`, `--delay`, `--timeout` y `--retries`.
Reanudar exige las mismas fuentes y versión. Salida 0 indica ejecución válida,
incluso con casos no verificables; revisar el resumen y los pendientes.

## Preparar el catálogo candidato con etiquetas

Después de generar la auditoría de ausentes y el enriquecimiento de agregadas:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_station_catalog.py --catalog-date 2026-10-27
```

`--catalog-date` es la fecha del listado local SENAMHI, no la fecha en que se
ejecuta el script. Se proporciona explícitamente para no inventar su antigüedad.
Las consultas de disponibilidad conservan su propia fecha, convertida a Lima.
No hace peticiones de red.

Genera `reports/stations-candidate.json` (lista compatible con el catálogo) y
`reports/stations-candidate-review.json` (procedencia, resumen y pendientes).
No modifica ninguna fuente ni informe de entrada. Comprueba las huellas de
ambos catálogos registradas en los informes, sus versiones, alcance y códigos.
Admite otras rutas mediante `--published`, `--current`, `--absent-report`,
`--added-report`, `--output` y `--review-output`.

Conserva todas las publicadas y añade candidatas enriquecidas que pasan la
validación del modelo, incluidas las pendientes de disponibilidad o revisión.
Las agregadas sin informe o con estructura inválida quedan en el archivo de
revisión. Actualiza los campos compartidos `nom`, `cate`, `ico`, `estado`, `lat`
y `lon` cuando están presentes en ambas fuentes y son diferentes. Conserva los
campos enriquecidos y el `data_since` de las publicadas. El informe incluye
`cambios_estaciones_comunes` con valores anteriores y nuevos.
El catálogo candidato no es una selección lista para publicar; revisar su
archivo de pendientes antes de usarlo.

Campos nuevos, independientes de `estado` (`REAL`, `DIFERIDO`, `AUTOMATICA`):

| Campo | Valores |
| --- | --- |
| `catalog_status` | `listed`, `absent`, `unknown` |
| `availability_status` | `periods_announced`, `no_periods_announced`, `periods_unknown` |
| `catalog_checked_at` | Fecha ISO del listado, o `null` |
| `availability_checked_at` | Fecha ISO de consulta, incluso si falló, o `null` |
| `note` | Explicación de revisión |

Las estaciones comunes sin auditoría de disponibilidad quedan `periods_unknown`,
aunque tengan `data_since`. No se infiere una baja oficial ni presencia de
observaciones. El modelo y la serialización del MCP exponen estos campos sin
bloquear consultas. Los registros antiguos sin etiquetas cargan con valores
`unknown`/`periods_unknown` y fechas `null`. La aplicación sigue cargando únicamente
su catálogo publicado; preparar el candidato no cambia los resultados activos.

## Actualizar metadatos de estaciones comunes

Si ya incorporaste las agregadas y las etiquetas, puedes preparar únicamente
los cambios de campos compartidos, sin repetir las consultas de fichas:

```powershell
.\.venv\Scripts\python.exe scripts\update_station_metadata.py
```

Genera `reports/stations-metadata-candidate.json` y
`reports/stations-metadata-review.json` con el detalle antes/después y las huellas
de las fuentes. Esta ejecución no modifica ninguno de los dos catálogos.

Para aplicar deliberadamente los cambios al catálogo publicado:

```powershell
.\.venv\Scripts\python.exe scripts\update_station_metadata.py --apply
```

Valida todo el catálogo antes de escribir y conserva una copia exacta en
`reports/estaciones-before-metadata-<huella>.json`. Nunca modifica `stations.json`.
No añade ni elimina estaciones. Solo actualiza `nom`, `cate`, `ico`, `estado`,
`lat` y `lon`; conserva códigos, ubicación administrativa, altitud, `data_since`,
etiquetas y notas. Los textos equivalentes por mayúsculas/espacios no se reescriben.
Sin diferencias no vuelve a escribir el catálogo publicado.

Admite `--published`, `--current`, `--output` y `--review-output`. Los destinos
de informes y respaldo no pueden sobrescribir las fuentes. Los informes de
auditorías anteriores siguen siendo evidencia histórica; no se reutilizan en
este paso ni se eluden sus controles de huellas en el generador completo.
