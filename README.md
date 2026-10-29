<div align="center">
  <a href="https://garua.danyneyra.dev/">
    <img alt="Logo de Garúa" src="https://github.com/danyneyra/garua/blob/main/docs/images/garua-logo.svg">
  </a>

  <p><strong>Garúa</strong> descarga, explora y analiza datos hidrometeorológicos oficiales del SENAMHI Perú.</p>
</div>

> Garúa es la llovizna fina característica de la costa peruana.

[![PyPI](https://img.shields.io/badge/PyPI-1c83ff?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/garua/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-89e240?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

**Documentación:** [garua.danyneyra.dev](https://garua.danyneyra.dev)

**Código fuente:** [github.com/danyneyra/garua](https://github.com/danyneyra/garua)

---

Garúa es una herramienta de código abierto para trabajar con estaciones meteorológicas e hidrológicas del [SENAMHI]. Permite buscar estaciones, descargar datos históricos en CSV, revisar archivos locales, resumir periodos, comparar meses o años, validar calidad de datos y recomendar estaciones cercanas a un punto geográfico.

## Video de introducción

<a href="https://www.youtube.com/watch?v=q5I_q8GrOZ0">
  <img src="https://github.com/danyneyra/garua/raw/main/docs/images/youtube-video.jpg" alt="Video de introducción a Garúa en YouTube" width="820">
</a>

Ver en YouTube: [Garúa: CLI y servidor MCP para datos del SENAMHI](https://www.youtube.com/watch?v=q5I_q8GrOZ0)

## Qué puedes hacer

| Tarea | Descripción |
| --- | --- |
| Buscar estaciones | Filtra estaciones por nombre, código, ubicación, tipo, altitud o cercanía a un punto geográfico. |
| Descargar históricos | Obtén datos mensuales, anuales o multianuales en archivos CSV listos para revisar o procesar. |
| Analizar periodos | Resume precipitación, temperatura, humedad, viento o nivel de río según el tipo de estación. |
| Validar calidad | Detecta duplicados, fechas faltantes, valores `S/D`, trazas `T` y otros problemas frecuentes. |

## Formas de uso

Garúa puede usarse de tres maneras:

- **App interactiva:** ejecuta `garua` y navega por un menú en terminal. Es ideal para explorar estaciones y descargar datos paso a paso.
- **Comandos directos:** usa parámetros cuando ya conoces la estación y el periodo, o cuando quieres automatizar búsquedas y descargas.
- **Servidor MCP:** conecta Garúa con VS Code, Claude Desktop, Codex u otros clientes de IA compatibles con [Model Context Protocol].

## Instalación rápida

Requisitos principales:

- Python 3.11+.
- Windows, macOS o Linux.
- Google Chrome, Brave o Microsoft Edge para las descargas desde SENAMHI.

Recomendamos instalarlo con **uv**, que mantiene Garúa y sus dependencias en un
entorno aislado. Si aún no tienes uv, en Windows puedes instalarlo con:

```powershell
winget install --id=astral-sh.uv -e
```

En macOS puedes usar `brew install uv`. Para Linux y otros métodos, consulta la
[instalación oficial de uv](https://docs.astral.sh/uv/getting-started/installation/).
Abre una terminal nueva y ejecuta:

```bash
uv --version
uv tool install garua
```

Si necesitas que uv gestione una versión compatible de Python:

```bash
uv tool install --python 3.13 garua
```

Para actualizar usa `uv tool upgrade garua`. Evita modificar directamente las
dependencias de su entorno. También puedes usar `pipx install garua` o instalar
con pip dentro de un entorno virtual; la guía completa explica las alternativas.

Verifica la instalación:

```bash
garua --health
```

La guía completa está en [Instalación](https://garua.danyneyra.dev/installation/).

¿Prefieres que tu asistente de IA te ayude? Copia el
[prompt de instalación guiada](https://garua.danyneyra.dev/installation/#instalar-con-ayuda-de-un-asistente-de-ia).
Incluye detección del sistema, instalación con uv, comprobaciones y configuración
opcional del cliente MCP.

## Uso rápido

Abre la app interactiva:

```bash
garua
```

<p align="center">
  <img src="https://github.com/danyneyra/garua/blob/main/docs/images/garua-cli-ui.jpg" alt="Interfaz interactiva de Garúa en la terminal" width="820">
</p>

Busca estaciones desde la línea de comandos:

```bash
garua --search Cabana
```

Descarga un mes específico:

```bash
garua --station 108047 --mode month --year 2025 --month 7
```

Ejecuta el servidor MCP:

```bash
garua-mcp
```

> Nota: cuando pidas descargar datos, Garúa abrirá un navegador local para consultar el sitio de SENAMHI y superar la verificación Cloudflare Turnstile cuando aparezca. Esto es esperado en la herramienta de descarga.

## Vista MCP

Garúa también funciona como servidor MCP. Puedes pedir tareas en lenguaje natural y el cliente usa las herramientas de Garúa para buscar estaciones, descargar datos o analizar CSV.

### Codex

<p align="center">
  <img src="https://github.com/danyneyra/garua/blob/main/docs/images/garua-codex.gif" alt="Vista de Garúa MCP en Codex" width="820">
</p>

### Claude Desktop

<p align="center">
  <img src="https://github.com/danyneyra/garua/blob/main/docs/images/garua-claude.gif" alt="Vista de Garúa MCP en Claude Desktop" width="820">
</p>

Ver configuración completa en [Configurar MCP](https://garua.danyneyra.dev/installation/#configurar-mcp) y más ejemplos en [Uso MCP](https://garua.danyneyra.dev/usage/mcp/).

Ejemplos en un cliente MCP:

```text
Busca estaciones meteorológicas en Arequipa sobre 3000 msnm
Recomienda una estación para lat -7.61, lon -77.82 con altitud 3000 msnm
Descarga datos de febrero 2025 de la estación Cabana
Resume diciembre 2025 para la estación 107008
Compara marzo 2025 vs marzo 2026 para Cabana
```

## Documentación

- [Primeros pasos](https://garua.danyneyra.dev/quickstart/)
- [Instalación](https://garua.danyneyra.dev/installation/)
- [Uso CLI](https://garua.danyneyra.dev/usage/cli/)
- [Uso MCP](https://garua.danyneyra.dev/usage/mcp/)
- [Ejemplos completos](https://garua.danyneyra.dev/usage/examples/)
- [Referencia de herramientas MCP](https://garua.danyneyra.dev/reference/tools/)
- [Variables de entorno](https://garua.danyneyra.dev/reference/environment/)
- [Changelog](https://garua.danyneyra.dev/changelog/)

## Guías principales

- [Buscar estaciones](https://garua.danyneyra.dev/guides/buscar-estaciones/)
- [Descargar datos](https://garua.danyneyra.dev/guides/descargar-datos/)
- [Explorar CSV](https://garua.danyneyra.dev/guides/explorar-csv/)
- [Resumir un periodo](https://garua.danyneyra.dev/guides/resumir-periodo/)
- [Comparar periodos](https://garua.danyneyra.dev/guides/comparar-periodos/)
- [Validar calidad de datos](https://garua.danyneyra.dev/guides/validar-datos/)
- [Recomendar estaciones](https://garua.danyneyra.dev/guides/recomendar-estacion/)

## Desarrollo

```bash
git clone https://github.com/danyneyra/garua.git
cd garua
uv sync --locked --extra dev
uv run --locked python -m unittest discover -s scripts -p "test_*.py"
```

`uv.lock` reproduce las dependencias de desarrollo probadas. Para trabajar desde
el repositorio usa `uv run --locked garua` o `uv run --locked garua-mcp`.

Más detalles en [Arquitectura](https://garua.danyneyra.dev/development/architecture/) y [Contribuir](https://garua.danyneyra.dev/development/contributing/).

## Cómo citar Garúa

Si utilizas Garúa en una investigación, tesis, artículo o informe técnico, cita
el software e indica la versión que utilizaste. Los metadatos de citación están
en [CITATION.cff](CITATION.cff).

Para la versión 0.31.0, puedes usar esta referencia:

> Neyra, D. D. (2026). *Garúa: herramienta para consultar y analizar datos hidrometeorológicos del SENAMHI Perú* (versión 0.31.0) \[Software\]. https://github.com/danyneyra/garua

Cita también al **SENAMHI como fuente de los datos** e identifica las estaciones,
las variables, el periodo analizado y la fecha de consulta para facilitar la
reproducibilidad del estudio.

Al publicar una nueva versión de Garúa, actualiza `version` y `date-released` en
`CITATION.cff`, así como la referencia de esta sección.



## Apoya Garúa

Si Garúa te resulta útil, puedes apoyar su desarrollo regalándome un jugo o una
gelatina. ¡Gracias por apoyar el proyecto!

[![Regálame un jugo o una gelatina](docs/images/apoyar-garua.svg)](https://www.paypal.com/donate/?hosted_button_id=XKZDCMX8X99WJ)


## Licencia

Este proyecto se publica bajo los términos de la licencia MIT. Ver [LICENSE](https://github.com/danyneyra/garua/blob/main/LICENSE).
