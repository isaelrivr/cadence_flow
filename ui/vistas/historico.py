"""Vista Drive Histórico alimentada desde bitácoras locales e histórico base."""

from __future__ import annotations

from typing import Any, Dict, List

import customtkinter as ctk

from fuentes.dashboard_datos import construir_historico
from ui import componentes, iconos, tema


def _variante_estado_historico(estado: str) -> str:
    bajo = (estado or "").lower()
    if bajo in {"firmado", "publicado", "vinculado"}:
        return "exito"
    if bajo in {"enviado", "en proceso"}:
        return "alerta"
    if "hallazgo" in bajo or "error" in bajo:
        return "error"
    return "info"


class _FilaHistorico(componentes.TarjetaCadence):
    """Fila reutilizable para documentos de Drive Histórico."""

    def __init__(self, master, al_ver_detalle) -> None:
        super().__init__(master)
        self._al_ver_detalle = al_ver_detalle
        self._item: Dict[str, Any] = {}

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        izq = ctk.CTkFrame(cont, fg_color="transparent")
        izq.pack(side="left", fill="x", expand=True)

        fila_tit = ctk.CTkFrame(izq, fg_color="transparent")
        fila_tit.pack(fill="x")

        ctk.CTkLabel(
            fila_tit,
            text="",
            image=iconos.obtener_icono("file", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_archivo = ctk.CTkLabel(
            fila_tit,
            text="",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_archivo.pack(side="left")

        self._lbl_meta = ctk.CTkLabel(
            izq,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_meta.pack(fill="x", pady=(3, 0))

        der = ctk.CTkFrame(cont, fg_color="transparent")
        der.pack(side="right", padx=(tema.ESPACIO_MD, 0))

        self._badge_origen = componentes.BadgeEstado(der, "Histórico", "info", con_nodo=False)
        self._badge_origen.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._badge_estado = componentes.BadgeEstado(der, "Firmado", "exito")
        self._badge_estado.pack(side="left", padx=(0, tema.ESPACIO_SM))

        componentes.BotonCadence(
            der,
            texto="Ver detalle",
            comando=lambda: self._al_ver_detalle(self._item),
            variante="secundario",
            tam="sm",
        ).pack(side="left")

    def actualizar(self, item: Dict[str, Any]) -> None:
        self._item = item
        self._lbl_archivo.configure(text=item.get("archivo", "Documento"))
        self._lbl_meta.configure(
            text=(
                f"{item.get('clave_materia', '')} · {item.get('materia', '')}  ·  "
                f"Por: {item.get('usuario', '')}  ·  {item.get('timestamp', '')}"
            )
        )
        origen = item.get("origen", "Histórico")
        var_origen = "info" if "Subida" in origen else ("alerta" if "Firma" in origen else "neutro")
        self._badge_origen.actualizar(origen, var_origen)

        estado = item.get("estado", "vinculado")
        self._badge_estado.actualizar(estado.capitalize(), _variante_estado_historico(estado))


class VistaHistorico(componentes.ScrollableCadence):
    """Repositorio histórico con búsqueda, filtros y carga local a salidas/."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._filtro_origen = "Todos"
        self._var_busqueda = ctk.StringVar(value="")

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        # Cabecera
        cab = ctk.CTkFrame(wrap, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        tit = ctk.CTkFrame(cab, fg_color="transparent")
        tit.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            tit,
            text="Drive Histórico y Respaldos",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        self._lbl_conteo = ctk.CTkLabel(
            tit,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_conteo.pack(fill="x", pady=(2, 0))

        componentes.BotonCadence(
            cab,
            texto="Cargar archivo local",
            comando=self.app.cargar_archivo_local,
            variante="primario",
            icono=iconos.obtener_icono("upload", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        ).pack(side="right")

        # Barra de búsqueda y filtro
        barra = componentes.TarjetaCadence(wrap)
        barra.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        barra_in = ctk.CTkFrame(barra, fg_color="transparent")
        barra_in.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        ctk.CTkLabel(
            barra_in,
            text="",
            image=iconos.obtener_icono("search", tema.ICONO_MD, tema.TEXTO_SECUNDARIO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._entry_busqueda = ctk.CTkEntry(
            barra_in,
            textvariable=self._var_busqueda,
            placeholder_text="Buscar por archivo, clave de asignatura o usuario...",
            height=tema.ALTO_BOTON_MD,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.INPUT_BG,
            border_color=tema.INPUT_BORDE,
            text_color=tema.TEXTO_PRIMARIO,
            placeholder_text_color=tema.TEXTO_SECUNDARIO,
            font=tema.fuente("cuerpo"),
        )
        self._entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, tema.ESPACIO_MD))
        self._var_busqueda.trace_add("write", lambda *_: self.actualizar())

        self._seg_origen = ctk.CTkSegmentedButton(
            barra_in,
            values=["Todos", "Subida local", "Firma digital", "Histórico 2026EJ"],
            command=self._cambiar_origen,
            font=tema.fuente("boton_sm"),
            fg_color=tema.SUPERFICIE_SUTIL,
            selected_color=tema.BTN_PRIMARIO_BG,
            selected_hover_color=tema.BTN_PRIMARIO_HOVER,
            unselected_color=tema.SUPERFICIE_SUTIL,
            unselected_hover_color=tema.SUPERFICIE_HOVER,
            text_color=tema.TEXTO_PRIMARIO,
        )
        self._seg_origen.set("Todos")
        self._seg_origen.pack(side="right")

        self._lista = ctk.CTkFrame(wrap, fg_color="transparent")
        self._lista.pack(fill="x")
        self._pool: List[_FilaHistorico] = []
        self._vacio = componentes.EstadoVacio(
            self._lista,
            titulo="No se encontraron documentos",
            mensaje="Ningún archivo coincide con la búsqueda o filtro seleccionado.",
            icono_nombre="historico",
            texto_cta="Limpiar filtros",
            comando_cta=self._limpiar_filtros,
        )
        self.actualizar()

    def _cambiar_origen(self, valor: str) -> None:
        self._filtro_origen = valor
        self.actualizar()

    def _limpiar_filtros(self) -> None:
        self._var_busqueda.set("")
        self._filtro_origen = "Todos"
        self._seg_origen.set("Todos")
        self.actualizar()

    def actualizar(self) -> None:
        todos = construir_historico(self.app.datos)
        consulta = self._var_busqueda.get().strip().lower()

        filtrados = []
        for item in todos:
            if self._filtro_origen != "Todos" and item.get("origen") != self._filtro_origen:
                continue
            if consulta:
                blob = (
                    f"{item.get('archivo', '')} {item.get('clave_materia', '')} "
                    f"{item.get('materia', '')} {item.get('usuario', '')}"
                ).lower()
                if consulta not in blob:
                    continue
            filtrados.append(item)

        self._lbl_conteo.configure(
            text=f"{len(filtrados)} documentos mostrados de {len(todos)} registros totales (bitácoras + 2026EJ)"
        )

        if not filtrados:
            for fila in self._pool:
                fila.pack_forget()
            self._vacio.pack(fill="x", pady=tema.ESPACIO_SM)
            return

        self._vacio.pack_forget()
        while len(self._pool) < len(filtrados):
            self._pool.append(_FilaHistorico(self._lista, self._ver_detalle))

        for idx, fila in enumerate(self._pool):
            if idx < len(filtrados):
                fila.actualizar(filtrados[idx])
                if not fila.winfo_manager():
                    fila.pack(fill="x", pady=(0, tema.ESPACIO_SM))
            else:
                fila.pack_forget()

    def _ver_detalle(self, item: Dict[str, Any]) -> None:
        ruta = item.get("ruta_local") or "Respaldo institucional / bitácora"
        componentes.ModalConfirmacion(
            self.winfo_toplevel(),
            titulo=item.get("archivo", "Detalle de documento"),
            mensaje=(
                f"Asignatura: {item.get('materia', '')} ({item.get('clave_materia', '')})\n"
                f"Origen: {item.get('origen', '')}  ·  Estado: {item.get('estado', '')}\n"
                f"Usuario: {item.get('usuario', '')}\n"
                f"Fecha: {item.get('timestamp', '')}\n"
                f"Ubicación: {ruta}\n\n"
                f"{item.get('detalle', '')}"
            ),
            texto_confirmar="Cerrar",
            variante_confirmar="primario",
        )
