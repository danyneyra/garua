# 🌐 Instalación de Garúa como Servidor MCP

Este servidor MCP funciona con **cualquier cliente compatible con el protocolo MCP**, incluyendo:
- 🔷 **VS Code** (con GitHub Copilot)
- 🔶 **Claude Desktop** (Anthropic)
- 🟣 **Codex (con GPT)**
- 🔵 **Otros clientes MCP**

## 🔑 Concepto Clave

**La instalación del servidor es la misma para todos los clientes**, solo cambia el archivo de configuración:

1. **Paso común:** `pip install garua` (instala el servidor una vez)
2. **Paso específico:** Configurar el cliente que uses (VS Code, Claude Desktop, etc.)

---

## 📋 Requisitos Previos

- **Python 3.11+** instalado
- **Cliente MCP** de tu elección (VS Code, Claude Desktop, etc.)
- **Windows, macOS o Linux**

---

## 🚀 Instalación del Servidor (Común para Todos)

### 1️⃣ Instalar el paquete

```bash
pip install garua
```

Esto instalará automáticamente:
- El servidor MCP
- Todas las dependencias (zendriver, beautifulsoup4, fastmcp, etc.)
- Herramientas de línea de comandos

✅ **Listo** - El servidor ya está instalado en tu sistema. Ahora configura tu cliente específico:

✅ **Listo** - El servidor ya está instalado en tu sistema. Ahora configura tu cliente específico:

---

## ⚙️ Configuración por Cliente

### 🔷 **Opción A: VS Code + GitHub Copilot**

**1. Ubicación del archivo de configuración:**

- **Windows:** `%APPDATA%\Code\User\mcp.json`  
- **macOS/Linux:** `~/.config/Code/User/mcp.json`

**2. Contenido del archivo:**

```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**3. Si usas virtualenv específico:**

```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "C:\\ruta\\a\\tu\\.venv\\Scripts\\python.exe",
      "args": ["d:\\DEV\\senamhi-scraper\\mcp_server.py"]
    }
  }
}
```

**4. Reiniciar VS Code:**

Presiona `Ctrl+Shift+P` → **"Developer: Reload Window"**

**5. Usar en Copilot Chat:**

```
@garua ¿cuántas estaciones tienes disponibles?
```

---

### 🔶 **Opción B: Claude Desktop (Anthropic)**

**1. Ubicación del archivo de configuración:**

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**2. Contenido del archivo:**

```json
{
  "mcpServers": {
    "garua": {
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```
**Nota:** Claude Desktop usa el mismo formato que VS Code, solo cambia la ubicación del archivo.

**3. Reiniciar Claude Desktop**

Cierra y vuelve a abrir la aplicación.

**4. Verificar conexión:**

En Claude Desktop verás un ícono de herramientas (🔧) que indica servidores MCP conectados. Click para ver las 16 tools disponibles.

**5. Usar en el chat:**

```
¿Qué estaciones meteorológicas hay en Cajamarca?
```

---

### 🟣 **Opción C: Codex (con GPT)**

**1. Ubicación del archivo de configuración:**

- **Windows:** `%USERPROFILE%\.codex\config.toml`
- **macOS/Linux:** `~/.codex/config.toml`

**2. Contenido del archivo:**

```toml
[mcp_servers.garua]
command = 'python'
args = ['-m', 'mcp_server']

[mcp_servers.garua.env]
PYTHONUTF8 = "1"
```



---

### 🔶 **Opción C: Cursor IDE**

**1. Ubicación del archivo de configuración:**

Similar a VS Code:
- **Windows:** `%APPDATA%\Cursor\User\mcp.json`
- **macOS/Linux:** `~/.config/Cursor/User/mcp.json`

**2. Configuración:**

```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**3. Reiniciar Cursor**

---

### 🔵 **Opción D: Otros Clientes MCP**

Cualquier cliente que soporte el protocolo MCP puede usar este servidor. La configuración general es:

```json
{
  "type": "stdio",
  "command": "python",
  "args": ["-m", "mcp_server"]
}
```

O con ruta absoluta al servidor:

```json
{
  "type": "stdio", 
  "command": "/ruta/a/python",
  "args": ["/ruta/a/mcp_server.py"]
}
```

---

## ✅ Verificación de Instalación

### Para todos los clientes:

Una vez configurado, deberías poder:

1. **Ver las herramientas disponibles** (16 tools en total)
2. **Hacer consultas** sobre estaciones SENAMHI
3. **Descargar datos** históricos

### Ejemplo de prueba universal:

```
¿Cuántas estaciones meteorológicas tienes disponibles?
```

Respuesta esperada: "Tengo 880 estaciones SENAMHI disponibles..." (o el número actualizado)

---

## 🎯 Herramientas Disponibles

Una vez instalado, tendrás acceso a 16 herramientas organizadas en 4 categorías:

### 🔍 Búsqueda y filtrado (7 tools)
- `search_stations` - Buscar estaciones por nombre
- `get_station_info` - Detalles de una estación específica
- `find_stations_near` - Estaciones cercanas a coordenadas
- `filter_stations_by_location` - Filtrar por departamento/provincia/distrito
- `filter_stations_by_altitude` - Filtrar por rango de altitud
- `check_data_availability` - Consultar disponibilidad de datos históricos
- `filter_stations_advanced` - Filtro combinado multi-criterio

### 📊 Estadísticas (5 tools)
- `stations_count` - Conteo total de estaciones
- `stations_summary` - Resumen por tipo y estado
- `get_all_stations` - Lista completa de estaciones
- `get_departments_summary` - Estadísticas por departamento
- `get_location_hierarchy` - Estructura jerárquica de ubicaciones

### 📁 Gestión de archivos (3 tools)
- `list_downloaded_files` - Listar CSVs descargados (con filtros opcionales)
- `read_csv_preview` - Vista previa de archivos CSV
- `extract_month_from_csv` - Extraer mes específico de archivo consolidado

### ⬇️ Descarga (1 tool)
- `scrape_station_data` - Descargar datos históricos del SENAMHI

## 📖 Ejemplos de Uso

Los ejemplos varían ligeramente según el cliente:

### 🔷 **En VS Code (GitHub Copilot)**

Usa `@garua` para invocar el servidor:

```
@garua busca estaciones meteorológicas en Cajamarca
@garua descarga los datos de enero 2025 de la estación Cabana
@garua muéstrame los archivos CSV que tengo descargados
```

### 🟣 **En Claude Desktop**

Pregunta directamente (Claude detecta automáticamente):

```
¿Qué estaciones meteorológicas hay en Cajamarca sobre 3000 msnm?
Descarga datos de febrero 2025 de la estación Cabana
Lista los archivos CSV que ya tengo descargados
```

### 🔶 **En Cursor IDE**

Similar a VS Code, puedes usar menciones o preguntar directamente:

```
@garua busca estaciones en Arequipa
¿Qué datos históricos tengo descargados?
```

---

## 🔧 Solución de Problemas

### Error: "No se encuentra el módulo" o "Module not found"

**Causa:** El paquete no está instalado o no está en el PATH de Python.

**Solución:**

1. Verifica la instalación:
   ```bash
   pip show garua
   ```

2. Si no aparece, instálalo:
   ```bash
   pip install garua
   ```

3. Verifica que estés usando el Python correcto:
   ```bash
   which python    # Linux/Mac
   where python    # Windows
   ```

### Error: "Command not found: python"

**Causa:** Python no está en el PATH o se llama diferente en tu sistema.

**Solución:** Usa `python3` en lugar de `python`:

```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

O usa la ruta absoluta:

```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "C:\\Python311\\python.exe",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

### El servidor no aparece en el cliente

**Para VS Code:**
1. Verifica que el archivo `mcp.json` esté en la ubicación correcta
2. Reinicia completamente VS Code (`Ctrl+Shift+P` → "Developer: Reload Window")
3. Revisa la consola: `Help` → `Toggle Developer Tools` → pestaña `Console`

**Para Claude Desktop:**
1. Verifica la ubicación de `claude_desktop_config.json`
2. Cierra completamente Claude Desktop y vuelve a abrirlo
3. Busca el ícono de herramientas (🔧) en la interfaz

**Para otros clientes:**
1. Verifica la sintaxis del archivo de configuración (debe ser JSON válido)
2. Reinicia el cliente
3. Consulta la documentación específica del cliente

### El servidor se conecta pero no responde

**Causa:** Posible error en el código del servidor o dependencias faltantes.

**Solución:**

1. Prueba ejecutar el servidor manualmente:
   ```bash
   python -m mcp_server
   ```

2. Si hay errores, reinstala las dependencias:
   ```bash
   pip uninstall garua
   pip install garua
   ```

### Error de permisos en Windows

**Causa:** Python instalado desde Microsoft Store tiene restricciones.

**Solución:**
1. Instala Python desde [python.org](https://python.org) en lugar de Microsoft Store
2. O usa la ruta completa al ejecutable de Python en el virtualenv


---

## 🌐 Instalación para Desarrollo

Si deseas contribuir al proyecto o hacer modificaciones locales:

```bash
# Clonar el repositorio
git clone https://github.com/danyneyra/senamhi-scraper.git
cd senamhi-scraper

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e ".[dev]"
```

### Configurar el cliente para usar tu versión local

En lugar de `python -m mcp_server`, usa la ruta absoluta:

**VS Code (mcp.json):**
```json
{
  "mcpServers": {
    "garua": {
      "type": "stdio",
      "command": "D:\\DEV\\garua\\.venv\\Scripts\\python.exe",
      "args": ["D:\\DEV\\garua\\mcp_server.py"]
    }
  }
}
```

**Claude Desktop (claude_desktop_config.json):**
```json
{
  "mcpServers": {
    "garua": {
      "command": "D:\\DEV\\garua\\.venv\\Scripts\\python.exe",
      "args": ["D:\\DEV\\garua\\mcp_server.py"]
    }
  }
}
```

**Nota:** Ajusta las rutas según tu sistema operativo (usa `/` en Linux/Mac).

---

## 📦 Archivos de Salida

Los datos descargados se guardan en:

```
output/
└── csv/
    ├── NombreEstacion/
    │   ├── NombreEstacion-202501.csv     # Datos de un mes
    │   ├── NombreEstacion-2025.csv       # Datos de un año
    │   └── NombreEstacion-2020-2025.csv  # Datos de un periodo
```

## 📄 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Soporte

- 🐛 **Reportar bugs:** [GitHub Issues](https://github.com/danyneyra/senamhi-scraper/issues)
- 💬 **Preguntas:** [GitHub Discussions](https://github.com/danyneyra/senamhi-scraper/discussions)
- 📧 **Contacto:** danydanieln@hotmail.com

---

**¿Necesitas ayuda?** Abre un issue en GitHub o contáctame directamente.
