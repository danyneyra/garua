"""Detección de navegadores Chromium compatibles con zendriver."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from zendriver import Config

from garua.exceptions import BrowserNotFoundError
from garua.settings import BROWSER_EXECUTABLE_PATH


ENV_BROWSER_PATH = "GARUA_BROWSER_PATH"


@dataclass(frozen=True)
class BrowserCheck:
    """Resultado de detección del navegador usado por Garua."""

    ok: bool
    path: str | None
    source: str | None
    message: str


def _is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def _normalize_path(raw_path: str) -> str:
    return str(Path(raw_path).expanduser())


def _path_from_env() -> BrowserCheck | None:
    if not BROWSER_EXECUTABLE_PATH:
        return None

    browser_path = Path(_normalize_path(BROWSER_EXECUTABLE_PATH))
    if _is_executable(browser_path):
        return BrowserCheck(
            ok=True,
            path=str(browser_path),
            source=ENV_BROWSER_PATH,
            message=f"Navegador configurado por {ENV_BROWSER_PATH}.",
        )

    return BrowserCheck(
        ok=False,
        path=str(browser_path),
        source=ENV_BROWSER_PATH,
        message=(
            f"{ENV_BROWSER_PATH} apunta a una ruta inválida o no ejecutable: "
            f"{browser_path}"
        ),
    )


def _path_from_zendriver() -> BrowserCheck | None:
    try:
        browser_path = Config().browser_executable_path
    except FileNotFoundError:
        return None

    if browser_path:
        return BrowserCheck(
            ok=True,
            path=str(browser_path),
            source="zendriver",
            message="Navegador detectado por zendriver.",
        )

    return None


def _edge_candidates() -> list[str]:
    candidates: list[str] = []
    path_match = shutil.which("msedge") or shutil.which("microsoft-edge")
    if path_match:
        candidates.append(path_match)

    if sys.platform == "win32":
        for base in (
            os.environ.get("PROGRAMFILES"),
            os.environ.get("PROGRAMFILES(X86)"),
            os.environ.get("LOCALAPPDATA"),
            os.environ.get("PROGRAMW6432"),
        ):
            if base:
                candidates.append(
                    os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")
                )

    elif sys.platform == "darwin":
        candidates.append(
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        )

    else:
        for name in ("microsoft-edge", "microsoft-edge-stable"):
            path_match = shutil.which(name)
            if path_match:
                candidates.append(path_match)

    return candidates


def _path_from_edge() -> BrowserCheck | None:
    for candidate in _edge_candidates():
        browser_path = Path(candidate)
        if _is_executable(browser_path):
            return BrowserCheck(
                ok=True,
                path=str(browser_path),
                source="edge",
                message="Microsoft Edge detectado como navegador Chromium compatible.",
            )

    return None


def check_browser() -> BrowserCheck:
    """Detecta un navegador compatible sin iniciar una sesión de scraping."""
    env_check = _path_from_env()
    if env_check:
        return env_check

    zendriver_check = _path_from_zendriver()
    if zendriver_check:
        return zendriver_check

    edge_check = _path_from_edge()
    if edge_check:
        return edge_check

    return BrowserCheck(
        ok=False,
        path=None,
        source=None,
        message=(
            "No se encontró Google Chrome, Brave ni Microsoft Edge. "
            "Instala Google Chrome o Brave, o define "
            f"{ENV_BROWSER_PATH} con la ruta completa del ejecutable."
        ),
    )


def get_browser_config() -> Config:
    """Devuelve una configuración zendriver lista para arrancar el navegador."""
    browser_check = check_browser()
    if not browser_check.ok or not browser_check.path:
        raise BrowserNotFoundError(browser_check.message)

    return Config(browser_executable_path=browser_check.path)


def get_runtime_summary() -> dict[str, str | bool | None]:
    """Resumen compacto para comandos de diagnóstico."""
    browser_check = check_browser()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "browser_ok": browser_check.ok,
        "browser_path": browser_check.path,
        "browser_source": browser_check.source,
        "browser_message": browser_check.message,
    }
