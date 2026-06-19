---
icon: lucide/droplet
title: "Documentación"
---
<style>
.md-content .md-typeset h1 { display: none; }
</style>

<div align="center">
  <a href="https://garua.danyneyra.dev/">
    <img alt="Logo de Garúa" src="images/garua-logo.svg">
  </a>

  <p><strong>Garúa</strong> descarga, explora y analiza datos hidrometeorológicos oficiales del SENAMHI Perú.</p>
</div>

> Garúa es la llovizna fina característica de la costa peruana.

[![PyPI](https://img.shields.io/badge/PyPI-1c83ff?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/garua/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-89e240?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

**Documentación**: [https://garua.danyneyra.dev](https://garua.danyneyra.dev)

**Código fuente**: [https://github.com/danyneyra/garua](https://github.com/danyneyra/garua)

---

Garúa es una herramienta de código abierto para trabajar con estaciones meteorológicas e hidrológicas del [SENAMHI]. Permite buscar estaciones, descargar datos históricos en CSV, revisar archivos locales, resumir periodos, comparar meses o años, validar calidad de datos y recomendar estaciones cercanas a un punto geográfico.

## Video de introducción

<div class="garua-video" markdown="1">
  <iframe src="https://www.youtube.com/embed/q5I_q8GrOZ0" title="Garúa: CLI y servidor MCP para datos del SENAMHI" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## Qué puedes hacer

<div class="grid cards" markdown>

-   :lucide-search: **Buscar estaciones**

    Filtra estaciones por nombre, código, ubicación, tipo, altitud o cercanía a un punto geográfico.

-   :lucide-download: **Descargar históricos**

    Obtén datos mensuales, anuales o multianuales en archivos CSV listos para revisar o procesar.

-   :lucide-chart-line: **Analizar periodos**

    Resume precipitación, temperatura, humedad, viento o nivel de río según el tipo de estación.

-   :lucide-shield-check: **Validar calidad**

    Detecta duplicados, fechas faltantes, valores `S/D`, trazas `T` y otros problemas frecuentes.

</div>

## Elige tu flujo

<div class="grid cards" markdown>

-   :lucide-panel-top: **App interactiva**

    Ejecuta `garua` y navega por un menú en terminal. Es ideal para explorar estaciones y descargar datos paso a paso.

    [Ver uso interactivo](usage/cli.md#app-interactiva){data-preview}

-   :lucide-terminal: **Comandos directos**

    Usa parámetros cuando ya conoces la estación y el periodo, o cuando quieres automatizar búsquedas y descargas.

    [Ver comandos CLI](usage/cli.md#comandos-con-parametros){data-preview}

-   :lucide-sparkles: **Servidor MCP**

    Conecta Garúa con VS Code, Claude Desktop, Codex u otros clientes de IA compatibles con [Model Context Protocol].

    [Ver uso MCP](usage/mcp.md){data-preview}

</div>

[Model Context Protocol]: https://modelcontextprotocol.io/docs/getting-started/intro
[SENAMHI]: https://www.senamhi.gob.pe/?p=estaciones

## Instalación

??? info "Requisitos: Python 3.11+"
    Antes de instalar Garúa, asegúrate de tener Python disponible en tu sistema. Se recomienda usar una versión reciente de [Python] y revisar la guía oficial [Python Setup and Usage] si necesitas ayuda con la instalación.

[Python Setup and Usage]: https://docs.python.org/3/using
[Python]: https://www.python.org/downloads/

??? note "Navegador basado en Chromium"
    Para descargar datos en CSV desde SENAMHI, Garúa necesita abrir un navegador local basado en Chromium, como [Google Chrome], [Brave] o [Microsoft Edge]. En Windows, Microsoft Edge suele venir instalado con el sistema operativo.

[Google Chrome]: https://www.google.com/intl/es_es/chrome/safety/
[Brave]: https://brave.com/es/download/
[Microsoft Edge]: https://www.microsoft.com/es-es/edge/download


Con Python instalado, ejecuta este comando desde tu :material-console: terminal [^1]:

[^1]:
    Puedes usar terminales como PowerShell, CMD, Warp, etc.

<div class="garua-terminal" data-garua-terminal aria-label="Instalación rápida" data-type-speed="80" data-progress-speed="30">
  <div class="garua-terminal__bar">
    <span class="garua-terminal__dot" aria-hidden="true"></span>
    <span class="garua-terminal__dot" aria-hidden="true"></span>
    <span class="garua-terminal__dot" aria-hidden="true"></span>
    <span class="garua-terminal__title">Powershell</span>
  </div>
  <pre><code><span data-line data-type="input">pip install garua</span>
</code><span data-line data-type="progress" data-progress-label=" " style="padding-left: 1.5rem; padding-bottom: 0.5rem" data-progress-blocks="32">████████████████████████████████ 100%</span></pre>
  <button class="garua-terminal__replay" type="button" data-terminal-replay aria-label="Reiniciar animación">reiniciar ↻</button>
</div>

Ver la guía completa de [Instalación](installation.md#instalar-desde-pypi){data-preview}.

## Uso rápido

Abre la app interactiva:

<div class="garua-terminal" data-garua-terminal markdown="1" data-type-speed="80" data-line-delay="320">

```console
$ garua

 ╭─── Garúa v0.30.0 ───────────────────────────────────╮
 │                                                     │
 │  GARUA                                              │
 │  Datos meteorológicos e hidrológicos                │
 │  del SENAMHI del Perú                               │
 │  Consulta estaciones. Descarga históricos           │
 │                                                     │
 ╰─────────────────────────────────────────────────────╯
 ───────────────────────────────────────────────────────
 BÚSQUEDA DE ESTACIÓN
 ───────────────────────────────────────────────────────
 💧 Código o nombre (ej: 472D30C8 o SIHUAS): 

```
</div>

Si todo se ejecutó correctamente, ya puedes usar Garúa 🎉

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


## Vista MCP

Garúa también funciona como servidor MCP: puedes pedir tareas en lenguaje natural y el cliente usa las herramientas de Garúa para buscar estaciones, descargar datos o analizar CSV.
Puedes ver la configuración completa en [Configurar MCP](installation.md#configurar-mcp){data-preview} y más ejemplos en [Uso MCP](usage/mcp.md){data-preview}.

!!! info "Nota sobre descargas"
    Cuando pidas descargar datos, Garúa abrirá un navegador local para consultar el sitio de SENAMHI y superar la verificación Cloudflare Turnstile cuando aparezca. Esto es esperado en la herramienta de descarga.



=== ":fontawesome-brands-openai: Codex"
    ![Vista de Garúa MCP en Codex](images/garua-codex.gif)

    Puedes descargarlo desde la web oficial de [Codex](https://openai.com/es-419/codex/).

=== ":fontawesome-brands-claude: Claude Desktop"
    ![Vista de Garúa MCP en Claude Desktop](images/garua-claude.gif)

    Puedes descargarlo desde la web oficial de [Claude Desktop](https://claude.com/download).



Ejemplos en un cliente MCP:

```text
Busca estaciones meteorológicas en Arequipa sobre 3000 msnm
Recomienda una estación para lat -7.61, lon -77.82 con altitud 3000 msnm
Descarga datos de febrero 2025 de la estación Cabana
Resume diciembre 2025 para la estación 107008
Compara marzo 2025 vs marzo 2026 para Cabana
```


## Siguientes pasos

<div class="grid cards" markdown>

-   :lucide-rocket: **Primeros pasos**

    Sigue el camino corto para instalar Garúa, buscar una estación y descargar tu primer CSV.

    [Ir a primeros pasos](quickstart.md){data-preview}

-   :lucide-book-open: **Guías de uso**

    Revisa flujos concretos para buscar estaciones, descargar datos, explorar CSV y analizar periodos.

    [Ver guías](guides/buscar-estaciones.md){data-preview}

-   :lucide-code-xml: **Desarrollo**

    Consulta la arquitectura del proyecto si quieres contribuir o entender cómo está organizado Garúa.

    [Ver arquitectura](development/architecture.md){data-preview}

</div>


## Licencia

Este proyecto se publica bajo los términos de la licencia MIT.

