"""Permite ejecutar el pipeline con ``python -m etl``."""

from __future__ import annotations

from etl.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
