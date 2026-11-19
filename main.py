"""Punto de entrada principal de Cadence Flow."""

from __future__ import annotations

import ctypes
import platform
import sys

import customtkinter as ctk

from ui import tema
from ui.app import CadenceFlowApp


def _habilitar_dpi_awareness() -> None:
    """Activa escalado nítido HiDPI en Windows sin afectar macOS/Linux."""
    if platform.system() != "Windows":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main() -> int:
    _habilitar_dpi_awareness()
    ctk.set_default_color_theme("blue")
    tema.cargar_fuentes_locales()
    app = CadenceFlowApp(con_splash=True)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
