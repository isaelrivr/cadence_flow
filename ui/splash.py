"""Pantalla de arranque (Splash) de ~2 s con logotipo animado en degradado."""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from ui import animaciones, componentes, tema


class SplashCadence(ctk.CTkToplevel):
    """Splash screen centrada sobre fondo claro para lucir el logotipo oficial."""

    def __init__(
        self,
        master,
        gestor_animaciones: animaciones.GestorAnimacionesGlobal,
        al_finalizar: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=tema.FONDO_SPLASH)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self._al_finalizar = al_finalizar
        self._gestor = gestor_animaciones
        self._after_prog: Optional[str] = None
        self._cerrado = False

        # Borde sutil externo en azul petróleo
        marco = ctk.CTkFrame(
            self,
            corner_radius=tema.RADIO_MODAL,
            fg_color=tema.FONDO_SPLASH,
            border_width=tema.BORDE_NORMAL,
            border_color=tema.BORDE_ACTIVO,
        )
        marco.pack(fill="both", expand=True)

        # Franja superior en degradado simulado con barra al 100%
        franja = componentes.BarraProgresoDegradado(
            marco, progreso=1.0, ancho_inicial=520, alto=6, bg_token=tema.FONDO_SPLASH
        )
        franja.pack(fill="x", padx=tema.ESPACIO_LG, pady=(tema.ESPACIO_MD, 0))

        margen_c = tema.margen_libre_logo(tema.ALTO_LOGO_SPLASH)
        logo_box = ctk.CTkFrame(marco, fg_color=tema.FONDO_SPLASH)
        logo_box.pack(pady=(margen_c, tema.ESPACIO_MD), padx=margen_c)

        self._lbl_logo = ctk.CTkLabel(
            logo_box,
            text="",
            width=tema.ANCHO_LOGO_SPLASH,
            height=tema.ALTO_LOGO_SPLASH,
            fg_color=tema.FONDO_SPLASH,
        )
        self._lbl_logo.pack()

        self._ctrl_logo = animaciones.ControladorLogoAnimado(
            self._lbl_logo,
            ancho=tema.ANCHO_LOGO_SPLASH,
            alto=tema.ALTO_LOGO_SPLASH,
            variante="color",
            siempre_activo=True,
            gestor=self._gestor,
        )

        # Textos sobre fondo claro explícito con contraste de marca
        ctk.CTkLabel(
            marco,
            text=tema.ESLOGAN,
            font=tema.fuente("titulo_splash"),
            text_color=tema.MARCA_AZUL_PROFUNDO,
        ).pack(pady=(0, tema.ESPACIO_XS))

        ctk.CTkLabel(
            marco,
            text=f"{tema.NOMBRE_PRODUCTO}  ·  {tema.NOMBRE_EMPRESA}",
            font=tema.fuente("etiqueta"),
            text_color=tema.MARCA_GRIS_AZULADO,
        ).pack(pady=(0, tema.ESPACIO_LG))

        self._barra = componentes.BarraProgresoDegradado(
            marco,
            progreso=0.0,
            ancho_inicial=420,
            alto=10,
            bg_token=tema.FONDO_SPLASH,
        )
        self._barra.pack(fill="x", padx=tema.ESPACIO_XXXL)

        self._lbl_estado = ctk.CTkLabel(
            marco,
            text="Inicializando interfaz y sincronizando bitácoras...",
            font=tema.fuente("etiqueta"),
            text_color=tema.MARCA_AZUL_PETROLEO,
        )
        self._lbl_estado.pack(pady=(tema.ESPACIO_SM, tema.ESPACIO_XL))

        componentes.centrar_ventana(self, 560, 420)
        self._paso_actual = 0
        self._total_pasos = 24
        duracion = (
            tema.DURACION_SPLASH_REDUCIDO_MS
            if self._gestor.reducir_movimiento
            else tema.DURACION_SPLASH_MS
        )
        self._intervalo = max(20, duracion // self._total_pasos)
        self._after_prog = self.after(self._intervalo, self._avanzar)

    def _avanzar(self) -> None:
        self._after_prog = None
        if self._cerrado:
            return
        self._paso_actual += 1
        prog = min(1.0, self._paso_actual / float(self._total_pasos))
        self._barra.establecer_progreso(prog)

        if prog >= 0.72:
            self._lbl_estado.configure(text="Preparando panel de gestión académica...")
        elif prog >= 0.35:
            self._lbl_estado.configure(text="Cargando asignaturas e indicadores del periodo...")

        if self._paso_actual < self._total_pasos:
            self._after_prog = self.after(self._intervalo, self._avanzar)
        else:
            self.cerrar()

    def cerrar(self) -> None:
        if self._cerrado:
            return
        self._cerrado = True
        if self._after_prog is not None:
            try:
                self.after_cancel(self._after_prog)
            except Exception:
                pass
            self._after_prog = None
        self._ctrl_logo.detener()
        try:
            self.destroy()
        except Exception:
            pass
        self._al_finalizar()
