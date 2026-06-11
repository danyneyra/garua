# Uso MCP

El servidor MCP permite usar Garua desde clientes compatibles con Model Context Protocol. Es ideal cuando quieres pedir tareas en lenguaje natural y dejar que el cliente llame las tools correctas.

## Ejecutar servidor

```bash
garua-mcp
```

## Configuración básica

```json
{
  "mcpServers": {
    "garua": {
      "command": "garua-mcp"
    }
  }
}
```

Si el cliente no encuentra el comando, usa la ruta absoluta al ejecutable o al Python del entorno virtual.

## Prompts útiles

```text
Busca estaciones meteorologicas en Arequipa sobre 3000 msnm
Que estaciones hay cerca de lat -7.61, lon -77.82?
Descarga datos de julio 2025 de la estacion Cabana
Resume julio 2025 para la estacion 108047
Compara marzo 2025 vs marzo 2026 para Cabana
Valida la calidad de datos de julio 2025 para la estacion 108047
```

## Flujo recomendado

1. Busca o filtra estaciones.
2. Confirma el código de estación.
3. Revisa disponibilidad histórica si necesitas un período específico.
4. Descarga los datos si aún no existen localmente.
5. Resume, compara o valida calidad según tu objetivo.

## Referencia técnica

La lista completa de tools esta en [../reference/tools.md](../reference/tools.md). Esa referencia se genera desde los docstrings del código para mantenerla sincronizada con el servidor.
