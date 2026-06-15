---
icon: lucide/history
tags:
  - Changelog
  - Releases
  - Versiones

---

# Changelog

Esta página resume los cambios visibles para usuarios de Garúa. El historial
detallado del proyecto también se mantiene en el archivo
[`CHANGELOG.md`](https://github.com/danyneyra/garua/blob/main/CHANGELOG.md) y en
las publicaciones de GitHub.

## v0.30.0 - 2026-06-15

### Nueva etapa como Garúa

- El proyecto adopta el nombre **Garúa** y deja atrás la etapa inicial como
  `senamhi-scraper`.
- Se consolida como una herramienta para usar desde terminal, scripts y clientes de IA
  compatibles con MCP.
- Se actualizan los metadatos del paquete para publicación en PyPI.

### CLI

- `garua` abre la aplicación interactiva de terminal.
- Se mantienen opciones por parámetros para flujos automatizados.
- `garua --doctor` y `garua --health` ayudan a validar Python, sistema operativo,
  carpeta de salida y navegador disponible.

### Servidor MCP

- `garua-mcp` inicia el servidor MCP local por `stdio`.
- La referencia de herramientas MCP se genera desde el código para reducir
  diferencias entre implementación y documentación.
- Se agregan ejemplos de configuración para VS Code, Codex, Claude Desktop y
  otros clientes compatibles.

### Documentación

- Nueva documentación con Zensical.
- Guías por tarea para buscar estaciones, descargar datos, explorar CSV, resumir,
  comparar, validar calidad y recomendar estaciones.
- Referencias para herramientas MCP, CLI, variables de entorno, archivos de
  salida y criterios de calidad de datos.
- Instrucciones de instalación y actualización con `pip` y `pipx`.

### Empaquetado

- El paquete fuente mantiene un `sdist` liviano: incluye código, README,
  changelog, contributing, licencia y metadatos.
- Las dependencias de documentación quedan como extra opcional y no se instalan
  al usar `pip install garua`.

## Historia del Proyecto

Garúa nació como una herramienta CLI para descargar datos hidrometeorológicos del
SENAMHI. Con el tiempo evolucionó hacia una librería modular y un servidor MCP
para que asistentes de IA compatibles puedan buscar estaciones, descargar datos,
resumir, comparar y validar información sin escribir scripts manuales.
