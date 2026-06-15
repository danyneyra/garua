---
icon: lucide/play
tags:
  - CLI
  - Comandos
---


# Referencia CLI

La CLI se instala como `garua`.

## Comandos principales

```bash
garua --help
garua --version
garua --doctor
garua --search QUERY
garua --station CODIGO --mode month --year ANO --month MES
garua --station CODIGO --mode year --year ANO
garua --station CODIGO --mode period --start ANO --end ANO
```

## Opciones

| Opcion | Uso |
| --- | --- |
| `--version` | Muestra la versión instalada y sale. |
| `--doctor` | Revisa Python, sistema, carpetas de salida y navegador disponible. |
| `--health` | Alias de `--doctor`. |
| `--search QUERY` | Busca estaciones por código exacto o nombre parcial. |
| `--station CODIGO` | Código interno de estación SENAMHI. |
| `--mode month` | Descarga un mes. Requiere `--year` y `--month`. |
| `--mode year` | Descarga un ano. Requiere `--year`. |
| `--mode period` | Descarga un rango. Requiere `--start` y `--end`. |
| `--individual` | Genera un CSV por mes en descargas anuales o por período. |
| `--output DIR` | Directorio de salida para CSV cuando aplique. |

## Recomendación

Usa `garua --search` antes de descargar si no conoces el código exacto de la estación.
