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

Instala Garúa desde PyPI:

```bash
pip install garua
```

También puedes instalarlo con `pipx` si quieres usarlo como herramienta global de terminal:

```bash
pipx install garua
```

Verifica la instalación:

```bash
garua --help
garua --doctor
```

La guía completa está en [Instalación](https://garua.danyneyra.dev/installation/).

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
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Más detalles en [Arquitectura](https://garua.danyneyra.dev/development/architecture/) y [Contribuir](https://garua.danyneyra.dev/development/contributing/).

## Licencia

Este proyecto se publica bajo los términos de la licencia MIT. Ver [LICENSE](https://github.com/danyneyra/garua/blob/main/LICENSE).

[Model Context Protocol]: https://modelcontextprotocol.io/docs/getting-started/intro
[SENAMHI]: https://www.senamhi.gob.pe/?p=estaciones
