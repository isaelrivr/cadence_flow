"""Generador y caché de íconos vectoriales geométricos renderizados con Pillow.

Sigue el concepto visual de Cadence Flow (música + circuito): trazos limpios,
nodos circulares y geometría hexagonal con antialiasing 2x. No usa emojis ni
colores literales; todo proviene de ui.tema.
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

import customtkinter as ctk
from PIL import Image, ImageDraw

from ui import tema

_CACHE_ICONOS: Dict[Tuple[str, int, str, str], ctk.CTkImage] = {}


def _hex_a_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convierte un color hexadecimal #RRGGBB a tupla RGBA."""
    limpio = hex_color.lstrip("#")
    return (
        int(limpio[0:2], 16),
        int(limpio[2:4], 16),
        int(limpio[4:6], 16),
        alpha,
    )


def _puntos_hexagono(cx: float, cy: float, r: float) -> list[Tuple[float, float]]:
    """Calcula los 6 vértices de un hexágono regular centrado en (cx, cy)."""
    return [
        (
            cx + r * math.cos(math.radians(60 * i - 30)),
            cy + r * math.sin(math.radians(60 * i - 30)),
        )
        for i in range(6)
    ]


def _dibujar_icono_pil(nombre: str, tam: int, hex_color: str) -> Image.Image:
    """Dibuja un ícono en resolución 2x y lo reduce con LANCZOS para máxima nitidez."""
    escala = 2
    s = tam * escala
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = _hex_a_rgba(hex_color)
    col_suave = _hex_a_rgba(hex_color, 55)
    g = max(2, round(s * 0.095))  # Grosor uniforme de trazo
    u = s / 24.0  # Cuadrícula lógica 24x24

    def p(x: float, y: float) -> Tuple[float, float]:
        return (x * u, y * u)

    if nombre == "dashboard":
        cajas = [(3, 3, 10.5, 10.5), (13.5, 3, 21, 10.5), (3, 13.5, 10.5, 21), (13.5, 13.5, 21, 21)]
        for idx, (x1, y1, x2, y2) in enumerate(cajas):
            fill = col_suave if idx == 0 else None
            d.rounded_rectangle([x1 * u, y1 * u, x2 * u, y2 * u], radius=2.2 * u, outline=col, fill=fill, width=g)

    elif nombre == "indicadores":
        d.ellipse([3 * u, 3 * u, 21 * u, 21 * u], outline=col, width=g)
        d.ellipse([7.5 * u, 7.5 * u, 16.5 * u, 16.5 * u], outline=col, width=g)
        d.ellipse([10.5 * u, 10.5 * u, 13.5 * u, 13.5 * u], fill=col)

    elif nombre == "historico":
        d.polygon(
            [p(3, 6), p(9.5, 6), p(11.5, 8.5), p(21, 8.5), p(21, 19), p(3, 19)],
            outline=col,
            fill=col_suave,
        )
        d.line([p(3, 6), p(9.5, 6), p(11.5, 8.5), p(21, 8.5), p(21, 19), p(3, 19), p(3, 6)], fill=col, width=g)
        d.line([p(7, 13.5), p(17, 13.5)], fill=col, width=g)

    elif nombre == "bitacora":
        d.rounded_rectangle([4 * u, 3 * u, 20 * u, 21 * u], radius=2.2 * u, outline=col, width=g)
        for y in (8.5, 12.5, 16.5):
            d.ellipse([7 * u, (y - 1) * u, 9 * u, (y + 1) * u], fill=col)
            d.line([p(11, y), p(17, y)], fill=col, width=g)

    elif nombre == "agentes":
        pts = _puntos_hexagono(12 * u, 12 * u, 5.2 * u)
        d.polygon(pts, outline=col, fill=col_suave)
        d.line(pts + [pts[0]], fill=col, width=g)
        d.ellipse([10.3 * u, 10.3 * u, 13.7 * u, 13.7 * u], fill=col)
        nodos = [(4, 6), (20, 6), (4, 18), (20, 18)]
        for nx, ny in nodos:
            d.line([p(12, 12), p(nx, ny)], fill=col, width=max(2, g - 1))
            d.ellipse([(nx - 1.7) * u, (ny - 1.7) * u, (nx + 1.7) * u, (ny + 1.7) * u], fill=col)

    elif nombre == "usuarios":
        d.ellipse([8 * u, 4 * u, 16 * u, 12 * u], outline=col, fill=col_suave, width=g)
        d.arc([4 * u, 13.5 * u, 20 * u, 24.5 * u], start=190, end=350, fill=col, width=g)
        d.line([p(4.2, 20), p(19.8, 20)], fill=col, width=g)

    elif nombre == "upload":
        d.line([p(12, 16), p(12, 4)], fill=col, width=g)
        d.line([p(7.5, 8.5), p(12, 4), p(16.5, 8.5)], fill=col, width=g)
        d.line([p(4, 16.5), p(4, 20), p(20, 20), p(20, 16.5)], fill=col, width=g)

    elif nombre == "check":
        d.line([p(4.5, 12.5), p(9.5, 17.5), p(19.5, 6.5)], fill=col, width=g + 1)

    elif nombre == "alert":
        d.polygon([p(12, 3.5), p(21, 19.5), p(3, 19.5)], outline=col, fill=col_suave)
        d.line([p(12, 3.5), p(21, 19.5), p(3, 19.5), p(12, 3.5)], fill=col, width=g)
        d.line([p(12, 9.5), p(12, 14)], fill=col, width=g)
        d.ellipse([11 * u, 16 * u, 13 * u, 18 * u], fill=col)

    elif nombre == "error":
        d.ellipse([3.5 * u, 3.5 * u, 20.5 * u, 20.5 * u], outline=col, fill=col_suave, width=g)
        d.line([p(8.5, 8.5), p(15.5, 15.5)], fill=col, width=g)
        d.line([p(15.5, 8.5), p(8.5, 15.5)], fill=col, width=g)

    elif nombre == "clock":
        d.ellipse([3.5 * u, 3.5 * u, 20.5 * u, 20.5 * u], outline=col, width=g)
        d.line([p(12, 7.5), p(12, 12.5), p(15.5, 14.5)], fill=col, width=g)

    elif nombre == "play":
        d.polygon([p(7, 5), p(19, 12), p(7, 19)], fill=col)

    elif nombre == "pause":
        d.rounded_rectangle([6.5 * u, 5 * u, 10 * u, 19 * u], radius=1.2 * u, fill=col)
        d.rounded_rectangle([14 * u, 5 * u, 17.5 * u, 19 * u], radius=1.2 * u, fill=col)

    elif nombre == "refresh":
        d.arc([4 * u, 4 * u, 20 * u, 20 * u], start=40, end=315, fill=col, width=g)
        d.polygon([p(17, 4), p(20.5, 8), p(15.5, 9)], fill=col)

    elif nombre == "search":
        d.ellipse([4 * u, 4 * u, 16 * u, 16 * u], outline=col, width=g)
        d.line([p(14.5, 14.5), p(20, 20)], fill=col, width=g + 1)

    elif nombre == "sun":
        d.ellipse([7.5 * u, 7.5 * u, 16.5 * u, 16.5 * u], outline=col, fill=col_suave, width=g)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x1, y1 = 12 + 6.5 * math.cos(rad), 12 + 6.5 * math.sin(rad)
            x2, y2 = 12 + 9.2 * math.cos(rad), 12 + 9.2 * math.sin(rad)
            d.line([p(x1, y1), p(x2, y2)], fill=col, width=g)

    elif nombre == "moon":
        d.arc([4.5 * u, 4.5 * u, 19.5 * u, 19.5 * u], start=45, end=275, fill=col, width=g)
        d.arc([8.5 * u, 4 * u, 19.5 * u, 15.5 * u], start=80, end=250, fill=col, width=g)

    elif nombre == "bolt":
        d.polygon([p(13, 3), p(5.5, 13.5), p(11.5, 13.5), p(10.5, 21), p(18.5, 10.5), p(12.5, 10.5)], fill=col)

    elif nombre == "shield":
        pts = [p(12, 3), p(19.5, 6), p(19.5, 12.5), p(12, 21), p(4.5, 12.5), p(4.5, 6)]
        d.polygon(pts, outline=col, fill=col_suave)
        d.line(pts + [pts[0]], fill=col, width=g)
        d.line([p(9, 12), p(11.2, 14.3), p(15.5, 9.5)], fill=col, width=g)

    elif nombre in ("calendar_start", "calendar_end"):
        d.rounded_rectangle([4 * u, 5.5 * u, 20 * u, 20 * u], radius=2 * u, outline=col, width=g)
        d.line([p(4, 10), p(20, 10)], fill=col, width=g)
        d.line([p(8.5, 3.5), p(8.5, 7)], fill=col, width=g)
        d.line([p(15.5, 3.5), p(15.5, 7)], fill=col, width=g)
        if nombre == "calendar_start":
            d.polygon([p(10, 12.5), p(15.5, 15.3), p(10, 18)], fill=col)
        else:
            d.line([p(8.5, 15), p(11, 17.5), p(15.5, 12.8)], fill=col, width=g)

    elif nombre == "motion":
        d.arc([3 * u, 6 * u, 21 * u, 22 * u], start=200, end=340, fill=col, width=g)
        d.arc([6.5 * u, 10 * u, 17.5 * u, 20 * u], start=200, end=340, fill=col, width=g)
        d.ellipse([10.5 * u, 14.5 * u, 13.5 * u, 17.5 * u], fill=col)

    elif nombre == "file":
        pts = [p(5.5, 3), p(14.5, 3), p(18.5, 7), p(18.5, 21), p(5.5, 21)]
        d.polygon(pts, outline=col, fill=col_suave)
        d.line(pts + [pts[0]], fill=col, width=g)
        d.line([p(14.5, 3), p(14.5, 7), p(18.5, 7)], fill=col, width=g)
        d.line([p(8.5, 12), p(15.5, 12)], fill=col, width=g)
        d.line([p(8.5, 16), p(13.5, 16)], fill=col, width=g)

    elif nombre == "hex_node":
        pts = _puntos_hexagono(12 * u, 12 * u, 7.5 * u)
        d.polygon(pts, outline=col, fill=col_suave)
        d.line(pts + [pts[0]], fill=col, width=g)
        d.ellipse([9.5 * u, 9.5 * u, 14.5 * u, 14.5 * u], fill=col)

    else:  # info / respaldo
        d.ellipse([3.5 * u, 3.5 * u, 20.5 * u, 20.5 * u], outline=col, fill=col_suave, width=g)
        d.ellipse([11 * u, 7 * u, 13 * u, 9 * u], fill=col)
        d.line([p(12, 11.2), p(12, 17)], fill=col, width=g)

    return img.resize((tam, tam), Image.Resampling.LANCZOS)


def obtener_icono(
    nombre: str,
    tam: int = tema.ICONO_MD,
    color_token: str | Tuple[str, str] = tema.TEXTO_PRIMARIO,
) -> ctk.CTkImage:
    """Devuelve un CTkImage dual claro/oscuro cacheado para el ícono solicitado."""
    color_claro = tema.resolver_color(color_token, "Light")
    color_oscuro = tema.resolver_color(color_token, "Dark")
    clave = (nombre, tam, color_claro, color_oscuro)
    if clave not in _CACHE_ICONOS:
        img_clara = _dibujar_icono_pil(nombre, tam, color_claro)
        img_oscura = _dibujar_icono_pil(nombre, tam, color_oscuro)
        _CACHE_ICONOS[clave] = ctk.CTkImage(
            light_image=img_clara,
            dark_image=img_oscura,
            size=(tam, tam),
        )
    return _CACHE_ICONOS[clave]
