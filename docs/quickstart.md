# Primeros pasos

Esta guía muestra el camino más corto para instalar Garua, buscar una estación y descargar datos.

## 1. Instala Garua

```bash
pip install garua
```

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

Garua generara archivos CSV en la carpeta de salida configurada por el proyecto.

## 4. Usa Garua con MCP

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

## Siguiente paso

- Para instalacion detallada: [installation.md](installation.md)
- Para comandos CLI: [usage/cli.md](usage/cli.md)
- Para uso con IA via MCP: [usage/mcp.md](usage/mcp.md)
