---
icon: simple/modelcontextprotocol
title: "Compatibilidad de Garúa con FastMCP 4 y MCP 2"
description: "Revisa la migración de Garúa a FastMCP 4, las versiones de dependencias admitidas y las pruebas de compatibilidad del servidor MCP."
---

# Compatibilidad con FastMCP 4

La versión 0.31.0 trabaja con FastMCP 4.1.4, MCP 2.3.0 y mcp-types 2.3.0.
La versión 0.30.0 utiliza una línea anterior de dependencias; sus requisitos
no cambian retroactivamente con esta actualización.

## Dependencias y actualizaciones

`pyproject.toml` declara:

```text
fastmcp>=4.1.4,<4.2
mcp>=2.3.0,<2.4
mcp-types>=2.3.0,<2.4
```

Se permiten parches dentro de esas líneas. Un cambio de versión menor requiere
revisión: FastMCP 4.1 incluyó cambios de comportamiento respecto a 4.0.
No se promete compatibilidad con futuras versiones que aún no se han probado.
`mcp_compat.py` comprueba estos rangos antes de importar el servidor y explica
cómo reparar un entorno modificado. Una instalación manual que ignore los
requisitos puede dejar el entorno inconsistente; ningún rango impide que alguien
lo fuerce. La comprobación falla con contexto, sin intentar reparar paquetes.

El `uv.lock` del repositorio fija la resolución completa para desarrollo y CI:

```bash
uv sync --locked --extra dev
uv run --locked python -m unittest discover -s scripts -p "test_*.py"
```

El lockfile no impone versiones a quien instala Garúa desde PyPI. Esa instalación
usa los requisitos del paquete publicado. No actualices dependencias individuales
dentro de una instalación de usuario; actualiza Garúa como unidad en un entorno
aislado con `uv tool upgrade garua` o `pipx upgrade garua`.

## Revisión de cambios oficiales

| Versión | Cambio revisado | Aplicación en Garúa |
| --- | --- | --- |
| [4.0](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.0.0) | SDK MCP 2, campos Python snake_case, APIs antiguas retiradas, tareas como extensión y protocolo nuevo con negociación de clientes anteriores. | Mantener stdio; probar clientes de ambos protocolos. Garúa no usa sampling, roots, APIs retiradas ni tareas en segundo plano. |
| [4.0.9](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.0.9) | Caché de patrones de plantillas de resources. | Probar lectura de resources y descubrimiento de plantillas. |
| [4.0.10](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.0.10) | Correcciones de stdio y tareas tras transforms. | Probar el proceso stdio real; Garúa no usa task tools ni CodeMode. |
| [4.0.11](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.0.11) | Endurecimiento de clientes, esquemas, OpenAPI y controles de acceso. | Probar esquemas del catálogo completo de tools. No hay OAuth, proxies ni OpenAPI configurados en Garúa. |
| [4.1.0](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.0) | Cambios en MultiAuth, búsqueda regex, rutas de skills/OpenAPI, sesiones HTTP y soporte de Python. | No se activan estos componentes. Mantener límites menores explícitos y pruebas stdio. No ampliar la lista de versiones Python soportadas sin probarlas. |
| [4.1.1](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.1) | Límites de búsqueda regex, skills enlazadas y correcciones de configuración proxy/JWKS. | No hay configuración propia que migrar para estas funciones. |
| [4.1.2](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.2) | Autorización tras transforms, binding del issuer OAuth, resources síncronos en threadpool y OpenAPI. | Probar resources y prompts existentes; no añadir OAuth o providers ajenos al caso de uso. |
| [4.1.3](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.3) | Dependencias de certificados, timeouts y correcciones de generadores/visibilidad. | Resolver dependencias actualizadas. La actualización de certificados del sistema sigue siendo responsabilidad del entorno. |
| [4.1.4](https://github.com/PrefectHQ/fastmcp/releases/tag/v4.1.4) | Correcciones de CLI generada, servidores montados, sesiones de cliente, OAuth y extras de tareas/keyring. | Garúa usa su propia CLI, sin servidores montados, Redis ni keyring personalizado. Verificar cliente, registro de tools y resultados nativos. |

La [guía oficial de migración desde FastMCP 3](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-3)
es la referencia para futuras revisiones. Garúa ya requiere Python 3.11+ y
Pydantic 2.13.4+, por encima de los mínimos de esa migración. No integra FastAPI,
por lo que no tiene una restricción propia de Starlette que adaptar.

## Respuestas y tipos

Los helpers de `schemas/` devuelven `fastmcp.tools.ToolResult` con
`content`, `structured_content` e `is_error`. No deben devolver un diccionario
que imite un resultado MCP: FastMCP lo trataría como datos y envolvería de nuevo
el mensaje, los errores y los enlaces. El contenido estructurado conserva los
campos de negocio: `station`, `stations`, `files`, `stats`, etc.

Los clientes reciben errores de ejecución con `isError=true`, texto legible y
detalles estructurados. Los enlaces aparecen como bloques `resource_link`
nativos. Un error de argumentos sigue siendo distinto de una descarga fallida.
Cada respuesta de Garúa incluye también un bloque `TextContent` con el JSON
completo de `structuredContent`; el mensaje legible va en su campo `message`,
sin un bloque de resumen separado. Esto permite que
clientes que solo incorporan `content` al contexto del modelo reciban estaciones,
filas, estadísticas y detalles de errores. `schemas/result.py` centraliza esta
compatibilidad, conservando los enlaces nativos y el resultado `ToolResult`.
Las aplicaciones que antes desempaquetaban `structuredContent` dos veces deben
leer ahora directamente el contenido estructurado del resultado MCP.

En objetos Python del SDK se usan `mime_type`, `structured_content` e `is_error`;
el protocolo JSON conserva sus alias camelCase. Las URI de `ResourceLink` son
texto, aunque `FileInfo` use `AnyUrl` internamente. Los tests desactivan el puente
camelCase para detectar dependencias accidentales de las compatibilidades antiguas.

## Publicación y recuperación

Las restricciones nuevas se incorporan a Garúa 0.31.0.
No es posible cambiar retroactivamente los requisitos de un wheel 0.30.0 ya
instalado. Por eso esta migración utiliza el número 0.31.0. Si se mantiene una rama FastMCP 3, necesita una publicación de mantenimiento
separada con límites `fastmcp<4` y `mcp<2`, y sus propias pruebas.

Para recuperar una 0.30.0 publicada cuyo entorno fue actualizado a FastMCP 4,
se puede reinstalar en otro entorno con restricciones para su línea original:

```bash
uv tool install --force --reinstall "garua==0.30.0" --with "fastmcp>=3.3.1,<4" --with "mcp>=1.27.1,<2"
```

Es una ruta de recuperación de la rama anterior, no la pila probada por esta
migración. Para adoptar FastMCP 4, utiliza Garúa 0.31.0. El comando
`uv tool install garua` instala la versión disponible en PyPI; no obtiene cambios
del repositorio que aún no se hayan publicado.

## Validación y límites

Las pruebas sin acceso a SENAMHI cubren validación de argumentos, descarga
simulada con archivo, enlaces nativos, errores MCP, búsquedas, fichas, resources,
plantillas, prompts, ambos protocolos y arranque stdio en otro proceso.
Los CSV temporales no afectan a descargas existentes. La batería no sustituye
una prueba de navegador frente a SENAMHI ni valida funciones de FastMCP que
Garúa no utiliza. CI está configurado para Python 3.11, 3.12 y 3.13 en Windows
y Linux; su ejecución remota depende de subir estos cambios.
