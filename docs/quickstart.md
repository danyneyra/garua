---
icon: lucide/package-open
tags:
  - Primeros pasos

---

# Primeros pasos

Esta guía muestra el camino más corto para instalar Garúa, buscar una estación y descargar datos.

## 1. Instala Garúa

<div class="garua-terminal" data-garua-terminal markdown="1" aria-label="Instalación rápida de Garúa en terminal">

```console
$ pip install garua
████████████████████████████████ 100%

$ garua --doctor
OK Python 3.11+
OK Navegador compatible encontrado

$ garua --search Cabana
Cabana | código 108047 | Meteorológica | Áncash
```

</div>

## 2. Busca una estación

Puedes iniciar la app interactiva:

```bash
garua
```

O usar parámetros directos:

```bash
garua --search Cabana
```

Anota el código interno de la estación que quieras usar. Si hay varias coincidencias, elige la que tenga departamento, provincia y tipo adecuados para tu caso.

## 3. Descarga datos

```bash
garua --station 108047 --mode month --year 2025 --month 7
```

Garúa generara archivos CSV en la carpeta de salida configurada por el proyecto.

## 4. Usa Garúa con MCP

Ejecuta:

```bash
garua-mcp
```

O configura tu cliente MCP para llamar ese comando. Luego puedes pedir:

```text
Busca estaciones meteorologicas en Cajamarca
Descarga julio 2025 de la estacion 108047
Resume los datos descargados de julio 2025 para esa estacion
```

## Siguientes pasos

<div class="grid cards" markdown>

-   :lucide-rocket: **Instalación detallada**

    Revisa información detalla de como instalar y configurar Garúa en tu sistema y en tu MCP cliente.

    [Ir a Instalación](installation.md){data-preview}

-   :lucide-square-terminal: **Uso CLI**

    Revisa el uso de Garúa vía CLI: App interactiva y comandos.

    [Ver Uso de CLI](usage/cli.md){data-preview}

-   :lucide-server: **Uso MCP**

    Revisa el uso de Garúa vía MCP Server, puedes usarlo en tu cliente de IA favorito.

    [Ver Uso en MCP](usage/mcp.md){data-preview}

</div>