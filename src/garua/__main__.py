"""Ejecutar la CLI de Garua con ``python -m garua``."""

import sys

from garua.main import cli


if __name__ == "__main__":
    sys.exit(cli())
