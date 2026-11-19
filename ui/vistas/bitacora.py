"""Vista Bitácora filtrable alimentada por bitacora-firmas.jsonl y bitacora-subidas.jsonl."""

from __future__ import annotations

from typing import Any, Dict, List

import customtkinter as ctk

from fuentes.dashboard_datos import construir_bitacora_unificada
from ui import componentes, iconos, tema


def _estilo_estado_bitacora(estado: str) -> str:
    bajo = (estado or "").lower()
    if bajo in {"firmado", "publicado", "vinculado", "completado"}:
        return "exito"
    if bajo in {"enviado", "en proceso"}:
        return "alerta"
    if "hallazgo" in bajo or "error" in bajo:
        return "error"
    return "info"


class _FilaBitacora(ctk.CTkFrame):
    """Fila de tabla reutilizable para eventos de bitácora."""

    def __init__(self, master) -> None:
        super().__init__(
            master,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE,
            border_width=tema.BORDE_NORMAL,
            border_color=tema.BORDE,
        )
        for col, peso in [(0, 2), (1, 2), (2, 3), (3, 3), (4, 1)]:
            self.grid_columnconfigure(col, weight=peso)

        self._lbl_fecha = ctk.CTkLabel(
            self,
            text="",
            font=tema.fuente("mono"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_fecha.grid(row=0, column=0, sticky="ew", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        self._lbl_usuario = ctk.CTkLabel(
            self,
            text="",
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_usuario.grid(row=0, column=1, sticky="ew", padx=tema.ESPACIO_SM, pady=tema.ESPACIO_SM)

        self._lbl_accion = ctk.CTkLabel(
            self,
            text="",
            font=tema.fuente("cuerpo_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_accion.grid(row=0, column=2, sticky="ew", padx=tema.ESPACIO_SM, pady=tema.ESPACIO_SM)

        self._lbl_ref = ctk.CTkLabel(
            self,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_ref.grid(row=0, column=3, sticky="ew", padx=tema.ESPACIO_SM, pady=tema.ESPACIO_SM)

        self._badge = componentes.BadgeEstado(self, "firmado", "exito")
        self._badge.grid(row=0, column=4, sticky="e", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

    def actualizar(self, ev: Dict[str, Any]) -> None:
        self._lbl_fecha.configure(text=ev.get("timestamp", ""))
        self._lbl_usuario.configure(text=ev.get("usuario", ""))
        self._lbl_accion.configure(text=ev.get("accion", ""))
        self._lbl_ref.configure(text=ev.get("referencia", ""))
        est = ev.get("estado", "info")
        self._badge.actualizar(est.capitalize(), _estilo_estado_bitacora(est))


class VistaBitacora(componentes.ScrollableCadence):
    """Tabla filtrable de auditoría y trazabilidad sobre salidas/*.jsonl."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._var_busqueda = ctk.StringVar(value="")
        self._var_origen = ctk.StringVar(value="Todos")
        self._var_estado = ctk.StringVar(value="Todos")

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        cab = ctk.CTkFrame(wrap, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        tit = ctk.CTkFrame(cab, fg_color="transparent")
        tit.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            tit,
            text="Bitácora de Auditoría y Trazabilidad",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        self._lbl_sub = ctk.CTkLabel(
            tit,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_sub.pack(fill="x", pady=(2, 0))

        componentes.BotonCadence(
            cab,
            texto="Recargar bitácoras",
            comando=self._recargar_desde_disco,
            variante="secundario",
            icono=iconos.obtener_icono("refresh", tema.ICONO_SM, tema.TEXTO_PRIMARIO),
        ).pack(side="right")

        # Filtros
        filtros = componentes.TarjetaCadence(wrap)
        filtros.pack(fill="x", pady=(0, tema.ESPACIO_MD))
        f_in = ctk.CTkFrame(filtros, fg_color="transparent")
        f_in.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        ctk.CTkEntry(
            f_in,
            textvariable=self._var_busqueda,
            placeholder_text="Filtrar por fecha, usuario, acción o clave...",
            height=tema.ALTO_BOTON_MD,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.INPUT_BG,
            border_color=tema.INPUT_BORDE,
            text_color=tema.TEXTO_PRIMARIO,
            placeholder_text_color=tema.TEXTO_SECUNDARIO,
            font=tema.fuente("cuerpo"),
        ).pack(side="left", fill="x", expand=True, padx=(0, tema.ESPACIO_MD))
        self._var_busqueda.trace_add("write", lambda *_: self.actualizar())

        ctk.CTkOptionMenu(
            f_in,
            values=["Todos", "Firmas", "Subidas"],
            variable=self._var_origen,
            command=lambda _v: self.actualizar(),
            height=tema.ALTO_BOTON_MD,
            width=140,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
            button_color=tema.BTN_PRIMARIO_BG,
            button_hover_color=tema.BTN_PRIMARIO_HOVER,
            text_color=tema.TEXTO_PRIMARIO,
            font=tema.fuente("cuerpo"),
            dropdown_font=tema.fuente("cuerpo"),
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        ctk.CTkOptionMenu(
            f_in,
            values=["Todos", "firmado", "enviado", "con hallazgos", "vinculado", "publicado", "sin enviar"],
            variable=self._var_estado,
            command=lambda _v: self.actualizar(),
            height=tema.ALTO_BOTON_MD,
            width=165,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
            button_color=tema.BTN_PRIMARIO_BG,
            button_hover_color=tema.BTN_PRIMARIO_HOVER,
            text_color=tema.TEXTO_PRIMARIO,
            font=tema.fuente("cuerpo"),
            dropdown_font=tema.fuente("cuerpo"),
        ).pack(side="left")

        # Encabezado de tabla
        self._encabezado = ctk.CTkFrame(
            wrap,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.FONDO_HEADER,
        )
        for col, peso in [(0, 2), (1, 2), (2, 3), (3, 3), (4, 1)]:
            self._encabezado.grid_columnconfigure(col, weight=peso)

        for col, titulo, ancla in [
            (0, "Fecha", "w"),
            (1, "Usuario", "w"),
            (2, "Acción", "w"),
            (3, "Referencia / Documento", "w"),
            (4, "Estado", "e"),
        ]:
            ctk.CTkLabel(
                self._encabezado,
                text=titulo,
                font=tema.fuente("cuerpo_bold"),
                text_color=tema.TEXTO_SOBRE_OSCURO,
                anchor=ancla,
            ).grid(row=0, column=col, sticky="ew", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)
        self._encabezado.pack(fill="x", pady=(0, tema.ESPACIO_SM))

        self._tabla = ctk.CTkFrame(wrap, fg_color="transparent")
        self._tabla.pack(fill="x")
        self._pool: List[_FilaBitacora] = []
        self._vacio = componentes.EstadoVacio(
            self._tabla,
            titulo="La bitácora aún no tiene registros visibles",
            mensaje=(
                "Cuando apruebes una firma digital, publiques un indicador o cargues un archivo local, "
                "los eventos aparecerán aquí desde salidas/bitacora-firmas.jsonl y bitacora-subidas.jsonl."
            ),
            icono_nombre="bitacora",
            texto_cta="Ir al panel principal",
            comando_cta=lambda: self.app.navegar_a("dashboard"),
        )
        self.actualizar()

    def _recargar_desde_disco(self) -> None:
        self.app.recargar_bitacoras_desde_disco()
        self.app.notificar("Bitácoras actualizadas", "Eventos leídos desde salidas/*.jsonl.", "info")

    def actualizar(self) -> None:
        eventos = construir_bitacora_unificada(self.app.datos)
        q = self._var_busqueda.get().strip().lower()
        orig = self._var_origen.get()
        est = self._var_estado.get().lower()

        filtrados = []
        for ev in eventos:
            if orig != "Todos" and ev.get("origen") != orig:
                continue
            if est != "todos" and (ev.get("estado", "").lower() != est):
                continue
            if q:
                blob = (
                    f"{ev.get('timestamp', '')} {ev.get('usuario', '')} "
                    f"{ev.get('accion', '')} {ev.get('referencia', '')} {ev.get('estado', '')}"
                ).lower()
                if q not in blob:
                    continue
            filtrados.append(ev)

        self._lbl_sub.configure(
            text=f"{len(filtrados)} eventos mostrados ({len(eventos)} totales en archivos .jsonl)"
        )

        if not filtrados:
            self._encabezado.pack_forget()
            for fila in self._pool:
                fila.pack_forget()
            self._vacio.pack(fill="x", pady=tema.ESPACIO_SM)
            return

        if not self._encabezado.winfo_manager():
            self._encabezado.pack(fill="x", pady=(0, tema.ESPACIO_SM), before=self._tabla)
        self._vacio.pack_forget()

        while len(self._pool) < len(filtrados):
            self._pool.append(_FilaBitacora(self._tabla))

        for idx, fila in enumerate(self._pool):
            if idx < len(filtrados):
                fila.actualizar(filtrados[idx])
                if not fila.winfo_manager():
                    fila.pack(fill="x", pady=(0, tema.ESPACIO_XS))
            else:
                fila.pack_forget()
