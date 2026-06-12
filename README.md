<div align="center">
  <a href="https://garua.app/">
    <img alt="Garua logo" src="https://www.garua.app/garua-logo.svg">
  </a>

  <p><strong>Garua</strong> descarga, explora y analiza datos hidrometeorológicos oficiales del SENAMHI Perú.</p>
</div>

> Garúa es la llovizna fina característica de la costa peruana.

[![PyPI](https://img.shields.io/badge/PyPI-1c83ff?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/garua/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-89e240?style=for-the-badge)](https://opensource.org/licenses/MIT)

Garua es una herramienta open source para trabajar con estaciones meteorológicas e hidrológicas del SENAMHI. Permite buscar estaciones, descargar datos históricos en CSV, revisar archivos locales, resumir periodos, comparar meses o años, validar calidad de datos y recomendar estaciones cercanas a un punto geográfico.

Puedes usarlo de tres maneras:

- **CLI interactiva**: ejecuta `garua` y navega por un menú en terminal.
- **CLI con parámetros**: automatiza búsquedas y descargas en una sola línea.
- **Servidor MCP**: integración con clientes como VS Code, Claude Desktop, Codex o cualquier cliente compatible con Model Context Protocol.

## Instalación rápida

Requiere Python 3.11+ (Recomendable 3.13).

```bash
pip install garua
```

Ver la guía completa en [docs/installation.md](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/installation.md).

## Uso rápido

Abrir la app interactiva en terminal:

```bash
garua
```

<p align="center">
  <img src="https://github.com/danyneyra/senamhi-scraper/raw/dev/docs/img/garua-cli-ui.jpg" alt="Interfaz interactiva de Garua en la terminal" width="820">
</p>

También puedes ejecutar acciones directas con parámetros.

Buscar estaciones desde la línea de comandos:

```bash
garua --search Cabana
```

Descargar un mes específico:

```bash
garua --station 108047 --mode month --year 2025 --month 7
```

Ejecutar el servidor MCP:

```bash
garua-mcp
```
> Importante: las descargas abren un navegador local para scrapear el sitio de SENAMHI y superar la verificación Cloudflare Turnstile cuando aparece.

## Preview MCP

Garua también funciona como servidor MCP: puedes pedir tareas en lenguaje natural y el cliente usa las tools de Garua para buscar estaciones, descargar datos o analizar CSV.

### Preview en Codex (ChatGPT)

<p align="center">
  <img src="https://github.com/danyneyra/senamhi-scraper/raw/dev/docs/img/garua-codex.gif" alt="Preview de Garua MCP en Codex" width="820">
</p>

### Preview en Claude Desktop

<p align="center">
  <img src="https://github.com/danyneyra/senamhi-scraper/raw/dev/docs/img/garua-claude.gif" alt="Preview de Garua MCP en Claude Desktop" width="820">
</p>

Ver configuración completa en [docs/installation.md](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/installation.md) y ejemplos en [docs/usage/mcp.md](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/usage/mcp.md).

Ejemplos en un cliente MCP:

```text
Busca estaciones meteorologicas en Arequipa sobre 3000 msnm
Descarga datos de febrero 2025 de la estacion Cabana
Resume diciembre 2025 para la estacion 107008
Compara marzo 2025 vs marzo 2026 para Cabana
Recomienda una estacion para lat -7.61, lon -77.82 con altitud 3000 msnm
```

## Documentación

- [Inicio de documentación](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/index.md)
- [Primeros pasos](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/quickstart.md)
- [Instalación](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/installation.md)
- [Uso CLI](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/usage/cli.md)
- [Uso MCP](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/usage/mcp.md)
- [Ejemplos completos](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/usage/examples.md)
- [Referencia de tools MCP](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/reference/tools.md)

## Guías principales

- [Buscar estaciones](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/buscar-estaciones.md)
- [Descargar datos](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/descargar-datos.md)
- [Explorar CSV](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/explorar-csv.md)
- [Resumir un período](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/resumir-periodo.md)
- [Comparar periodos](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/comparar-periodos.md)
- [Validar calidad de datos](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/validar-datos.md)
- [Recomendar estaciones](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/guides/recomendar-estacion.md)

## Estado del proyecto

Garua esta en fase final antes de una publicacion estable. El paquete ya esta preparado para uso como CLI y servidor MCP, pero las interfaces pueden recibir ajustes menores mientras se ordena la documentacion y se endurecen los flujos principales.

## Desarrollo

```bash
git clone https://github.com/danyneyra/senamhi-scraper.git
cd senamhi-scraper
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Mas detalles en [docs/development/architecture.md](https://github.com/danyneyra/senamhi-scraper/blob/dev/docs/development/architecture.md).

## Licencia

MIT. Ver [LICENSE](https://github.com/danyneyra/senamhi-scraper/blob/dev/LICENSE).
