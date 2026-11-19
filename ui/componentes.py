"""Componentes reutilizables de Cadence Flow construidos sobre CustomTkinter.

Todos los colores, tipografías, radios y espaciados provienen exclusivamente
de ui.tema. Incluye accesibilidad por teclado, scroll fluido multiplataforma,
badges semánticos, barra de progreso en degradado, tooltips, toasts y modales.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional, Tuple

import customtkinter as ctk
from PIL import ImageTk

from ui import animaciones, iconos, tema


def _proteger_scrollbar_ctk(scrollbar) -> None:
    """Evita recursión en CTkScrollbar._draw -> update_idletasks bajo HiDPI."""
    if scrollbar is None or getattr(scrollbar, "_set_protegido", False):
        return
    orig_set = scrollbar.set

    def _set_seguro(start_value, end_value) -> None:
        s, e = float(start_value), float(end_value)
        if getattr(scrollbar, "_en_set", False):
            return
        prev_s = getattr(scrollbar, "_start_value", -1.0)
        prev_e = getattr(scrollbar, "_end_value", -1.0)
        if abs(s - prev_s) < 1e-6 and abs(e - prev_e) < 1e-6:
            return
        scrollbar._en_set = True
        try:
            orig_set(s, e)
        finally:
            scrollbar._en_set = False

    scrollbar.set = _set_seguro
    scrollbar._set_protegido = True


def habilitar_scroll_fluido(scroll_frame: ctk.CTkScrollableFrame) -> None:
    """Asegura scroll con rueda seguro y fluido en Windows, macOS y Linux."""
    _proteger_scrollbar_ctk(getattr(scroll_frame, "_scrollbar", None))
    orig_check = getattr(scroll_frame, "_check_if_valid_scroll", None)
    if orig_check is None or getattr(scroll_frame, "_scroll_parcheado", False):
        return

    def _check_seguro(widget) -> bool:
        if isinstance(widget, str) or widget is None:
            return False
        try:
            if not scroll_frame.winfo_ismapped():
                return False
        except Exception:
            return False
        return bool(orig_check(widget))

    scroll_frame._check_if_valid_scroll = _check_seguro  # type: ignore[attr-defined]
    scroll_frame._scroll_parcheado = True  # type: ignore[attr-defined]


class ScrollableCadence(ctk.CTkScrollableFrame):
    """Contenedor desplazable estilizado según los tokens de Cadence Flow."""

    def __init__(self, master, **kwargs) -> None:
        kwargs.setdefault("fg_color", tema.FONDO_APP)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("scrollbar_fg_color", tema.SCROLLBAR_TRACK)
        kwargs.setdefault("scrollbar_button_color", tema.SCROLLBAR_THUMB)
        kwargs.setdefault("scrollbar_button_hover_color", tema.SCROLLBAR_THUMB_HOVER)
        super().__init__(master, **kwargs)
        habilitar_scroll_fluido(self)


class BotonCadence(ctk.CTkButton):
    """Botón accesible con variantes de marca, foco visible y soporte de teclado."""

    _ESTILOS = {
        "primario": (tema.BTN_PRIMARIO_BG, tema.BTN_PRIMARIO_HOVER, tema.BTN_PRIMARIO_TEXTO, tema.BTN_PRIMARIO_BG, 0),
        "oscuro": (tema.BTN_OSCURO_BG, tema.BTN_OSCURO_HOVER, tema.BTN_OSCURO_TEXTO, tema.BTN_OSCURO_BG, 0),
        "secundario": (tema.BTN_SECUNDARIO_BG, tema.BTN_SECUNDARIO_HOVER, tema.BTN_SECUNDARIO_TEXTO, tema.BORDE, tema.BORDE_NORMAL),
        "cian": (tema.BTN_CIAN_BG, tema.BTN_CIAN_HOVER, tema.BTN_CIAN_TEXTO, tema.BTN_CIAN_BG, 0),
        "fantasma": ("transparent", tema.SUPERFICIE_HOVER, tema.TEXTO_PRIMARIO, tema.BORDE, tema.BORDE_NORMAL),
        "exito": (tema.BTN_EXITO_BG, tema.BTN_EXITO_HOVER, tema.BTN_EXITO_TEXTO, tema.BTN_EXITO_BG, 0),
        "peligro": (tema.BTN_PELIGRO_BG, tema.BTN_PELIGRO_HOVER, tema.BTN_PELIGRO_TEXTO, tema.BTN_PELIGRO_BG, 0),
    }

    def __init__(
        self,
        master,
        texto: str,
        comando: Optional[Callable[[], None]] = None,
        variante: str = "primario",
        tam: str = "md",
        icono: Optional[ctk.CTkImage] = None,
        ancho: Optional[int] = None,
        habilitado: bool = True,
        **kwargs,
    ) -> None:
        fg, hov, txt, borde, grosor = self._ESTILOS.get(variante, self._ESTILOS["primario"])
        alto = (
            tema.ALTO_BOTON_SM
            if tam == "sm"
            else (tema.ALTO_BOTON_LG if tam == "lg" else tema.ALTO_BOTON_MD)
        )
        fuente_btn = tema.fuente("boton_sm" if tam == "sm" else "boton")

        self._variante = variante
        self._fg_normal = fg
        self._borde_normal = borde
        self._grosor_normal = grosor
        self._texto_color_normal = txt
        self._comando_usuario = comando

        cfg = {
            "text": texto,
            "command": self._ejecutar_si_activo,
            "height": alto,
            "corner_radius": tema.RADIO_BOTON,
            "fg_color": fg,
            "hover_color": hov,
            "text_color": txt,
            "text_color_disabled": tema.BTN_DESHABILITADO_TEXTO,
            "border_color": borde,
            "border_width": grosor,
            "font": fuente_btn,
            "image": icono,
            "compound": "left",
        }
        if ancho is not None:
            cfg["width"] = ancho
        cfg.update(kwargs)
        super().__init__(master, **cfg)

        self.configure(cursor=tema.CURSOR_MANO)
        self._configurar_accesibilidad_teclado()
        self.establecer_habilitado(habilitado)

    def _configurar_accesibilidad_teclado(self) -> None:
        """Habilita Tab, Enter, Espacio y anillo de foco visible en el lienzo interno."""
        canvas = getattr(self, "_canvas", None)
        if canvas is None:
            return
        try:
            canvas.configure(takefocus=1)
            canvas.bind("<FocusIn>", self._al_enfocar, add="+")
            canvas.bind("<FocusOut>", self._al_desenfocar, add="+")
            canvas.bind("<Return>", self._al_activar_tecla, add="+")
            canvas.bind("<space>", self._al_activar_tecla, add="+")
        except Exception:
            pass

    def _al_enfocar(self, _event=None) -> None:
        if self.cget("state") == "normal":
            self.configure(border_color=tema.FOCO_BORDE, border_width=tema.BORDE_FOCO)

    def _al_desenfocar(self, _event=None) -> None:
        self.configure(border_color=self._borde_normal, border_width=self._grosor_normal)

    def _al_activar_tecla(self, _event=None) -> str:
        self._ejecutar_si_activo()
        return "break"

    def _ejecutar_si_activo(self) -> None:
        if self.cget("state") == "normal" and self._comando_usuario is not None:
            self._comando_usuario()

    def actualizar_comando(self, comando: Optional[Callable[[], None]]) -> None:
        self._comando_usuario = comando

    def establecer_variante(self, variante: str) -> None:
        fg, hov, txt, borde, grosor = self._ESTILOS.get(variante, self._ESTILOS["primario"])
        self._variante = variante
        self._fg_normal = fg
        self._borde_normal = borde
        self._grosor_normal = grosor
        self._texto_color_normal = txt
        if self.cget("state") == "normal":
            self.configure(
                fg_color=fg,
                hover_color=hov,
                text_color=txt,
                border_color=borde,
                border_width=grosor,
            )

    def establecer_habilitado(self, habilitado: bool) -> None:
        """Actualiza estado interactivo, foco por teclado y cursor."""
        estado = "normal" if habilitado else "disabled"
        self.configure(
            state=estado,
            fg_color=self._fg_normal if habilitado else tema.BTN_DESHABILITADO_BG,
            text_color=self._texto_color_normal if habilitado else tema.BTN_DESHABILITADO_TEXTO,
            cursor=tema.CURSOR_MANO if habilitado else tema.CURSOR_NORMAL,
        )
        canvas = getattr(self, "_canvas", None)
        if canvas is not None:
            try:
                canvas.configure(takefocus=1 if habilitado else 0)
            except Exception:
                pass


class BadgeEstado(ctk.CTkFrame):
    """Chip de estado semántico con nodo geométrico y actualización in-place."""

    def __init__(
        self,
        master,
        texto: str,
        variante: str = "info",
        con_nodo: bool = True,
        **kwargs,
    ) -> None:
        estilos = tema.SEMANTICO.get(variante, tema.SEMANTICO["info"])
        super().__init__(
            master,
            corner_radius=tema.RADIO_PILL,
            fg_color=estilos["bg"],
            border_color=estilos["borde"],
            border_width=tema.BORDE_NORMAL,
            **kwargs,
        )
        self._con_nodo = con_nodo
        self._lbl_icono: Optional[ctk.CTkLabel] = None
        if con_nodo:
            self._lbl_icono = ctk.CTkLabel(
                self,
                text="",
                image=iconos.obtener_icono("hex_node", 12, estilos["fg"]),
                width=12,
                height=14,
            )
            self._lbl_icono.pack(side="left", padx=(tema.ESPACIO_SM, 2), pady=3)

        self._lbl_texto = ctk.CTkLabel(
            self,
            text=texto,
            font=tema.fuente("badge"),
            text_color=estilos["fg"],
            height=18,
        )
        padx_izq = 2 if con_nodo else tema.ESPACIO_MD
        self._lbl_texto.pack(side="left", padx=(padx_izq, tema.ESPACIO_MD), pady=3)

    def actualizar(self, texto: str, variante: str = "info") -> None:
        """Actualiza texto y colores semánticos sin destruir el widget."""
        estilos = tema.SEMANTICO.get(variante, tema.SEMANTICO["info"])
        self.configure(fg_color=estilos["bg"], border_color=estilos["borde"])
        self._lbl_texto.configure(text=texto, text_color=estilos["fg"])
        if self._lbl_icono is not None:
            self._lbl_icono.configure(image=iconos.obtener_icono("hex_node", 12, estilos["fg"]))


class TarjetaCadence(ctk.CTkFrame):
    """Contenedor tarjeta con radio uniforme, borde nítido y acento opcional."""

    def __init__(
        self,
        master,
        con_acento: bool = False,
        color_acento: str | Tuple[str, str] = tema.BORDE_ACTIVO,
        **kwargs,
    ) -> None:
        kwargs.setdefault("corner_radius", tema.RADIO_TARJETA)
        kwargs.setdefault("fg_color", tema.SUPERFICIE)
        kwargs.setdefault("border_width", tema.BORDE_NORMAL)
        kwargs.setdefault("border_color", tema.BORDE)
        super().__init__(master, **kwargs)

        self._barra_acento: Optional[ctk.CTkFrame] = None
        if con_acento:
            self._barra_acento = ctk.CTkFrame(
                self,
                height=3,
                corner_radius=2,
                fg_color=color_acento,
            )
            self._barra_acento.pack(
                fill="x",
                padx=tema.ESPACIO_LG,
                pady=(tema.ESPACIO_SM, 0),
            )


class TarjetaKPI(TarjetaCadence):
    """Tarjeta de métrica clave con jerarquía clara y actualización in-place."""

    def __init__(
        self,
        master,
        titulo: str,
        valor: str,
        detalle: str = "",
        icono_nombre: str = "hex_node",
        color_valor: str | Tuple[str, str] = tema.TEXTO_PRIMARIO,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        fila_top = ctk.CTkFrame(cuerpo, fg_color="transparent")
        fila_top.pack(fill="x")

        self._icono = ctk.CTkLabel(
            fila_top,
            text="",
            image=iconos.obtener_icono(icono_nombre, tema.ICONO_SM, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_SM,
        )
        self._icono.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_titulo = ctk.CTkLabel(
            fila_top,
            text=titulo,
            font=tema.fuente("kpi_titulo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_titulo.pack(side="left", fill="x", expand=True)

        self._lbl_valor = ctk.CTkLabel(
            cuerpo,
            text=valor,
            font=tema.fuente("kpi_valor"),
            text_color=color_valor,
            anchor="w",
        )
        self._lbl_valor.pack(fill="x", pady=(tema.ESPACIO_SM, 2))

        self._lbl_detalle = ctk.CTkLabel(
            cuerpo,
            text=detalle,
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_detalle.pack(fill="x")

    def actualizar(
        self,
        valor: str,
        detalle: Optional[str] = None,
        color_valor: Optional[str | Tuple[str, str]] = None,
    ) -> None:
        self._lbl_valor.configure(text=valor)
        if color_valor is not None:
            self._lbl_valor.configure(text_color=color_valor)
        if detalle is not None:
            self._lbl_detalle.configure(text=detalle)


class BarraProgresoDegradado(ctk.CTkFrame):
    """Barra de progreso con el degradado oficial cian -> petróleo -> azul profundo."""

    def __init__(
        self,
        master,
        progreso: float = 0.0,
        ancho_inicial: int = 240,
        alto: int = tema.ALTO_BARRA_PROGRESO,
        bg_token: str | Tuple[str, str] = tema.SUPERFICIE,
        **kwargs,
    ) -> None:
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, height=alto, **kwargs)
        self.pack_propagate(False)

        self._progreso = max(0.0, min(1.0, float(progreso)))
        self._ancho_inicial = max(60, int(ancho_inicial))
        self._alto_logico = max(6, int(alto))
        self._bg_token = bg_token
        self._ultimo_ancho = 0
        self._ultimo_alto = 0
        self._ultimo_prog = -1.0
        self._ultimo_modo = ""
        self._photo: Optional[ImageTk.PhotoImage] = None

        self._canvas = tk.Canvas(
            self,
            height=self._alto_logico,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._al_redimensionar, add="+")

        self._cb_tema = lambda _modo: self._dibujar(forzar=True)
        tema.suscribir_cambio_tema(self._cb_tema)
        self.bind("<Destroy>", self._limpiar, add="+")

    def _limpiar(self, _event=None) -> None:
        tema.desuscribir_cambio_tema(self._cb_tema)

    def _al_redimensionar(self, _event=None) -> None:
        self._dibujar(forzar=False)

    def establecer_progreso(self, progreso: float) -> None:
        """Actualiza el progreso (0.0 a 1.0) re-renderizando solo si cambió."""
        nuevo = max(0.0, min(1.0, float(progreso)))
        if abs(nuevo - self._progreso) < 0.005 and self._photo is not None:
            return
        self._progreso = nuevo
        self._dibujar(forzar=False)

    def _dibujar(self, forzar: bool = False) -> None:
        if not self._canvas.winfo_exists():
            return
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w < 12 or h < 4:
            w = self._ancho_inicial
            h = self._alto_logico
        modo = tema.obtener_modo_actual()
        if (
            not forzar
            and abs(w - self._ultimo_ancho) < 3
            and abs(h - self._ultimo_alto) < 2
            and abs(self._progreso - self._ultimo_prog) < 0.005
            and modo == self._ultimo_modo
            and self._photo is not None
        ):
            return

        fondo = tema.resolver_color(self._bg_token, modo)
        img = animaciones.crear_imagen_barra_degradada(w, h, self._progreso, modo=modo)
        self._photo = ImageTk.PhotoImage(img)
        self._canvas.configure(bg=fondo)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo)

        self._ultimo_ancho = w
        self._ultimo_alto = h
        self._ultimo_prog = self._progreso
        self._ultimo_modo = modo


class SeparadorCircuito(ctk.CTkFrame):
    """Línea divisoria sutil estilo pista de PCB con nodos circulares."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", height=12, **kwargs)
        self._canvas = tk.Canvas(self, height=12, highlightthickness=0, bd=0)
        self._canvas.pack(fill="x", expand=True)
        self._canvas.bind("<Configure>", self._dibujar, add="+")
        self._cb_tema = lambda _modo: self._dibujar()
        tema.suscribir_cambio_tema(self._cb_tema)
        self.bind("<Destroy>", self._limpiar, add="+")

    def _limpiar(self, _event=None) -> None:
        tema.desuscribir_cambio_tema(self._cb_tema)

    def _dibujar(self, _event=None) -> None:
        if not self._canvas.winfo_exists():
            return
        w = max(80, self._canvas.winfo_width())
        h = 12
        cy = h // 2
        fondo = tema.resolver_color(tema.FONDO_APP)
        linea = tema.resolver_color(tema.CIRCUITO_LINEA)
        nodo = tema.resolver_color(tema.CIRCUITO_NODO)

        self._canvas.configure(bg=fondo)
        self._canvas.delete("all")
        self._canvas.create_line(6, cy, w - 6, cy, fill=linea, width=1)
        for nx in (8, w // 3, w - 8):
            self._canvas.create_oval(nx - 3, cy - 3, nx + 3, cy + 3, fill=nodo, outline=fondo, width=1)


class TooltipCadence:
    """Tooltip flotante no intrusivo para controles e indicadores."""

    def __init__(self, widget, texto: str) -> None:
        self.widget = widget
        self.texto = texto
        self._after_id: Optional[str] = None
        self._ventana: Optional[tk.Toplevel] = None

        widget.bind("<Enter>", self._programar, add="+")
        widget.bind("<Leave>", self._ocultar, add="+")
        widget.bind("<ButtonPress>", self._ocultar, add="+")
        widget.bind("<Destroy>", self._ocultar, add="+")

    def actualizar_texto(self, texto: str) -> None:
        self.texto = texto

    def _programar(self, _event=None) -> None:
        self._cancelar()
        if not self.texto:
            return
        try:
            self._after_id = self.widget.after(tema.DELAY_TOOLTIP_MS, self._mostrar)
        except Exception:
            self._after_id = None

    def _mostrar(self) -> None:
        self._after_id = None
        if self._ventana is not None or not self.widget.winfo_exists():
            return
        try:
            wx = self.widget.winfo_rootx() + 12
            wy = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except Exception:
            return

        win = tk.Toplevel(self.widget)
        win.wm_overrideredirect(True)
        win.wm_attributes("-topmost", True)

        bg = tema.resolver_color(tema.FONDO_HEADER)
        fg = tema.resolver_color(tema.TEXTO_SOBRE_OSCURO)
        borde = tema.resolver_color(tema.BORDE_ACTIVO)

        marco = tk.Frame(win, bg=borde, padx=1, pady=1)
        marco.pack()
        lbl = tk.Label(
            marco,
            text=self.texto,
            bg=bg,
            fg=fg,
            font=(tema.familia_principal(), 10),
            padx=10,
            pady=6,
            justify="left",
            wraplength=300,
        )
        lbl.pack()

        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        tw = win.winfo_reqwidth()
        th = win.winfo_reqheight()
        wx = min(wx, max(8, sw - tw - 12))
        if wy + th > sh - 12:
            wy = max(8, self.widget.winfo_rooty() - th - 6)
        win.wm_geometry(f"+{wx}+{wy}")
        self._ventana = win

    def _cancelar(self) -> None:
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _ocultar(self, _event=None) -> None:
        self._cancelar()
        if self._ventana is not None:
            try:
                self._ventana.destroy()
            except Exception:
                pass
            self._ventana = None


class EstadoVacio(TarjetaCadence):
    """Estado vacío claro y accionable cuando no hay datos o resultados."""

    def __init__(
        self,
        master,
        titulo: str,
        mensaje: str,
        icono_nombre: str = "file",
        texto_cta: Optional[str] = None,
        comando_cta: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        centro = ctk.CTkFrame(self, fg_color="transparent")
        centro.pack(expand=True, padx=tema.ESPACIO_XXXL, pady=tema.ESPACIO_XXXL)

        ctk.CTkLabel(
            centro,
            text="",
            image=iconos.obtener_icono(icono_nombre, tema.ICONO_XL, tema.MARCA_AZUL_PETROLEO),
        ).pack(pady=(0, tema.ESPACIO_MD))

        ctk.CTkLabel(
            centro,
            text=titulo,
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
        ).pack(pady=(0, tema.ESPACIO_XS))

        ctk.CTkLabel(
            centro,
            text=mensaje,
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            wraplength=460,
            justify="center",
        ).pack(pady=(0, tema.ESPACIO_LG))

        if texto_cta and comando_cta is not None:
            BotonCadence(
                centro,
                texto=texto_cta,
                comando=comando_cta,
                variante="primario",
            ).pack()


class ToastManager:
    """Notificaciones flotantes no bloqueantes apiladas en la esquina inferior derecha."""

    def __init__(self, master_root: ctk.CTk) -> None:
        self.root = master_root
        self._contenedor = ctk.CTkFrame(
            master_root,
            fg_color="transparent",
            corner_radius=0,
        )
        self._toasts: List[ctk.CTkFrame] = []

    def mostrar(self, titulo: str, mensaje: str = "", tipo: str = "info") -> None:
        estilos = tema.SEMANTICO.get(tipo, tema.SEMANTICO["info"])
        icono_map = {"exito": "check", "alerta": "alert", "error": "error", "info": "info"}
        icono_nom = icono_map.get(tipo, "info")

        toast = ctk.CTkFrame(
            self._contenedor,
            corner_radius=tema.RADIO_TARJETA,
            fg_color=tema.SUPERFICIE,
            border_width=tema.BORDE_NORMAL,
            border_color=estilos["borde"],
            width=360,
        )
        toast.pack(side="bottom", fill="x", pady=(tema.ESPACIO_SM, 0))

        franja = ctk.CTkFrame(toast, width=5, corner_radius=3, fg_color=estilos["fg"])
        franja.pack(side="left", fill="y", padx=(6, 0), pady=6)

        cuerpo = ctk.CTkFrame(toast, fg_color="transparent")
        cuerpo.pack(side="left", fill="both", expand=True, padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        fila_tit = ctk.CTkFrame(cuerpo, fg_color="transparent")
        fila_tit.pack(fill="x")

        ctk.CTkLabel(
            fila_tit,
            text="",
            image=iconos.obtener_icono(icono_nom, tema.ICONO_SM, estilos["fg"]),
            width=tema.ICONO_SM,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            fila_tit,
            text=titulo,
            font=tema.fuente("cuerpo_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        btn_cerrar = ctk.CTkLabel(
            fila_tit,
            text="×",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_SECUNDARIO,
            cursor=tema.CURSOR_MANO,
            width=20,
        )
        btn_cerrar.pack(side="right")
        btn_cerrar.bind("<Button-1>", lambda _e, t=toast: self._cerrar(t))

        if mensaje:
            ctk.CTkLabel(
                cuerpo,
                text=mensaje,
                font=tema.fuente("etiqueta"),
                text_color=tema.TEXTO_SECUNDARIO,
                anchor="w",
                justify="left",
                wraplength=290,
            ).pack(fill="x", pady=(2, 0))

        self._toasts.append(toast)
        self._reposicionar()
        self.root.after(tema.DURACION_TOAST_MS, lambda t=toast: self._cerrar(t))

    def _reposicionar(self) -> None:
        if self._toasts:
            self._contenedor.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
            self._contenedor.lift()
        else:
            self._contenedor.place_forget()

    def _cerrar(self, toast: ctk.CTkFrame) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
        try:
            if toast.winfo_exists():
                toast.destroy()
        except Exception:
            pass
        self._reposicionar()


def centrar_ventana(ventana: ctk.CTk | ctk.CTkToplevel, ancho: int, alto: int, padre=None) -> None:
    """Centra una ventana respecto a su padre o pantalla actual sin salir de límites."""
    ventana.update_idletasks()
    sw = ventana.winfo_screenwidth()
    sh = ventana.winfo_screenheight()
    w = min(ancho, max(400, sw - 40))
    h = min(alto, max(300, sh - 60))

    if padre is not None and padre.winfo_exists():
        px = padre.winfo_rootx()
        py = padre.winfo_rooty()
        pw = padre.winfo_width()
        ph = padre.winfo_height()
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
    else:
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)

    x = max(8, min(x, sw - w - 8))
    y = max(8, min(y, sh - h - 32))
    ventana.geometry(f"{w}x{h}+{x}+{y}")


class ModalConfirmacion(ctk.CTkToplevel):
    """Modal accesible de confirmación para acciones críticas o firma digital."""

    def __init__(
        self,
        master,
        titulo: str,
        mensaje: str,
        texto_confirmar: str = "Confirmar",
        variante_confirmar: str = "primario",
        requerir_check: bool = False,
        texto_check: str = "",
        al_confirmar: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(master, fg_color=tema.FONDO_APP)
        self.title(titulo)
        self.resizable(False, False)
        self.transient(master)
        self._al_confirmar = al_confirmar
        self._requerir_check = requerir_check
        self._check_var = ctk.BooleanVar(value=not requerir_check)

        if tema.ICONO_ICO_PATH.exists():
            try:
                self.iconbitmap(str(tema.ICONO_ICO_PATH))
            except Exception:
                pass

        tarjeta = TarjetaCadence(self, con_acento=True)
        tarjeta.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_LG)

        cont = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        ctk.CTkLabel(
            cont,
            text=titulo,
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", pady=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            cont,
            text=mensaje,
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
            justify="left",
            wraplength=420,
        ).pack(fill="x", pady=(0, tema.ESPACIO_MD))

        if requerir_check:
            chk = ctk.CTkCheckBox(
                cont,
                text=texto_check or "Confirmo explícitamente esta acción.",
                variable=self._check_var,
                command=self._actualizar_estado_confirmar,
                font=tema.fuente("cuerpo_bold"),
                text_color=tema.TEXTO_PRIMARIO,
                fg_color=tema.BTN_PRIMARIO_BG,
                hover_color=tema.BTN_PRIMARIO_HOVER,
                border_color=tema.BORDE_ACTIVO,
            )
            chk.pack(fill="x", pady=(0, tema.ESPACIO_LG))

        acciones = ctk.CTkFrame(cont, fg_color="transparent")
        acciones.pack(fill="x", pady=(tema.ESPACIO_SM, 0))

        self._btn_confirmar = BotonCadence(
            acciones,
            texto=texto_confirmar,
            comando=self._confirmar,
            variante=variante_confirmar,
            habilitado=not requerir_check,
        )
        self._btn_confirmar.pack(side="right", padx=(tema.ESPACIO_SM, 0))

        BotonCadence(
            acciones,
            texto="Cancelar",
            comando=self.destroy,
            variante="secundario",
        ).pack(side="right")

        self.bind("<Escape>", lambda _e: self.destroy())
        centrar_ventana(self, 490, 275 if requerir_check else 230, padre=master)
        self.grab_set()
        self.focus_set()

    def _actualizar_estado_confirmar(self) -> None:
        self._btn_confirmar.establecer_habilitado(bool(self._check_var.get()))

    def _confirmar(self) -> None:
        if self._requerir_check and not self._check_var.get():
            return
        cb = self._al_confirmar
        self.destroy()
        if cb is not None:
            cb()


class ModalHallazgo(ctk.CTkToplevel):
    """Modal para capturar observaciones o hallazgos del verificador."""

    def __init__(
        self,
        master,
        nombre_materia: str,
        al_guardar: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color=tema.FONDO_APP)
        self.title("Reportar hallazgo de verificación")
        self.resizable(False, False)
        self.transient(master)
        self._al_guardar = al_guardar

        if tema.ICONO_ICO_PATH.exists():
            try:
                self.iconbitmap(str(tema.ICONO_ICO_PATH))
            except Exception:
                pass

        tarjeta = TarjetaCadence(self, con_acento=True)
        tarjeta.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_LG)

        cont = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        ctk.CTkLabel(
            cont,
            text="Reportar hallazgo",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            cont,
            text=f"Asignatura: {nombre_materia}",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", pady=(2, tema.ESPACIO_MD))

        self._texto = ctk.CTkTextbox(
            cont,
            height=96,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.INPUT_BG,
            border_color=tema.INPUT_BORDE,
            border_width=tema.BORDE_NORMAL,
            text_color=tema.TEXTO_PRIMARIO,
            font=tema.fuente("cuerpo"),
        )
        self._texto.pack(fill="both", expand=True)
        self._texto.insert("1.0", "Falta adjuntar evidencia de rúbrica firmada en unidad correspondiente.")

        self._lbl_error = ctk.CTkLabel(
            cont,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.SEMANTICO["error"]["fg"],
            anchor="w",
        )
        self._lbl_error.pack(fill="x", pady=(tema.ESPACIO_XS, tema.ESPACIO_SM))

        acciones = ctk.CTkFrame(cont, fg_color="transparent")
        acciones.pack(fill="x")

        BotonCadence(
            acciones,
            texto="Registrar hallazgo",
            comando=self._guardar,
            variante="peligro",
        ).pack(side="right", padx=(tema.ESPACIO_SM, 0))

        BotonCadence(
            acciones,
            texto="Cancelar",
            comando=self.destroy,
            variante="secundario",
        ).pack(side="right")

        self.bind("<Escape>", lambda _e: self.destroy())
        centrar_ventana(self, 490, 295, padre=master)
        self.grab_set()
        self._texto.focus_set()

    def _guardar(self) -> None:
        detalle = self._texto.get("1.0", "end").strip()
        if len(detalle) < 8:
            self._lbl_error.configure(text="Describe el hallazgo con al menos 8 caracteres.")
            return
        cb = self._al_guardar
        self.destroy()
        cb(detalle)
