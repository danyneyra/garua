---
icon: lucide/file-down
title: "Entrega de archivos CSV mediante MCP en Garúa"
description: "Conoce cómo Garúa entrega CSV a clientes MCP mediante enlaces, lectura de resources y contenido embebido, con sus límites y rutas locales."
---

# Entrega de CSV a clientes MCP

Las respuestas conservan `files[].path` y `files[].uri` (ruta y URI local
`file://`) y añaden `files[].resource_uri` cuando el CSV existe dentro de
`CSV_DIR` o `EXPORTS_DIR`. El índice de descargas también devuelve `resource_uri`.
Los bloques `resource_link` usan esa URI MCP cuando está disponible.

El cliente puede enviar `resources/read` con la URI `garua://files/{file_id}`
para recibir el CSV sin acceso directo al filesystem del servidor. El identificador
codifica el área y la ruta relativa; no es un token secreto ni una autorización.
Cada lectura valida que el archivo resuelto permanezca dentro de un directorio
permitido, incluidos enlaces simbólicos. Solo se admiten CSV existentes.
Los archivos externos conservan sus referencias locales, sin anunciar lectura MCP.
La plantilla anterior `garua://data/files/{station_code}/{filename}` sigue disponible.

## Contenido embebido

Los CSV pequeños enlazados desde una respuesta viajan también como bloques
`resource` con `TextResourceContents` y `mime_type="text/csv"`. Son contenidos
completos; no se adjuntan fragmentos que parezcan archivos completos.
El JSON principal sigue siendo un único bloque `text`, idéntico a
`structuredContent`; los recursos embebidos son bloques adicionales.

| Variable | Valor predeterminado | Efecto |
| --- | --- | --- |
| `GARUA_MCP_INLINE_FILE_MAX_BYTES` | 32768 | Máximo de bytes CSV por archivo embebido |
| `GARUA_MCP_INLINE_TOTAL_MAX_BYTES` | 65536 | Presupuesto total de bytes CSV por respuesta |

Poner cualquiera de los límites en 0 desactiva los adjuntos embebidos. Los
límites miden bytes CSV antes de serializar el protocolo, no tokens ni tamaño JSON.
Archivos mayores, ilegibles o eliminados después de producir la respuesta no se
embeben; los límites no restringen la lectura completa solicitada con
`resources/read`. URI repetidas se adjuntan una sola vez.

## Evaluación de las alternativas

| Mecanismo | Qué resuelve | Límite |
| --- | --- | --- |
| Ruta local / `file://` | Abrir el archivo desde un cliente con acceso local | No transfiere bytes a un cliente remoto |
| URI MCP + `resources/read` | Transportar el CSV bajo demanda | El host debe exponer o utilizar resources |
| Recurso embebido | Transportar CSV pequeños junto al resultado | Consume contexto; no garantiza una tarjeta descargable |
| Descarga HTTP | Descargar archivos grandes desde una URL accesible | Requiere endpoint, alcance de red, autorización y ciclo de vida de enlaces |
| Filesystem en el cliente | Leer los CSV locales desde herramientas MCP | Requiere acceso a las rutas y un mecanismo adicional para publicar adjuntos |

Se implementan URI MCP y adjuntos pequeños como base portable. No se publica
un endpoint HTTP de archivos. MCP Apps queda descartado para este flujo. Ejecutar MCP
mediante HTTP no expone automáticamente una URL descargable para cada CSV.

Si se necesita descarga directa independiente del chat, el siguiente paso es un
endpoint autenticado con identificadores de archivo y cabecera de descarga,
reutilizando la misma resolución de rutas. No basta con devolver una URL localhost
cuando el cliente o su entorno de ejecución están en otro equipo.

## Integración opcional con Filesystem

Garúa y `@modelcontextprotocol/server-filesystem` se conectan como servidores
independientes al mismo cliente. El cliente coordina sus herramientas; Garúa no
instala Filesystem, no lo invoca ni requiere una dependencia de Node.js.

Para utilizar este flujo, Filesystem debe ejecutarse en un entorno con acceso
a los CSV de Garúa. Configura la carpeta de salida como directorio autorizado
en Filesystem, mediante argumentos o los roots que soporte esa instalación.
`list_allowed_directories`, si está disponible, permite comprobar el acceso.
Una ruta Windows local no identifica el mismo archivo en un servidor remoto.
Consulta la [configuración oficial de Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem).

Después de descargar:

1. El cliente toma `files[].path` del resultado de Garúa, sin volver a listar
   archivos para reconstruir las rutas.
2. Si tiene herramientas Filesystem autorizadas, lee un CSV con `read_text_file`
   o varios con `read_multiple_files`, utilizando el contenido completo.
3. Si también dispone de un entorno para guardar archivos y una herramienta
   de presentación, guarda una copia con el mismo contenido y la presenta
   mediante el mecanismo disponible, por ejemplo `present_files`.
4. Confirma la entrega solo tras completarla. Conserva el CSV original; no usa
   `move_file` para este flujo.

Leer contenido con Filesystem no lo copia automáticamente al entorno de
ejecución del cliente. Ese paso necesita herramientas adicionales y no se deduce
por el nombre del cliente. Garúa no fija una carpeta de adjuntos del cliente.
Si faltan esas capacidades, devuelve rutas y URI sin afirmar que se adjuntaron
archivos. `resource_uri` y los recursos embebidos siguen siendo alternativas
para obtener los datos sin Filesystem.

La descripción de `scrape_station_data` incluye esta guía condicional. El
usuario sigue configurando Filesystem en su cliente; no se modifica su
configuración ni se instala la extensión automáticamente.

## Validación y comprobación en clientes

Las pruebas automatizadas cubren lectura por URI en ambos protocolos, lectura
por stdio real, igualdad del contenido embebido y leído, límites por archivo y
respuesta, desactivación, exportaciones y rechazo de rutas externas o manipuladas.

La presentación en Claude y Codex requiere una comprobación manual por cliente:

1. Reiniciar el servidor y reconectar el cliente.
2. Descargar un CSV pequeño y confirmar que la respuesta incluye su contenido
   embebido y `resource_uri`.
3. Leer la URI MCP y comparar el CSV con el archivo local.
4. Repetir con un CSV que exceda el límite: debe quedar enlazado, sin contenido
   embebido parcial.
5. Anotar por separado si el modelo recibe datos, si el usuario ve una vista
   previa y si puede descargar un adjunto. Son capacidades distintas.
6. Con Filesystem conectado, verificar acceso a la carpeta, lectura de las rutas
   devueltas y presentación de una copia si el cliente ofrece esa capacidad.
   Repetir sin Filesystem: la descarga de Garúa debe seguir funcionando.

Las pruebas de protocolo no verifican la interfaz de Claude o Codex ni la copia
de archivos a sus entornos de ejecución. Esas comprobaciones permanecen pendientes.
