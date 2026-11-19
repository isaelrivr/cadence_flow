"""Motor de animaciones cacheadas para el logotipo oficial y micro-transiciones.

Precalcula los fotogramas del logotipo con Pillow una sola vez por tamaño y
variante para evitar trabajo costoso dentro de after(). Respeta la pausa por
ventana minimizada y la preferencia de accesibilidad 'Reducir movimiento'.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageEnhance

from ui import tema

_CACHE_BASE_LOGO: Optional[Image.Image] = None
_CACHE_FRAMES_LOGO: Dict[Tuple[int, int, str], Tuple[ctk.CTkImage, ...]] = {}


def _cargar_logo_base() -> Image.Image:
    """Carga el logo oficial respetando su canal alfa y proporciones originales."""
    global _CACHE_BASE_LOGO
    if _CACHE_BASE_LOGO is not None:
        return _CACHE_BASE_LOGO

    if tema.LOGO_OFICIAL_PATH.exists():
        _CACHE_BASE_LOGO = Image.open(tema.LOGO_OFICIAL_PATH).convert("RGBA")
        return _CACHE_BASE_LOGO

    # Respaldo provisional solo si faltara el archivo oficial
    provisional = Image.new("RGBA", (646, 373), (0, 0, 0, 0))
    d = ImageDraw.Draw(provisional)
    d.ellipse([40, 40, 180, 180], outline=tema.RGB_AZUL_PETROLEO + (255,), width=14)
    d.line([180, 110, 580, 110], fill=tema.RGB_CIAN + (255,), width=12)
    _CACHE_BASE_LOGO = provisional
    return _CACHE_BASE_LOGO


def _crear_variante_base(ancho: int, alto: int, variante: str) -> Image.Image:
    """Escala el logo preservando relación de aspecto y genera variante blanca si aplica."""
    orig = _cargar_logo_base()
    ratio = min(ancho / orig.width, alto / orig.height)
    nuevo_w = max(1, int(round(orig.width * ratio)))
    nuevo_h = max(1, int(round(orig.height * ratio)))
    escalado = orig.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)

    lienzo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    ox = (ancho - nuevo_w) // 2
    oy = (alto - nuevo_h) // 2
    lienzo.paste(escalado, (ox, oy), escalado)

    if variante == "blanco":
        alfa = lienzo.getchannel("A")
        blanca = Image.new("RGBA", (ancho, alto), tema.RGB_BLANCO + (255,))
        blanca.putalpha(alfa)
        return blanca
    return lienzo


def _generar_frames_logo(ancho: int, alto: int, variante: str) -> Tuple[ctk.CTkImage, ...]:
    """Precalcula los 36 fotogramas con destello cian recortado al alfa y pulso suave."""
    clave = (ancho, alto, variante)
    if clave in _CACHE_FRAMES_LOGO:
        return _CACHE_FRAMES_LOGO[clave]

    base = _crear_variante_base(ancho, alto, variante)
    alfa_base = base.getchannel("A")
    total = tema.FRAMES_LOGO
    frames_ctk: List[ctk.CTkImage] = []

    ancho_banda = max(16, int(ancho * 0.22))
    inclinacion = int(alto * 0.35)

    for idx in range(total):
        t = idx / float(total)
        # Fotograma 0 permanece completamente en reposo (sin destello)
        if idx == 0:
            frame_pil = base
        else:
            # Pulso suave sinusoidal de brillo
            factor_brillo = 1.0 + 0.07 * math.sin(2.0 * math.pi * t)
            pulsada = ImageEnhance.Brightness(base).enhance(factor_brillo)
            pulsada.putalpha(alfa_base)

            # Destello cian diagonal que recorre de izquierda a derecha
            x_centro = -ancho_banda + t * (ancho + inclinacion + ancho_banda * 2)
            capa_destello = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
            dib = ImageDraw.Draw(capa_destello)

            # Capa exterior difusa y núcleo brillante
            opacidad_ext = 70 if variante == "color" else 95
            opacidad_int = 135 if variante == "color" else 170

            poly_ext = [
                (x_centro - ancho_banda, 0),
                (x_centro + ancho_banda, 0),
                (x_centro + ancho_banda - inclinacion, alto),
                (x_centro - ancho_banda - inclinacion, alto),
            ]
            poly_int = [
                (x_centro - ancho_banda * 0.36, 0),
                (x_centro + ancho_banda * 0.36, 0),
                (x_centro + ancho_banda * 0.36 - inclinacion, alto),
                (x_centro - ancho_banda * 0.36 - inclinacion, alto),
            ]
            dib.polygon(poly_ext, fill=tema.RGB_CIAN + (opacidad_ext,))
            dib.polygon(poly_int, fill=tema.RGB_CIAN + (opacidad_int,))

            # Recortar estrictamente al canal alfa original del logotipo
            alfa_destello = ImageChops.multiply(capa_destello.getchannel("A"), alfa_base)
            capa_destello.putalpha(alfa_destello)

            frame_pil = Image.alpha_composite(pulsada, capa_destello)

        frames_ctk.append(
            ctk.CTkImage(
                light_image=frame_pil,
                dark_image=frame_pil,
                size=(ancho, alto),
            )
        )

    resultado = tuple(frames_ctk)
    _CACHE_FRAMES_LOGO[clave] = resultado
    return resultado


def obtener_frames_logo(ancho: int, alto: int, variante: str = "color") -> Tuple[ctk.CTkImage, ...]:
    """Obtiene los fotogramas cacheados del logotipo ('color' o 'blanco')."""
    return _generar_frames_logo(ancho, alto, variante)


def _interpolar_rgb(
    c1: Tuple[int, int, int],
    c2: Tuple[int, int, int],
    t: float,
) -> Tuple[int, int, int]:
    """Interpola linealmente entre dos colores RGB."""
    return (
        int(round(c1[0] + (c2[0] - c1[0]) * t)),
        int(round(c1[1] + (c2[1] - c1[1]) * t)),
        int(round(c1[2] + (c2[2] - c1[2]) * t)),
    )


def crear_imagen_barra_degradada(
    ancho: int,
    alto: int,
    progreso: float,
    modo: str = "Light",
) -> Image.Image:
    """Renderiza una barra de progreso redondeada con el degradado oficial."""
    w = max(12, int(ancho))
    h = max(6, int(alto))
    prog = max(0.0, min(1.0, float(progreso)))

    escala = 2
    sw, sh = w * escala, h * escala
    radio = sh // 2

    track_rgb = (
        tema.RGB_PIZARRA_TRACK_OSCURO if modo == "Dark" else tema.RGB_PIZARRA_TRACK
    )
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=radio, fill=track_rgb + (255,))

    fill_w = int(round(sw * prog))
    if fill_w > 0:
        fill_w = max(fill_w, min(sw, sh))
        tira = Image.new("RGBA", (sw, 1), (0, 0, 0, 0))
        pix = tira.load()
        denom = max(1, sw - 1)
        for x in range(fill_w):
            t = x / denom
            if t < 0.55:
                col = _interpolar_rgb(tema.RGB_CIAN, tema.RGB_AZUL_PETROLEO, t / 0.55)
            else:
                col = _interpolar_rgb(
                    tema.RGB_AZUL_PETROLEO, tema.RGB_AZUL_PROFUNDO, (t - 0.55) / 0.45
                )
            pix[x, 0] = col + (255,)

        grad = tira.resize((sw, sh), Image.Resampling.NEAREST)
        mascara = Image.new("L", (sw, sh), 0)
        dm = ImageDraw.Draw(mascara)
        dm.rounded_rectangle([0, 0, fill_w - 1, sh - 1], radius=radio, fill=255)
        grad.putalpha(mascara)
        img = Image.alpha_composite(img, grad)

    return img.resize((w, h), Image.Resampling.LANCZOS)


class GestorAnimacionesGlobal:
    """Coordina pausa al minimizar y el modo de accesibilidad 'Reducir movimiento'."""

    def __init__(self) -> None:
        self.reducir_movimiento: bool = False
        self.ventana_minimizada: bool = False
        self._controladores: List["ControladorLogoAnimado"] = []
        self._callbacks_transicion: List[str] = []

    def registrar(self, controlador: "ControladorLogoAnimado") -> None:
        if controlador not in self._controladores:
            self._controladores.append(controlador)

    def desregistrar(self, controlador: "ControladorLogoAnimado") -> None:
        if controlador in self._controladores:
            self._controladores.remove(controlador)

    def establecer_reducir_movimiento(self, activo: bool) -> None:
        self.reducir_movimiento = bool(activo)
        self._sincronizar_todos()

    def establecer_minimizada(self, minimizada: bool) -> None:
        if self.ventana_minimizada == bool(minimizada):
            return
        self.ventana_minimizada = bool(minimizada)
        self._sincronizar_todos()

    def puede_animar(self) -> bool:
        return not self.reducir_movimiento and not self.ventana_minimizada

    def _sincronizar_todos(self) -> None:
        for ctrl in list(self._controladores):
            ctrl.evaluar_estado()

    def detener_todo(self) -> None:
        for ctrl in list(self._controladores):
            ctrl.detener()


class ControladorLogoAnimado:
    """Anima un CTkLabel con los fotogramas precalculados del logotipo oficial."""

    def __init__(
        self,
        label_widget: ctk.CTkLabel,
        ancho: int,
        alto: int,
        variante: str = "color",
        siempre_activo: bool = False,
        gestor: Optional[GestorAnimacionesGlobal] = None,
    ) -> None:
        self.label = label_widget
        self.ancho = ancho
        self.alto = alto
        self.variante = variante
        self.siempre_activo = siempre_activo
        self.gestor = gestor

        self.frames = obtener_frames_logo(ancho, alto, variante)
        self.indice = 0
        self.hover_activo = False
        self.procesando_contador = 0
        self._after_id: Optional[str] = None
        self._destruido = False

        self.label.configure(image=self.frames[0], text="")
        if self.gestor is not None:
            self.gestor.registrar(self)

        if not self.siempre_activo:
            self.label.bind("<Enter>", self._on_enter)
            self.label.bind("<Leave>", self._on_leave)

        self.evaluar_estado()

    def _on_enter(self, _event=None) -> None:
        self.hover_activo = True
        self.evaluar_estado()

    def _on_leave(self, _event=None) -> None:
        self.hover_activo = False
        self.evaluar_estado()

    def iniciar_procesamiento(self) -> None:
        """Activa la animación del header mientras la aplicación procesa una tarea."""
        self.procesando_contador += 1
        self.evaluar_estado()

    def detener_procesamiento(self) -> None:
        """Reduce el contador de tareas activas y detiene el loop al quedar en cero."""
        self.procesando_contador = max(0, self.procesando_contador - 1)
        self.evaluar_estado()

    def _debe_reproducir(self) -> bool:
        if self._destruido:
            return False
        if self.gestor is not None and not self.gestor.puede_animar():
            return False
        return self.siempre_activo or self.hover_activo or self.procesando_contador > 0

    def evaluar_estado(self) -> None:
        """Arranca o pausa el loop sin recrear recursos."""
        if self._destruido:
            return
        if self._debe_reproducir():
            if self._after_id is None:
                self._programar_siguiente()
        else:
            self._cancelar_after()
            self._mostrar_reposo()

    def _mostrar_reposo(self) -> None:
        self.indice = 0
        try:
            if self.label.winfo_exists():
                self.label.configure(image=self.frames[0])
        except Exception:
            pass

    def _programar_siguiente(self) -> None:
        try:
            if self.label.winfo_exists():
                self._after_id = self.label.after(tema.INTERVALO_LOGO_MS, self._avanzar_frame)
        except Exception:
            self._after_id = None

    def _avanzar_frame(self) -> None:
        self._after_id = None
        if not self._debe_reproducir():
            self._mostrar_reposo()
            return
        self.indice = (self.indice + 1) % len(self.frames)
        try:
            if self.label.winfo_exists():
                self.label.configure(image=self.frames[self.indice])
                self._programar_siguiente()
        except Exception:
            self._after_id = None

    def _cancelar_after(self) -> None:
        if self._after_id is not None:
            try:
                self.label.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def detener(self) -> None:
        self._destruido = True
        self._cancelar_after()
        if self.gestor is not None:
            self.gestor.desregistrar(self)


def animar_transicion_cambio_materia(
    widget_raiz: ctk.CTkBaseClass,
    tarjetas: List[ctk.CTkFrame],
    gestor: Optional[GestorAnimacionesGlobal] = None,
) -> None:
    """Realiza un pulso breve (~180 ms) sin destruir widgets al cambiar de materia."""
    if gestor is not None and not gestor.puede_animar():
        return

    originales = []
    for card in tarjetas:
        try:
            originales.append((card, card.cget("border_color"), card.cget("border_width")))
        except Exception:
            continue

    pasos = 6
    intervalo = max(20, tema.DURACION_TRANSICION_MS // pasos)

    def _aplicar_paso(paso: int) -> None:
        if not widget_raiz.winfo_exists():
            return
        enfasis = paso < 3
        for card, borde_orig, grosor_orig in originales:
            try:
                if card.winfo_exists():
                    if enfasis:
                        card.configure(border_color=tema.BORDE_ACTIVO, border_width=tema.BORDE_FOCO)
                    else:
                        card.configure(border_color=borde_orig, border_width=grosor_orig)
            except Exception:
                continue
        if paso < pasos:
            widget_raiz.after(intervalo, lambda: _aplicar_paso(paso + 1))

    _aplicar_paso(0)
