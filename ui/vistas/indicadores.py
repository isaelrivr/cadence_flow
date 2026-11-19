"""Vista interactiva de indicadores y gestión de evidencias (Fase 2 · Cierre)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import customtkinter as ctk

from fuentes.dashboard_datos import recalcular_indicador
from fuentes.persistencia import registrar_evento_firma
from ui import animaciones, componentes, iconos, tema
from ui.vistas.dashboard import (
    _estilo_evidencia,
    _estilo_publicacion,
    _estilo_valoracion,
)


class _TarjetaIndicadorDetalle(componentes.TarjetaCadence):
    """Tarjeta interactiva para marcar evidencias (0/3 a 3/3) y publicar indicador."""

    def __init__(self, master, al_cambiar_evidencia, al_publicar) -> None:
        super().__init__(master)
        self._al_cambiar = al_cambiar_evidencia
        self._al_publicar = al_publicar
        self._indicador: Optional[Dict[str, Any]] = None
        self._vars: List[ctk.BooleanVar] = [ctk.BooleanVar(value=False) for _ in range(3)]
        self._checks: List[ctk.CTkCheckBox] = []

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_LG)

        # Cabecera del indicador
        cab = ctk.CTkFrame(cont, fg_color="transparent")
        cab.pack(fill="x")

        izq = ctk.CTkFrame(cab, fg_color="transparent")
        izq.pack(side="left", fill="x", expand=True)

        fila_tit = ctk.CTkFrame(izq, fg_color="transparent")
        fila_tit.pack(fill="x")

        ctk.CTkLabel(
            fila_tit,
            text="",
            image=iconos.obtener_icono("indicadores", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_clave = ctk.CTkLabel(
            fila_tit,
            text="",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_clave.pack(side="left")

        self._lbl_meta = ctk.CTkLabel(
            fila_tit,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
        )
        self._lbl_meta.pack(side="left", padx=(tema.ESPACIO_MD, 0))

        self._lbl_desc = ctk.CTkLabel(
            izq,
            text="",
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_desc.pack(fill="x", pady=(2, 0))

        der = ctk.CTkFrame(cab, fg_color="transparent")
        der.pack(side="right")

        self._badge_pub = componentes.BadgeEstado(der, "Sin publicar", "neutro")
        self._badge_pub.pack(side="right", padx=(tema.ESPACIO_SM, 0))
        self._badge_val = componentes.BadgeEstado(der, "Sin evaluar", "neutro", con_nodo=False)
        self._badge_val.pack(side="right", padx=(tema.ESPACIO_SM, 0))
        self._badge_ev = componentes.BadgeEstado(der, "Pendiente", "neutro", con_nodo=False)
        self._badge_ev.pack(side="right")

        # Progreso y cálculo
        prog_row = ctk.CTkFrame(cont, fg_color="transparent")
        prog_row.pack(fill="x", pady=(tema.ESPACIO_MD, tema.ESPACIO_SM))

        self._lbl_sel = ctk.CTkLabel(
            prog_row,
            text="Selección: 0/3",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            width=130,
            anchor="w",
        )
        self._lbl_sel.pack(side="left")

        self._barra = componentes.BarraProgresoDegradado(prog_row, progreso=0.0, ancho_inicial=320)
        self._barra.pack(side="left", fill="x", expand=True, padx=tema.ESPACIO_MD)

        self._lbl_pct = ctk.CTkLabel(
            prog_row,
            text="-- %",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            width=64,
            anchor="e",
        )
        self._lbl_pct.pack(side="left")

        # Lista de 3 evidencias interactivas
        caja_ev = ctk.CTkFrame(
            cont,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
        )
        caja_ev.pack(fill="x", pady=(tema.ESPACIO_SM, tema.ESPACIO_MD))

        ev_inner = ctk.CTkFrame(caja_ev, fg_color="transparent")
        ev_inner.pack(fill="x", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        for idx in range(3):
            chk = ctk.CTkCheckBox(
                ev_inner,
                text="",
                variable=self._vars[idx],
                command=lambda i=idx: self._toggle_evidencia(i),
                font=tema.fuente("cuerpo"),
                text_color=tema.TEXTO_PRIMARIO,
                fg_color=tema.BTN_PRIMARIO_BG,
                hover_color=tema.BTN_PRIMARIO_HOVER,
                border_color=tema.BORDE_ACTIVO,
            )
            chk.pack(anchor="w", pady=3)
            self._checks.append(chk)

        # Pie de tarjeta con publicación
        pie = ctk.CTkFrame(cont, fg_color="transparent")
        pie.pack(fill="x")

        self._lbl_ayuda = ctk.CTkLabel(
            pie,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_ayuda.pack(side="left", fill="x", expand=True)

        self._btn_publicar = componentes.BotonCadence(
            pie,
            texto="Publicar indicador",
            comando=self._invocar_publicar,
            variante="primario",
            icono=iconos.obtener_icono("check", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        )
        self._btn_publicar.pack(side="right")
        self._tooltip_pub = componentes.TooltipCadence(self._btn_publicar, "")

    def _toggle_evidencia(self, idx: int) -> None:
        if self._indicador is None:
            return
        items = self._indicador.get("evidencias_items", [])
        if idx < len(items):
            items[idx]["marcada"] = bool(self._vars[idx].get())
        recalcular_indicador(self._indicador)
        self.actualizar(self._indicador)
        self._al_cambiar()

    def _invocar_publicar(self) -> None:
        if self._indicador is not None:
            self._al_publicar(self._indicador)

    def actualizar(self, ind: Dict[str, Any]) -> None:
        self._indicador = ind
        self._lbl_clave.configure(text=ind.get("clave", ""))
        self._lbl_meta.configure(text=f"Meta: {ind.get('meta', '')}")
        self._lbl_desc.configure(text=ind.get("descripcion", ""))

        txt_ev, var_ev = _estilo_evidencia(ind.get("evidencias", "pendiente"))
        self._badge_ev.actualizar(txt_ev, var_ev)

        txt_val, var_val = _estilo_valoracion(ind.get("valoracion"))
        self._badge_val.actualizar(txt_val, var_val)

        pub = ind.get("publicacion", "pendiente")
        txt_pub, var_pub = _estilo_publicacion(pub)
        self._badge_pub.actualizar(txt_pub, var_pub)

        seleccion = ind.get("seleccion", "0/3")
        self._lbl_sel.configure(text=f"Selección: {seleccion}")

        pct = ind.get("porcentaje_logrado")
        if pct is None:
            self._lbl_pct.configure(text="-- %")
            self._barra.establecer_progreso(0.0)
        else:
            self._lbl_pct.configure(text=f"{int(pct)} %")
            self._barra.establecer_progreso(float(pct) / 100.0)

        items = ind.get("evidencias_items", [])
        for idx, chk in enumerate(self._checks):
            if idx < len(items):
                chk.configure(text=items[idx]["nombre"], state="disabled" if pub == "publicado" else "normal")
                self._vars[idx].set(bool(items[idx].get("marcada")))

        if pub == "publicado":
            self._lbl_ayuda.configure(text="Indicador publicado. Las evidencias quedan bloqueadas para cierre.")
            self._btn_publicar.configure(text="Publicado")
            self._btn_publicar.establecer_habilitado(False)
            self._tooltip_pub.actualizar_texto("Este indicador ya fue publicado en el ciclo actual.")
        elif ind.get("porcentaje_logrado") is None:
            self._lbl_ayuda.configure(text="Marca al menos 1 evidencia para calcular el logro y habilitar publicación.")
            self._btn_publicar.configure(text="Publicar indicador")
            self._btn_publicar.establecer_habilitado(False)
            self._tooltip_pub.actualizar_texto("Selecciona al menos una evidencia antes de publicar.")
        else:
            self._lbl_ayuda.configure(text="Listo para publicar resultado evaluado en el cierre de asignatura.")
            self._btn_publicar.configure(text="Publicar indicador")
            self._btn_publicar.establecer_habilitado(True)
            self._tooltip_pub.actualizar_texto("Publicar resultado del indicador en bitácora.")


class VistaIndicadores(componentes.ScrollableCadence):
    """Vista dedicada para evaluar evidencias y publicar indicadores por asignatura."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._ultimo_indice: Optional[int] = None

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        cab = ctk.CTkFrame(wrap, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        tit = ctk.CTkFrame(cab, fg_color="transparent")
        tit.pack(side="left", fill="x", expand=True)

        self._lbl_titulo = ctk.CTkLabel(
            tit,
            text="Indicadores y Evidencias",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_titulo.pack(fill="x")

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
            texto="Volver al panel principal",
            comando=lambda: self.app.navegar_a("dashboard"),
            variante="secundario",
        ).pack(side="right")

        self._contenedor = ctk.CTkFrame(wrap, fg_color="transparent")
        self._contenedor.pack(fill="x")
        self._pool: List[_TarjetaIndicadorDetalle] = []
        self._vacio = componentes.EstadoVacio(
            self._contenedor,
            titulo="No hay indicadores configurados",
            mensaje="Selecciona otra asignatura en el encabezado para revisar sus indicadores.",
            icono_nombre="indicadores",
        )
        self.actualizar(animar=False)

    def actualizar(self, animar: bool = True) -> None:
        mat = self.app.materia_actual()
        idx_actual = self.app.indice_materia
        cambio = self._ultimo_indice is not None and self._ultimo_indice != idx_actual
        self._ultimo_indice = idx_actual

        self._lbl_sub.configure(
            text=f"{mat.get('nombre', '')}  ·  {mat.get('clave', '')}  ·  Grupo {mat.get('grupo', '')}  ·  Meta: {mat.get('meta_institucional', '')}"
        )

        indicadores = mat.get("indicadores", [])
        if not indicadores:
            for card in self._pool:
                card.pack_forget()
            self._vacio.pack(fill="x", pady=tema.ESPACIO_SM)
            return

        self._vacio.pack_forget()
        while len(self._pool) < len(indicadores):
            self._pool.append(
                _TarjetaIndicadorDetalle(
                    self._contenedor,
                    al_cambiar_evidencia=self._al_actualizar_evidencia,
                    al_publicar=self._confirmar_publicacion,
                )
            )

        for idx, card in enumerate(self._pool):
            if idx < len(indicadores):
                card.actualizar(indicadores[idx])
                if not card.winfo_manager():
                    card.pack(fill="x", pady=(0, tema.ESPACIO_MD))
            else:
                card.pack_forget()

        if animar and cambio:
            animaciones.animar_transicion_cambio_materia(
                self,
                self._pool[: len(indicadores)],
                self.app.gestor_animaciones,
            )

    def _al_actualizar_evidencia(self) -> None:
        self.app.refrescar_vistas(origen="indicadores")

    def _confirmar_publicacion(self, ind: Dict[str, Any]) -> None:
        mat = self.app.materia_actual()
        componentes.ModalConfirmacion(
            self.winfo_toplevel(),
            titulo="Publicar indicador",
            mensaje=(
                f"Se publicará el indicador {ind['clave']} de {mat['nombre']} "
                f"con {ind.get('porcentaje_logrado', 0)}% logrado ({ind.get('valoracion', 'Evaluado')})."
            ),
            texto_confirmar="Publicar indicador",
            variante_confirmar="exito",
            al_confirmar=lambda i=ind, m=mat: self._ejecutar_publicacion(i, m),
        )

    def _ejecutar_publicacion(self, ind: Dict[str, Any], mat: Dict[str, Any]) -> None:
        ind["publicacion"] = "publicado"
        ev = registrar_evento_firma(
            usuario=self.app.datos.get("docente_nombre", "Docente Titular"),
            rol="Docente Titular",
            materia=mat,
            estado_anterior="pendiente",
            estado_nuevo="publicado",
            accion=f"Publicación de indicador {ind['clave']}",
            detalle=(
                f"Evidencias {ind['seleccion']}, logro {ind.get('porcentaje_logrado', 0)}%, "
                f"valoración {ind.get('valoracion', '')}."
            ),
            aprobacion_humana=True,
        )
        self.app.datos["bitacora_firmas"].append(ev)
        self.app.refrescar_vistas()
        self.app.notificar(
            "Indicador publicado",
            f"{ind['clave']} ({ind.get('porcentaje_logrado', 0)}%) registrado.",
            "exito",
        )
