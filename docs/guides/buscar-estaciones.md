# Buscar estaciones

## Qué resuelve

Ayuda a encontrar estaciones SENAMHI por nombre, código, ubicación, altitud o cercanía a coordenadas.

## Cuándo usarlo

Úsalo antes de descargar, resumir o comparar datos si no tienes confirmado el código interno de la estación.

## Ejemplo rápido

CLI:

```bash
garua --search Cabana
```

MCP:

```text
Busca estaciones meteorologicas en Cajamarca llamadas Cabana
```

## Flujo recomendado

1. Busca por nombre o código.
2. Si hay varias coincidencias, revisa departamento, provincia, distrito, tipo y categoría.
3. Confirma el código interno.
4. Usa ese código en descargas, resúmenes o validaciones.

## Resultado esperado

Una lista de estaciones con nombre, código, tipo, categoria, estado, coordenadas, altitud y disponibilidad histórica.

## Problemas comunes

- Si el nombre devuelve muchas coincidencias, agrega departamento o provincia.
- Si necesitas cercanía real, usa coordenadas en vez de solo distrito.
- Si vas a analizar un período antiguo, revisa disponibilidad antes de descargar.
