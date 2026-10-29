"""Report unsupported MCP dependencies before importing the protocol engine."""

from importlib.metadata import PackageNotFoundError, version

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion

MCP_REQUIREMENTS = {
    "fastmcp": ">=4.1.4,<4.2",
    "mcp": ">=2.3.0,<2.4",
    "mcp-types": ">=2.3.0,<2.4",
}


def ensure_mcp_compatibility() -> None:
    problems = []
    for package, requirement in MCP_REQUIREMENTS.items():
        try:
            installed = version(package)
        except PackageNotFoundError:
            problems.append(f"{package}: no instalado (requiere {requirement})")
            continue
        try:
            compatible = SpecifierSet(requirement).contains(
                installed, prereleases=False
            )
        except InvalidVersion:
            compatible = False
        if not compatible:
            problems.append(f"{package}=={installed} (requiere {requirement})")
    if problems:
        constraints = " ".join(
            f'"{name}{spec}"' for name, spec in MCP_REQUIREMENTS.items()
        )
        raise RuntimeError(
            "Dependencias MCP fuera del rango probado por Garúa: "
            + "; ".join(problems)
            + ". Usa un entorno aislado para Garúa. Para restaurar sus dependencias: "
            + f"python -m pip install {constraints}"
        )
