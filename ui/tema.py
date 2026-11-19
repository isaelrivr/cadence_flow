"""Sistema de diseño y tokens visuales oficiales de Cadence Flow.

Este módulo es la ÚNICA fuente de verdad para colores, tipografía, espaciados,
radios, dimensiones y tiempos de animación. Ningún otro módulo debe declarar
colores hexadecimales ni tamaños tipográficos literales.
"""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import customtkinter as ctk

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FUENTES_DIR = ASSETS_DIR / "fonts"
LOGO_OFICIAL_PATH = ASSETS_DIR / "logo_cadence_transparente.png"
ICONO_ICO_PATH = ASSETS_DIR / "cadence_icon.ico"
ICONO_PNG_PATH = ASSETS_DIR / "cadence_icon.png"

# Identidad de marca (Cadence Technologies, S.A. de C.V.)
NOMBRE_PRODUCTO = "Cadence Flow"
NOMBRE_EMPRESA = "Cadence Technologies, S.A. de C.V."
ESLOGAN = "Datos en sincronía, decisiones con sentido."

# Cursores multiplataforma compatibles con Windows, macOS y Linux
CURSOR_MANO = "hand2"
CURSOR_NORMAL = ""

# ---------------------------------------------------------------------------
# Paleta oficial y tokens cromáticos (Claro, Oscuro) verificados WCAG AA
# ---------------------------------------------------------------------------
MARCA_AZUL_PROFUNDO = "#00304E"
MARCA_AZUL_PETROLEO = "#006080"
MARCA_CIAN = "#00F0F0"
MARCA_BLANCO = "#FFFFFF"
MARCA_GRIS_AZULADO = "#5B6770"

# Valores RGB para composición con Pillow
RGB_AZUL_PROFUNDO: Tuple[int, int, int] = (0, 48, 78)
RGB_AZUL_PETROLEO: Tuple[int, int, int] = (0, 96, 128)
RGB_CIAN: Tuple[int, int, int] = (0, 240, 240)
RGB_BLANCO: Tuple[int, int, int] = (255, 255, 255)
RGB_PIZARRA_TRACK: Tuple[int, int, int] = (214, 225, 232)
RGB_PIZARRA_TRACK_OSCURO: Tuple[int, int, int] = (30, 67, 94)

# Pares adaptativos (claro, oscuro) para CustomTkinter
FONDO_APP = ("#F4F7FA", "#081B29")
FONDO_SIDEBAR = ("#FFFFFF", "#0B2233")
FONDO_HEADER = ("#00304E", "#002238")
FONDO_SPLASH = ("#FFFFFF", "#FFFFFF")  # El logo original a color exige superficie clara

SUPERFICIE = ("#FFFFFF", "#0D2538")
SUPERFICIE_SUTIL = ("#EBF1F5", "#133148")
SUPERFICIE_HOVER = ("#E1EBF2", "#183B56")
BORDE = ("#D6E1E8", "#1E435E")
BORDE_ACTIVO = ("#006080", "#00F0F0")
DIVISOR = ("#E1E9EE", "#183850")
CIRCUITO_LINEA = ("#B8CDD9", "#1E4A66")
CIRCUITO_NODO = ("#006080", "#00F0F0")

TEXTO_PRIMARIO = ("#00304E", "#E8F2F7")
TEXTO_SECUNDARIO = ("#5B6770", "#9BB1C0")
TEXTO_TERCIARIO = ("#465560", "#B7CAD7")
TEXTO_SOBRE_OSCURO = ("#FFFFFF", "#FFFFFF")
TEXTO_CIAN_SOBRE_OSCURO = ("#00F0F0", "#00F0F0")
TEXTO_SOBRE_CIAN = ("#00304E", "#00304E")

# Botones y controles
BTN_PRIMARIO_BG = ("#006080", "#007A9E")
BTN_PRIMARIO_HOVER = ("#004A66", "#0091BA")
BTN_PRIMARIO_TEXTO = ("#FFFFFF", "#FFFFFF")

BTN_OSCURO_BG = ("#00304E", "#0F4568")
BTN_OSCURO_HOVER = ("#004870", "#175C87")
BTN_OSCURO_TEXTO = ("#FFFFFF", "#FFFFFF")

BTN_SECUNDARIO_BG = ("#EBF1F5", "#133148")
BTN_SECUNDARIO_HOVER = ("#D9E6EE", "#1B4260")
BTN_SECUNDARIO_TEXTO = ("#00304E", "#E8F2F7")

BTN_CIAN_BG = ("#00F0F0", "#00F0F0")
BTN_CIAN_HOVER = ("#45F6F6", "#45F6F6")
BTN_CIAN_TEXTO = ("#00304E", "#00304E")

BTN_PELIGRO_BG = ("#B41E3A", "#C82847")
BTN_PELIGRO_HOVER = ("#8E152C", "#DF3B5A")
BTN_PELIGRO_TEXTO = ("#FFFFFF", "#FFFFFF")

BTN_EXITO_BG = ("#0F6B5D", "#128574")
BTN_EXITO_HOVER = ("#0B5348", "#17A08C")
BTN_EXITO_TEXTO = ("#FFFFFF", "#FFFFFF")

BTN_DESHABILITADO_BG = ("#E2E8EE", "#152C3E")
BTN_DESHABILITADO_TEXTO = ("#7A8994", "#5F7788")

FOCO_BORDE = ("#006080", "#00F0F0")
HOVER_HEADER = ("#0A456A", "#0A3A58")
NAV_ACTIVO_BG = ("#E5F5FA", "#12374D")
NAV_HOVER_BG = ("#EFF5F9", "#0F2C40")
NAV_INDICADOR = ("#006080", "#00F0F0")

INPUT_BG = ("#FFFFFF", "#0A2030")
INPUT_BORDE = ("#C2D1DC", "#265170")
SCROLLBAR_TRACK = ("#EAF0F4", "#0B2030")
SCROLLBAR_THUMB = ("#B8C8D4", "#244D69")
SCROLLBAR_THUMB_HOVER = ("#006080", "#0099B8")

# Colores semánticos (texto, fondo, borde) con contraste WCAG AA verificado
SEMANTICO: Dict[str, Dict[str, Tuple[str, str]]] = {
    "exito": {
        "fg": ("#0F6B5D", "#5CE1CB"),
        "bg": ("#E5F6F3", "#0E3330"),
        "borde": ("#9BD9CE", "#1E5E55"),
    },
    "alerta": {
        "fg": ("#9A4A06", "#FBBF4D"),
        "bg": ("#FEF3E2", "#38260E"),
        "borde": ("#F2C98A", "#6D4A1B"),
    },
    "error": {
        "fg": ("#B41E3A", "#FB7185"),
        "bg": ("#FDECEF", "#3B1420"),
        "borde": ("#F1AEBB", "#74263B"),
    },
    "info": {
        "fg": ("#006080", "#5CE6F5"),
        "bg": ("#E5F5FA", "#0E2F42"),
        "borde": ("#9ED7E8", "#1F5A78"),
    },
    "neutro": {
        "fg": ("#5B6770", "#9BB1C0"),
        "bg": ("#EBF1F5", "#133148"),
        "borde": ("#CEDBE3", "#264B66"),
    },
    "cian_oscuro": {
        "fg": ("#00F0F0", "#00F0F0"),
        "bg": ("#0A3C5C", "#0A3C5C"),
        "borde": ("#008AA6", "#008AA6"),
    },
}

# ---------------------------------------------------------------------------
# Escala de espaciado, radios y dimensiones
# ---------------------------------------------------------------------------
ESPACIO_XS = 4
ESPACIO_SM = 8
ESPACIO_MD = 12
ESPACIO_LG = 16
ESPACIO_XL = 20
ESPACIO_XXL = 24
ESPACIO_XXXL = 32

RADIO_CHIP = 6
RADIO_BOTON = 8
RADIO_TARJETA = 12
RADIO_MODAL = 14
RADIO_PILL = 999

BORDE_NORMAL = 1
BORDE_FOCO = 2

ANCHO_MIN_VENTANA = 1040
ALTO_MIN_VENTANA = 680
ANCHO_DEFECTO_VENTANA = 1280
ALTO_DEFECTO_VENTANA = 800
ANCHO_SIDEBAR = 248
ALTO_HEADER = 76

ANCHO_LOGO_HEADER = 80
ALTO_LOGO_HEADER = 46
ANCHO_LOGO_SPLASH = 310
ALTO_LOGO_SPLASH = 179
MARGEN_LIBRE_RATIO_C = 85.0 / 373.0  # Altura exacta de la letra 'C' en el logo

ICONO_SM = 16
ICONO_MD = 18
ICONO_LG = 22
ICONO_XL = 42

ALTO_BOTON_SM = 30
ALTO_BOTON_MD = 36
ALTO_BOTON_LG = 40
ALTO_BARRA_PROGRESO = 10

# Motion y animaciones
FPS_LOGO = 30
INTERVALO_LOGO_MS = 33
FRAMES_LOGO = 36
DURACION_SPLASH_MS = 2000
DURACION_SPLASH_REDUCIDO_MS = 650
DURACION_TRANSICION_MS = 180
DURACION_TOAST_MS = 3600
DELAY_TOOLTIP_MS = 350

# ---------------------------------------------------------------------------
# Tipografía y carga de fuentes locales
# ---------------------------------------------------------------------------
_FAMILIA_PRINCIPAL = "Inter"
_FAMILIA_MONO = "Consolas"
_FUENTES_CARGADAS = False
_CACHE_FUENTES: Dict[str, ctk.CTkFont] = {}
_SUSCRIPTORES_TEMA: List[Callable[[str], None]] = []


def _familia_sistema_respaldo() -> Tuple[str, str]:
    """Devuelve familia sans-serif y monoespaciada según el sistema operativo."""
    so = platform.system()
    if so == "Windows":
        return "Segoe UI", "Consolas"
    if so == "Darwin":
        return "Helvetica Neue", "Menlo"
    return "Arial", "DejaVu Sans Mono"


def cargar_fuentes_locales() -> str:
    """Registra archivos Inter TTF en CustomTkinter antes de usar la interfaz."""
    global _FAMILIA_PRINCIPAL, _FAMILIA_MONO, _FUENTES_CARGADAS
    sans_fallback, mono_fallback = _familia_sistema_respaldo()
    _FAMILIA_MONO = mono_fallback

    if _FUENTES_CARGADAS:
        return _FAMILIA_PRINCIPAL

    cargada_inter = False
    if FUENTES_DIR.exists():
        for archivo_ttf in sorted(FUENTES_DIR.glob("*.ttf")):
            try:
                if ctk.FontManager.load_font(str(archivo_ttf.resolve())):
                    if "inter" in archivo_ttf.stem.lower():
                        cargada_inter = True
            except Exception:
                continue

    _FAMILIA_PRINCIPAL = "Inter" if cargada_inter else sans_fallback
    _FUENTES_CARGADAS = True
    return _FAMILIA_PRINCIPAL


def familia_principal() -> str:
    """Devuelve la familia tipográfica principal activa."""
    if not _FUENTES_CARGADAS:
        cargar_fuentes_locales()
    return _FAMILIA_PRINCIPAL


def familia_mono() -> str:
    """Devuelve la familia monoespaciada activa."""
    if not _FUENTES_CARGADAS:
        cargar_fuentes_locales()
    return _FAMILIA_MONO


_DEFINICION_ROLES: Dict[str, Tuple[str, int, str]] = {
    "titulo_splash": ("sans", 16, "bold"),
    "titulo_pagina": ("sans", 20, "bold"),
    "subtitulo": ("sans", 14, "bold"),
    "titulo_tarjeta": ("sans", 13, "bold"),
    "kpi_valor": ("sans", 18, "bold"),
    "kpi_titulo": ("sans", 11, "bold"),
    "cuerpo_bold": ("sans", 12, "bold"),
    "cuerpo": ("sans", 12, "normal"),
    "etiqueta": ("sans", 11, "normal"),
    "boton": ("sans", 12, "bold"),
    "boton_sm": ("sans", 11, "bold"),
    "badge": ("sans", 11, "bold"),
    "eslogan": ("sans", 12, "normal"),
    "mono": ("mono", 11, "normal"),
    "mono_bold": ("mono", 11, "bold"),
}


def fuente(rol: str) -> ctk.CTkFont:
    """Devuelve un CTkFont cacheado para el rol semántico solicitado."""
    if rol in _CACHE_FUENTES:
        return _CACHE_FUENTES[rol]
    tipo, tam, peso = _DEFINICION_ROLES.get(rol, ("sans", 12, "normal"))
    fam = familia_mono() if tipo == "mono" else familia_principal()
    obj = ctk.CTkFont(family=fam, size=tam, weight=peso)
    _CACHE_FUENTES[rol] = obj
    return obj


def obtener_modo_actual() -> str:
    """Retorna 'Light' o 'Dark' según la configuración activa de CustomTkinter."""
    modo = ctk.get_appearance_mode()
    return "Dark" if str(modo).lower() == "dark" else "Light"


def resolver_color(token: str | Tuple[str, str], modo: Optional[str] = None) -> str:
    """Convierte un token (claro, oscuro) en el hex string correspondiente al modo."""
    if isinstance(token, str):
        return token
    modo_uso = modo or obtener_modo_actual()
    return token[1] if modo_uso == "Dark" else token[0]


def suscribir_cambio_tema(callback: Callable[[str], None]) -> None:
    """Registra un callback para widgets Canvas/Pillow cuando cambia el tema."""
    if callback not in _SUSCRIPTORES_TEMA:
        _SUSCRIPTORES_TEMA.append(callback)


def desuscribir_cambio_tema(callback: Callable[[str], None]) -> None:
    """Elimina un callback registrado de cambio de tema."""
    if callback in _SUSCRIPTORES_TEMA:
        _SUSCRIPTORES_TEMA.remove(callback)


def cambiar_modo_apariencia(modo: str) -> None:
    """Cambia entre 'Light' y 'Dark' y notifica a los suscriptores."""
    objetivo = "Dark" if modo.lower() == "dark" else "Light"
    ctk.set_appearance_mode(objetivo)
    for cb in list(_SUSCRIPTORES_TEMA):
        try:
            cb(objetivo)
        except Exception:
            continue


def margen_libre_logo(altura_px: int) -> int:
    """Calcula el área libre mínima equivalente a la altura de la letra 'C'."""
    return max(ESPACIO_SM, int(round(altura_px * MARGEN_LIBRE_RATIO_C)))
