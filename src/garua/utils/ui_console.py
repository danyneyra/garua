"""
Módulo de interfaz de consola profesional con Rich.
Proporciona elementos visuales mejorados para el scraper de SENAMHI.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TaskProgressColumn,
)
from rich.text import Text
from rich import box
from rich.markup import escape
from rich.theme import Theme
from typing import List
from garua.models.station import Station
from garua.settings import VERSION

GARUA_PRIMARY = "#6469e3"
GARUA_ACCENT = "#8b9ce5"
PANEL_PADDING = (1, 2)
FULL_LOGO_MIN_WIDTH = 42
GARUA_LOGO = "\n".join(
    [
        " ██████   █████  ██████  ██   ██  █████ ",
        "██       ██   ██ ██   ██ ██   ██ ██   ██",
        "██  ███  ███████ ██████  ██   ██ ███████",
        "██   ██  ██   ██ ██   ██ ██   ██ ██   ██",
        " ██████  ██   ██ ██   ██  █████  ██   ██",
    ]
)
GARUA_LOGO_FALLBACK = r"""
  ____    _    ____  _   _    _
 / ___|  / \  |  _ \| | | |  / \
| |  _  / _ \ | |_) | | | | / _ \
| |_| |/ ___ \|  _ <| |_| |/ ___ \
 \____/_/   \_\_| \_\\___//_/   \_\
""".strip()
GARUA_COMPACT_LOGO = "GARUA"

# Tema personalizado Garúa con color principal #6469e3
garua_theme = Theme(
    {
        "info": GARUA_PRIMARY,
        "primary": GARUA_PRIMARY,
        "accent": GARUA_ACCENT,
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "processing": GARUA_PRIMARY,
    }
)

# Consola global configurada con tema Garúa
console = Console(theme=garua_theme)


class UIConsole:
    """Interfaz de usuario mejorada para la consola del scraper"""

    def __init__(self):
        self.console = console

    def _primary(self, text: str, *, bold: bool = False) -> str:
        """Aplica el color principal de Garúa a texto con markup Rich."""
        safe_text = escape(str(text))
        weight = "bold " if bold else ""
        return f"[{weight}{GARUA_PRIMARY}]{safe_text}[/{weight}{GARUA_PRIMARY}]"

    def _label(self, text: str) -> str:
        """Formatea una etiqueta de campo."""
        return self._primary(f"{text}:", bold=True)

    def _title(self, text: str, icon: str = "") -> str:
        """Formatea títulos de paneles y tablas."""
        title = f"{icon} {text}" if icon else text
        return self._primary(title, bold=True)

    def _panel(
        self,
        renderable,
        title: str,
        *,
        icon: str = "",
        panel_box=box.ROUNDED,
        padding=PANEL_PADDING,
    ) -> Panel:
        """Crea paneles consistentes y responsivos al ancho de consola."""
        return Panel(
            renderable,
            title=self._title(title, icon),
            title_align="left",
            border_style=GARUA_PRIMARY,
            box=panel_box,
            expand=True,
            padding=padding,
        )

    def _status(self, icon: str, message: str, style: str) -> str:
        """Formatea mensajes cortos de estado."""
        return f"[{style}]{icon} {escape(str(message))}[/{style}]"

    def prompt(self, text: str, icon: str = "💧") -> str:
        """Formatea prompts interactivos del CLI."""
        prompt_text = f"{icon} {text}" if icon else text
        return self._primary(prompt_text, bold=True)

    def _section_width(self) -> int:
        """Calcula el ancho estable para separadores de sección."""
        return max(20, self.console.width - 2)

    def _content_width(self) -> int:
        """Ancho aproximado disponible dentro de paneles y mensajes."""
        return max(20, self.console.width - 8)

    def _fit_text(self, text: str, max_width: int) -> str:
        """Recorta texto largo para evitar deformar layouts estrechos."""
        clean_text = str(text)
        if len(clean_text) <= max_width:
            return clean_text
        if max_width <= 3:
            return clean_text[:max_width]
        return f"{clean_text[: max_width - 3]}..."

    def _format_bytes(self, bytes_count: int) -> str:
        """Formatea bytes de forma compacta para mensajes de estado."""
        if bytes_count < 1024:
            return f"{bytes_count:,} B"
        if bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.1f} KB"
        return f"{bytes_count / (1024 * 1024):.1f} MB"

    def _build_station_table(
        self,
        stations: List[Station],
        query: str,
        *,
        numbered: bool = False,
    ) -> Table:
        """Construye una tabla de estaciones según el ancho actual."""
        compact = self.console.width < 60
        very_compact = self.console.width < 40
        table_title = (
            f"Búsqueda: '{query}'" if compact else f"Resultados de búsqueda: '{query}'"
        )

        table = Table(
            title=self._title(table_title, "💧"),
            show_header=True,
            header_style=f"bold {GARUA_PRIMARY}",
            border_style=GARUA_PRIMARY,
            box=box.ROUNDED,
            expand=True,
        )

        if numbered:
            table.add_column("#", justify="right", style=GARUA_PRIMARY, no_wrap=True)
        table.add_column("Código", style=GARUA_PRIMARY, no_wrap=True)
        table.add_column("Nombre", style="white", overflow="ellipsis")
        if not very_compact:
            table.add_column("Estado", style="yellow", no_wrap=True)
        if not compact:
            table.add_column("Tipo", style="magenta", no_wrap=True)
            table.add_column("Ubicación", style="green", overflow="ellipsis")

        for index, station in enumerate(stations, 1):
            location_parts = []
            if station.district:
                location_parts.append(station.district)
            if station.province:
                location_parts.append(station.province)
            if station.department:
                location_parts.append(station.department)
            location = ", ".join(location_parts) if location_parts else "N/A"

            row = []
            if numbered:
                row.append(str(index))
            row.extend([station.code, station.name])
            if not very_compact:
                row.append(station.status or "N/A")
            if not compact:
                row.extend([station.station_type or "N/A", location])

            table.add_row(*row)

        return table

    def _get_logo(self, available_width: int) -> str:
        """Devuelve el logo compatible con la codificación de la consola."""
        if available_width < FULL_LOGO_MIN_WIDTH:
            return GARUA_COMPACT_LOGO

        encoding = getattr(self.console.file, "encoding", None) or "utf-8"
        try:
            GARUA_LOGO.encode(encoding)
        except UnicodeEncodeError:
            return GARUA_LOGO_FALLBACK

        return GARUA_LOGO

    def print_welcome(self):
        """Muestra mensaje de bienvenida con el logo Garúa"""
        content_width = max(self.console.width - 3, 0)
        welcome_text = Text()
        welcome_text.append(
            self._get_logo(content_width), style=f"bold {GARUA_PRIMARY}"
        )
        welcome_text.append("\n\n")
        welcome_text.append("Datos meteorológicos e hidrológicos\n", style="dim")
        welcome_text.append("del SENAMHI del Perú.\n\n", style="dim")
        welcome_text.append(
            "Consulta estaciones. Descarga históricos.\n", style="white"
        )
        welcome_text.append(
            "Trabaja con datos confiables.", style=f"bold {GARUA_PRIMARY}"
        )

        self.console.print()
        welcome_panel = self._panel(
            welcome_text,
            f"Garúa v{VERSION}",
        )
        self.console.print(welcome_panel)
        self.console.print()

    def print_station_found(self, station: Station):
        """Muestra información de la estación encontrada"""
        code_display = station.code
        if station.frontend_code and station.frontend_code != station.code:
            code_display += f" | {station.frontend_code}"
        info = (
            f"{self._label('Nombre')} {escape(str(station.name))}\n"
            f"{self._label('Código')} {escape(str(code_display))}\n"
            f"{self._label('Tipo')} {escape(str(station.station_type))}\n"
            f"{self._label('Estado')} {escape(str(station.status))}\n"
            f"{self._label('Categoría')} {escape(str(station.category))}\n"
        )

        if station.department:
            info += f"{self._label('Departamento')} {escape(str(station.department))}\n"
        if station.province:
            info += f"{self._label('Provincia')} {escape(str(station.province))}\n"
        if station.district:
            info += f"{self._label('Distrito')} {escape(str(station.district))}\n"

        info += f"{self._label('Datos disponibles desde')} {escape(str(station.data_available_since))}\n"

        panel = self._panel(
            info.strip(),
            "Estación Seleccionada",
            icon="💧",
        )
        self.console.print(panel)

    def print_search_results(self, stations: List[Station], query: str):
        """Muestra resultados de búsqueda en una tabla elegante"""
        if not stations:
            self.console.print(
                f"\n[yellow]⚠️  No se encontraron estaciones para: [bold]{escape(str(query))}[/bold][/yellow]\n"
            )
            return

        very_compact = self.console.width < 40
        table = self._build_station_table(stations, query)

        self.console.print()
        self.console.print(table)
        total_text = (
            f"Total: {len(stations)}"
            if very_compact
            else f"Total: {len(stations)} estación(es) encontrada(s)"
        )
        self.console.print(f"\n[dim]{total_text}[/dim]\n")

    def select_station_result(
        self,
        stations: List[Station],
        query: str,
        *,
        max_display: int = 20,
    ) -> Station | None:
        """Muestra resultados y devuelve la estación seleccionada."""
        shown = stations[:max_display]
        if not shown:
            return None

        self.console.print()
        self.console.print(self._build_station_table(shown, query, numbered=True))

        hidden = len(stations) - len(shown)
        if hidden > 0:
            self.console.print(
                f"[dim]... y {hidden} más. Refina tu búsqueda para ver menos resultados.[/dim]"
            )

        from rich.prompt import Prompt

        pick = Prompt.ask(
            f"\n{self._primary(f'💧 Seleccione número (1-{len(shown)})', bold=True)} "
            "o [dim]Enter para nueva búsqueda[/dim]",
            default="",
        ).strip()

        if not pick:
            return None

        try:
            idx = int(pick) - 1
        except ValueError:
            self.error("Por favor ingresa un número válido.")
            return None

        if not 0 <= idx < len(shown):
            self.error(f"Número fuera de rango. Elija entre 1 y {len(shown)}.")
            return None

        return shown[idx]

    def print_scraping_start(self, station_name: str, mode: str):
        """Muestra inicio del scraping"""
        self.console.print()
        panel = self._panel(
            f"{self._label('Estación')} {escape(str(station_name))}\n"
            f"{self._label('Modo')} {escape(str(mode.upper()))}",
            "Iniciando Scraping",
            icon="💧",
            panel_box=box.HEAVY,
        )
        self.console.print(panel)

    def print_available_years(self, years: List[int]):
        """Muestra años disponibles de forma visual"""
        years_text = Text()
        years_text.append("Años disponibles: ", style=f"bold {GARUA_PRIMARY}")
        years_text.append(" | ".join(str(y) for y in years), style=GARUA_PRIMARY)
        self.console.print(years_text)

    def print_options_count(self, count: int):
        """Muestra cantidad de opciones a procesar"""
        self.console.print(
            f"\n{self._primary(f'💧 Se procesarán {count} opciones', bold=True)}\n"
        )

    def success(self, message: str):
        """Mensaje de éxito"""
        self.console.print(self._status("✅", message, "green"))

    def error(self, message: str):
        """Mensaje de error"""
        self.console.print(self._status("❌", message, "red"))

    def warning(self, message: str):
        """Mensaje de advertencia"""
        self.console.print(self._status("⚠️ ", message, "yellow"))

    def info(self, message: str):
        """Mensaje informativo"""
        self.console.print(self._primary(f"💧 {message}"))

    def processing(self, message: str):
        """Mensaje de procesamiento"""
        self.console.print(self._primary(f"🔄 {message}"))

    def print_section_header(self, text: str, icon: str = ""):
        """Imprime un encabezado de sección"""
        header_text = f"{icon} {text}" if icon else text
        rule = "─" * self._section_width()
        self.console.print(f"\n{self._primary(rule, bold=True)}")
        self.console.print(f"[bold white]{header_text}[/bold white]")
        self.console.print(f"{self._primary(rule, bold=True)}\n")

    def print_completion_summary(
        self, successful: int, total: int, saved_files: List[str]
    ):
        """Muestra resumen final del proceso"""
        status_color = "green" if successful == total else "yellow"
        success_rate = (successful / total * 100) if total > 0 else 0

        summary = f"""
{self._label("Opciones procesadas")} [{status_color}]{successful}/{total}[/{status_color}]
{self._label("Tasa de éxito")} [{status_color}]{success_rate:.1f}%[/{status_color}]
{self._label("Archivos generados")} {len(saved_files)}
"""

        if saved_files:
            summary += f"\n{self._label('Archivos guardados')}\n"
            file_width = max(12, self._content_width() - 6)
            for file_path in saved_files[:5]:  # Mostrar primeros 5
                summary += f"  [dim]→[/dim] {self._primary(self._fit_text(file_path, file_width))}\n"
            if len(saved_files) > 5:
                summary += f"  [dim]... y {len(saved_files) - 5} más[/dim]\n"

        panel = self._panel(
            summary.strip(),
            "Proceso Completado",
            icon="💧",
            panel_box=box.HEAVY,
        )
        self.console.print()
        self.console.print(panel)

    def create_progress_bar(self):
        """Crea una barra de progreso elegante para procesar opciones"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )

    def print_processing_option(self, current: int, total: int, option_text: str):
        """Muestra el procesamiento de una opción específica"""
        rule = "─" * min(38, self._section_width())
        self.console.print(f"\n{self._primary(rule, bold=True)}")
        self.console.print(
            f"{self._primary(f'Procesando [{current}/{total}]', bold=True)} → [white]{escape(str(option_text))}[/white]"
        )

    def print_data_captured(self, option_value: str, bytes_count: int):
        """Muestra información de datos capturados"""
        compact = self.console.width < 50
        option = self._fit_text(option_value, max(8, self._content_width() - 24))
        verb = "Capturado" if compact else "Datos capturados para"
        size = self._format_bytes(bytes_count) if compact else f"{bytes_count:,} bytes"
        self.console.print(
            f"{self._status('✅', f'{verb} {option}', 'green')} [dim]({size})[/dim]"
        )

    def print_retry_attempt(self, attempt: int, option_value: str, error: str):
        """Muestra intento de reintento"""
        option = self._fit_text(option_value, max(8, self._content_width() - 28))
        self.console.print(
            self._status("⚠️ ", f"Intento {attempt} fallido para {option}", "yellow")
        )
        self.console.print(f"[dim]   Error: {escape(str(error))}[/dim]")
        self.console.print("[cyan]🔄 Reintentando...[/cyan]")

    def print_browser_status(self, action: str):
        """Muestra estado del navegador"""
        self.console.print(self._primary(f"💧 {action}..."))

    def print_goodbye(self):
        """Muestra mensaje de despedida cuando se interrumpe el programa"""
        self.console.print()
        goodbye_panel = self._panel(
            "[dim]Proceso interrumpido por el usuario[/dim]\n\n"
            f"{self._primary('¡Hasta pronto!', bold=True)}",
            "Garúa",
        )
        self.console.print(goodbye_panel)
        self.console.print()


# Instancia global
ui = UIConsole()
