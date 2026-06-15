---
icon: lucide/play
tags:
  - Uso
  - CLI
  - Comandos
---

# Uso CLI

La CLI sirve para buscar estaciones y descargar datos desde una terminal. Puedes usarla como app interactiva con menú o como comando directo con parámetros.

## App interactiva

Ejecuta Garúa sin argumentos:

```bash
garua
```

Esto abre una interfaz en terminal que te guía paso a paso para:

- Buscar o seleccionar una estación.
- Elegir modo de descarga: mes, año o período.
- Definir fechas.
- Generar archivos CSV.

![Interfaz interactiva de Garua en la terminal](../images/garua-cli-ui.jpg)

Usa este modo cuando estas explorando o prefieres que Garúa te pregunte los datos necesarios.

## Comandos con parámetros

Usa parámetros cuando ya sabes que estación y período necesitas, o cuando quieres automatizar una descarga.

!!! info "Referencia de CLI"
    Puedes ver la tabla de comandos en [Referencia de CLI](../reference/cli.md#opciones){data-preview}

### Ver ayuda

```bash
garua --help
```

### Ver versión

```bash
garua --version
```

### Buscar estaciones

```bash
garua --search Cabana
garua --search 108047
```

Usa la búsqueda antes de descargar si no conoces el código interno de la estación.

### Descargas Csv

!!! info "Navegador local"
    Para descargar datos, Garúa abre un navegador local y consulta el portal de [SENAMHI]. Esto también permite completar la verificación de Cloudflare Turnstile cuando aparece.

[SENAMHI]: https://www.senamhi.gob.pe/?p=estaciones

### Descargar un mes

```bash
garua --station 108047 --mode month --year 2025 --month 7
```

### Descargar un año completo

```bash
garua --station 108047 --mode year --year 2025
```

!!! info "Archivo consolidado"
    Por defecto se descargará todo el año en un archivo CSV consolidado de todos los meses. Si deseas descargarlo en archivos independientes (un archivo CSV por mes) debes usar **--individual**

Para generar un CSV por mes:

```bash
garua --station 108047 --mode year --year 2025 --individual
```

### Descargar un rango de años

```bash
garua --station 108047 --mode period --start 2020 --end 2025
```

## Salida

!!! info "Carpeta de salida"
    Por defecto, los archivos se guardan en la carpeta Documentos del usuario. En Windows, la ruta es `C:\Users\TuUsuario\Documents\Garua\csv`.

    Si deseas cambiar la carpeta de salida, define la variable de entorno `GARUA_OUTPUT_DIR` con la ruta que quieras usar. Para más detalles de la configuración de variables de entorno en [Variables de Entorno](../reference/environment.md){data-preview}

Garua guarda los CSV en la carpeta de salida configurada. Los nombres incluyen estación y período, por ejemplo:

```text
Cabana-202507.csv
Cabana-2025.csv
Cabana-2020-2025.csv
```


Ver más detalles en [Archivos de Salida](../reference/output-files.md){data-preview}.
