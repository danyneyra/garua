# Instalación

Garua puede instalarse como herramienta CLI y como servidor MCP. La instalación base es la misma; lo que cambia es como lo conectas a tu flujo de trabajo.

## Requisitos

- Python 3.11+ (Recomendable 3.13).
- Windows, macOS o Linux.
- Acceso a internet para instalar el paquete y descargar datos desde SENAMHI.
- Un cliente MCP si quieres usar Garua desde un asistente compatible.

## Instalar desde PyPI

```bash
pip install garua
```

Verifica que los comandos estén disponibles:

```bash
garua --help
garua-mcp
```

## Instalar para desarrollo

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

## Configurar MCP

Garua funciona como servidor MCP local por `stdio`. La forma más simple es usar el comando instalado:

```bash
garua-mcp
```

Si el cliente no encuentra `garua-mcp`, usa una ruta absoluta al ejecutable o al Python de tu entorno virtual:

```text
D:\garua\.venv\Scripts\python.exe -m garua.mcp_server
```

### VS Code con GitHub Copilot

VS Code puede configurar servidores MCP en el perfil de usuario o en el workspace. Para compartir la configuración con un equipo, usa `.vscode/mcp.json` dentro del proyecto. Para uso personal, abre la configuración desde la paleta de comandos con `MCP: Open User Configuration`.

Ejemplo recomendado para `.vscode/mcp.json`:

```json
{
  "servers": {
    "garua": {
      "type": "stdio",
      "command": "garua-mcp"
    }
  }
}
```

Si usas entorno virtual:

```json
{
  "servers": {
    "garua": {
      "type": "stdio",
      "command": "D:\\garua\\.venv\\Scripts\\python.exe",
      "args": ["-m", "garua.mcp_server"]
    }
  }
}
```

Recomendaciones:

- Usa configuración de usuario si Garua estará disponible en todos tus proyectos.
- Usa `.vscode/mcp.json` si quieres que el proyecto documente o comparta su servidor MCP.
- Revisa el panel de MCP Servers en VS Code para iniciar, detener o ver logs del servidor.

### Claude Desktop

Claude Desktop usa `claude_desktop_config.json`.

Ubicaciones comunes:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Configuración recomendada:

```json
{
  "mcpServers": {
    "garua": {
      "command": "garua-mcp"
    }
  }
}
```

Si usas entorno virtual:

```json
{
  "mcpServers": {
    "garua": {
      "command": "D:\\garua\\.venv\\Scripts\\python.exe",
      "args": ["-m", "garua.mcp_server"]
    }
  }
}
```

Recomendaciones:

- Reinicia Claude Desktop después de editar el archivo.
- Si Claude no detecta Garua, usa rutas absolutas.
- Evita configurar servidores MCP que no conoces o no confías.

### Codex

Codex registra servidores MCP desde su archivo `config.toml`.

Configuración sugerida:

```toml
[mcp_servers.garua]
enabled = false
command = 'garua-mcp'
```

Usa `enabled = true` cuando quieras dejar Garua activo por defecto.

Si usas entorno virtual:

```toml
[mcp_servers.garua]
enabled = false
command = 'D:\garua\.venv\Scripts\python.exe'
args = ['-m', 'garua.mcp_server']
```

Recomendaciones:

- Mantén `enabled = false` si solo quieres activarlo cuando lo necesites.
- Usa `enabled = true` si Garua será parte habitual de tu flujo con datos SENAMHI.
- Prefiere rutas absolutas cuando Codex no herede el mismo `PATH` de tu terminal.

### Otros clientes MCP

Muchos clientes compatibles usan una variante de configuración con nombre del servidor, comando y argumentos.

Configuración base:

```json
{
  "mcpServers": {
    "garua": {
      "command": "garua-mcp"
    }
  }
}
```

Si el cliente usa el formato de VS Code, cambia `mcpServers` por `servers` y agrega `type: "stdio"`.

Recomendaciones:

- Confirma si tu cliente espera JSON, TOML o configuración desde interfaz gráfica.
- Usa `garua-mcp` si instalaste desde PyPI.
- Usa `python -m garua.mcp_server` si trabajas desde el código fuente.
- Reinicia el cliente después de cambiar la configuración.

## Validación

Cuando el servidor este conectado, prueba:

```text
Cuántas estaciones SENAMHI tienes disponibles?
Busca estaciones llamadas Cabana
```

Si el cliente responde usando Garua, la instalación esta lista.

## Problemas comunes

- Si `garua` no existe, revisa que el directorio de scripts de Python este en el `PATH`.
- Si el cliente MCP no encuentra el comando, usa la ruta absoluta al ejecutable o al Python del entorno virtual.
- Si la descarga falla por red o cambios del sitio de SENAMHI, vuelve a intentar y revisa si hay issues abiertos en el repositorio.
