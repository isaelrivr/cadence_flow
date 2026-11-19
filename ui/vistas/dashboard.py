"""Vista principal del panel de gestión académica (Dashboard) de Cadence Flow.

Reutiliza todos sus widgets y el pool de tarjetas al cambiar de asignatura,
mostrando KPIs, tarjeta de impacto energético, Fase 1 · Planeación (con flujo
completo de firma digital y firma_alerta) y Fase 2 · Cierre (indicadores).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import customtkinter as ctk

from fuentes.persistencia import registrar_evento_firma
from ui import animaciones, componentes, iconos, tema


def _estilo_firma(estado: str) -> tuple[str, str]:
    """Mapea el estado de firma a etiqueta legible y variante semántica."""
    mapa = {
        "sin enviar": ("Sin enviar", "info"),
        "enviado": ("Enviado a revisión", "alerta"),
        "con hallazgos": ("Con hallazgos", "error"),
        "firmado": ("Firmado digitalmente", "exito"),
    }
    return mapa.get(estado, (estado.capitalize(), "neutro"))


def _estilo_evidencia(estado: str) -> tuple[str, str]:
    mapa = {
        "pendiente": ("Evidencias: Pendiente", "neutro"),
        "en proceso": ("Evidencias: En proceso", "alerta"),
        "completa": ("Evidencias: Completa", "exito"),
    }
    return mapa.get(estado, (f"Evidencias: {estado}", "info"))


def _estilo_valoracion(valoracion: Optional[str]) -> tuple[str, str]:
    if not valoracion:
        return ("Valoración: Sin evaluar", "neutro")
    bajo = valoracion.lower()
    if "excelente" in bajo or "notable" in bajo:
        return (f"Valoración: {valoracion}", "exito")
    if "suficiente" in bajo:
        return (f"Valoración: {valoracion}", "info")
    return (f"Valoración: {valoracion}", "alerta")


def _estilo_publicacion(estado: str) -> tuple[str, str]:
    if estado == "publicado":
        return ("Publicado", "exito")
    return ("Sin publicar", "neutro")


class _TarjetaIndicadorPool(componentes.TarjetaCadence):
    """Tarjeta reutilizable de indicador para Fase 2 · Cierre sin destruir widgets."""

    def __init__(self, master, al_abrir_indicadores) -> None:
        super().__init__(master)
        self._al_abrir = al_abrir_indicadores

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        # Fila superior: clave + descripción + badges de estado
        fila_sup = ctk.CTkFrame(cont, fg_color="transparent")
        fila_sup.pack(fill="x")

        izq_sup = ctk.CTkFrame(fila_sup, fg_color="transparent")
        izq_sup.pack(side="left", fill="x", expand=True)

        fila_titulo = ctk.CTkFrame(izq_sup, fg_color="transparent")
        fila_titulo.pack(fill="x")

        self._icono = ctk.CTkLabel(
            fila_titulo,
            text="",
            image=iconos.obtener_icono("indicadores", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        )
        self._icono.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_clave = ctk.CTkLabel(
            fila_titulo,
            text="",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_clave.pack(side="left")

        self._lbl_meta = ctk.CTkLabel(
            fila_titulo,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_meta.pack(side="left", padx=(tema.ESPACIO_MD, 0))

        self._lbl_desc = ctk.CTkLabel(
            izq_sup,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_desc.pack(fill="x", pady=(2, 0))

        der_sup = ctk.CTkFrame(fila_sup, fg_color="transparent")
        der_sup.pack(side="right", padx=(tema.ESPACIO_MD, 0))

        self._badge_pub = componentes.BadgeEstado(der_sup, "Sin publicar", "neutro")
        self._badge_pub.pack(side="right", padx=(tema.ESPACIO_SM, 0))

        self._badge_val = componentes.BadgeEstado(der_sup, "Sin evaluar", "neutro", con_nodo=False)
        self._badge_val.pack(side="right", padx=(tema.ESPACIO_SM, 0))

        self._badge_ev = componentes.BadgeEstado(der_sup, "Pendiente", "neutro", con_nodo=False)
        self._badge_ev.pack(side="right")

        # Fila inferior: barra de progreso degradada + selección + botón gestionar
        fila_inf = ctk.CTkFrame(cont, fg_color="transparent")
        fila_inf.pack(fill="x", pady=(tema.ESPACIO_MD, 0))

        self._lbl_seleccion = ctk.CTkLabel(
            fila_inf,
            text="Selección: 0/3",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            width=120,
            anchor="w",
        )
        self._lbl_seleccion.pack(side="left")

        self._barra = componentes.BarraProgresoDegradado(fila_inf, progreso=0.0, ancho_inicial=260)
        self._barra.pack(side="left", fill="x", expand=True, padx=tema.ESPACIO_MD)

        self._lbl_pct = ctk.CTkLabel(
            fila_inf,
            text="-- %",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            width=56,
            anchor="e",
        )
        self._lbl_pct.pack(side="left", padx=(0, tema.ESPACIO_MD))

        self._btn_gestionar = componentes.BotonCadence(
            fila_inf,
            texto="Gestionar evidencias",
            comando=self._al_abrir,
            variante="secundario",
            tam="sm",
        )
        self._btn_gestionar.pack(side="right")

        self._tooltip = componentes.TooltipCadence(self._barra, "")

    def actualizar(self, ind: Dict[str, Any]) -> None:
        """Actualiza los datos del indicador sin reconstruir widgets."""
        self._lbl_clave.configure(text=ind.get("clave", ""))
        self._lbl_meta.configure(text=f"Meta: {ind.get('meta', 'Sin definir')}")
        self._lbl_desc.configure(text=ind.get("descripcion", "Indicador de desempeño académico"))

        txt_ev, var_ev = _estilo_evidencia(ind.get("evidencias", "pendiente"))
        self._badge_ev.actualizar(txt_ev, var_ev)

        txt_val, var_val = _estilo_valoracion(ind.get("valoracion"))
        self._badge_val.actualizar(txt_val, var_val)

        txt_pub, var_pub = _estilo_publicacion(ind.get("publicacion", "pendiente"))
        self._badge_pub.actualizar(txt_pub, var_pub)

        seleccion = ind.get("seleccion", "0/3")
        self._lbl_seleccion.configure(text=f"Selección: {seleccion}")

        pct = ind.get("porcentaje_logrado")
        if pct is None:
            self._lbl_pct.configure(text="-- %")
            self._barra.establecer_progreso(0.0)
        else:
            self._lbl_pct.configure(text=f"{int(pct)} %")
            self._barra.establecer_progreso(float(pct) / 100.0)

        self._tooltip.actualizar_texto(
            f"Indicador {ind.get('clave', '')} · Evidencias {seleccion} · "
            f"Meta institucional: {ind.get('meta', '')}."
        )


class VistaDashboard(componentes.ScrollableCadence):
    """Panel principal con KPIs, Impacto Energético, Planeación y Cierre."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._ultimo_indice_materia: Optional[int] = None

        self._construir_estructura()
        self.actualizar(animar=False)

    def _construir_estructura(self) -> None:
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)
        self._wrap = wrap

        # Encabezado de la vista + botones de acción rápida
        top = ctk.CTkFrame(wrap, fg_color="transparent")
        top.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        titulos = ctk.CTkFrame(top, fg_color="transparent")
        titulos.pack(side="left", fill="x", expand=True)

        self._lbl_materia = ctk.CTkLabel(
            titulos,
            text="",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_materia.pack(fill="x")

        self._lbl_subtitulo = ctk.CTkLabel(
            titulos,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_subtitulo.pack(fill="x", pady=(2, 0))

        acciones_top = ctk.CTkFrame(top, fg_color="transparent")
        acciones_top.pack(side="right")

        componentes.BotonCadence(
            acciones_top,
            texto="Cargar archivo local",
            comando=self.app.cargar_archivo_local,
            variante="secundario",
            icono=iconos.obtener_icono("upload", tema.ICONO_SM, tema.TEXTO_PRIMARIO),
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        componentes.BotonCadence(
            acciones_top,
            texto="Inicio de semestre",
            comando=lambda: self.app.abrir_modal_semestre("inicio"),
            variante="primario",
            icono=iconos.obtener_icono("calendar_start", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        componentes.BotonCadence(
            acciones_top,
            texto="Cierre de semestre",
            comando=lambda: self.app.abrir_modal_semestre("cierre"),
            variante="oscuro",
            icono=iconos.obtener_icono("calendar_end", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        ).pack(side="left")

        # Fila de 4 KPIs (creados una sola vez)
        kpi_grid = ctk.CTkFrame(wrap, fg_color="transparent")
        kpi_grid.pack(fill="x", pady=(0, tema.ESPACIO_MD))
        for col in range(4):
            kpi_grid.grid_columnconfigure(col, weight=1, uniform="kpi")

        self._kpi_clave = componentes.TarjetaKPI(kpi_grid, "Clave y grupo", "", "", "file")
        self._kpi_clave.grid(row=0, column=0, sticky="nsew", padx=(0, tema.ESPACIO_SM))

        self._kpi_indicadores = componentes.TarjetaKPI(kpi_grid, "Indicadores", "", "", "indicadores")
        self._kpi_indicadores.grid(row=0, column=1, sticky="nsew", padx=tema.ESPACIO_SM)

        self._kpi_hallazgos = componentes.TarjetaKPI(kpi_grid, "Hallazgos", "", "", "alert")
        self._kpi_hallazgos.grid(row=0, column=2, sticky="nsew", padx=tema.ESPACIO_SM)

        self._kpi_meta = componentes.TarjetaKPI(kpi_grid, "Meta institucional", "", "", "check")
        self._kpi_meta.grid(row=0, column=3, sticky="nsew", padx=(tema.ESPACIO_SM, 0))

        # Tarjeta de Impacto Energético (simulada)
        self._card_energia = componentes.TarjetaCadence(wrap, con_acento=True)
        self._card_energia.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        eng_body = ctk.CTkFrame(self._card_energia, fg_color="transparent")
        eng_body.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        eng_izq = ctk.CTkFrame(eng_body, fg_color="transparent")
        eng_izq.pack(side="left", fill="x", expand=True)

        eng_tit = ctk.CTkFrame(eng_izq, fg_color="transparent")
        eng_tit.pack(fill="x")

        ctk.CTkLabel(
            eng_tit,
            text="",
            image=iconos.obtener_icono("bolt", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            eng_tit,
            text="Impacto energético de inferencia local",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
        ).pack(side="left")

        self._badge_energia = componentes.BadgeEstado(eng_tit, "Eficiencia óptima", "exito")
        self._badge_energia.pack(side="left", padx=(tema.ESPACIO_MD, 0))

        self._lbl_energia_resumen = ctk.CTkLabel(
            eng_izq,
            text="",
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_energia_resumen.pack(fill="x", pady=(tema.ESPACIO_XS, 0))

        eng_der = ctk.CTkFrame(eng_body, fg_color="transparent", width=260)
        eng_der.pack(side="right", padx=(tema.ESPACIO_LG, 0))

        self._lbl_energia_ahorro = ctk.CTkLabel(
            eng_der,
            text="",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="e",
        )
        self._lbl_energia_ahorro.pack(fill="x", pady=(0, tema.ESPACIO_XS))

        self._barra_energia = componentes.BarraProgresoDegradado(eng_der, progreso=0.68, ancho_inicial=240)
        self._barra_energia.pack(fill="x")

        componentes.TooltipCadence(
            self._card_energia,
            "Estimación simulada basada en ejecuciones locales frente a centros de datos en la nube.",
        )

        componentes.SeparadorCircuito(wrap).pack(fill="x", pady=(tema.ESPACIO_XS, tema.ESPACIO_MD))

        # SECCIÓN: FASE 1 · PLANEACIÓN
        ctk.CTkLabel(
            wrap,
            text="Fase 1 · Planeación e Instrumentación",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", pady=(0, tema.ESPACIO_SM))

        self._card_plan = componentes.TarjetaCadence(wrap)
        self._card_plan.pack(fill="x", pady=(0, tema.ESPACIO_LG))

        plan_cont = ctk.CTkFrame(self._card_plan, fg_color="transparent")
        plan_cont.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_LG)

        plan_top = ctk.CTkFrame(plan_cont, fg_color="transparent")
        plan_top.pack(fill="x")

        plan_doc_box = ctk.CTkFrame(plan_top, fg_color="transparent")
        plan_doc_box.pack(side="left", fill="x", expand=True)

        fila_doc = ctk.CTkFrame(plan_doc_box, fg_color="transparent")
        fila_doc.pack(fill="x")

        ctk.CTkLabel(
            fila_doc,
            text="",
            image=iconos.obtener_icono("file", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_plan_doc = ctk.CTkLabel(
            fila_doc,
            text="",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_plan_doc.pack(side="left")

        self._lbl_plan_meta = ctk.CTkLabel(
            plan_doc_box,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_plan_meta.pack(fill="x", pady=(tema.ESPACIO_XS, 0))

        self._badge_firma = componentes.BadgeEstado(plan_top, "Sin enviar", "info")
        self._badge_firma.pack(side="right")

        # Banner de alerta (firma_alerta) — se muestra/oculta dinámicamente sin destruir
        self._banner_alerta = ctk.CTkFrame(
            plan_cont,
            corner_radius=tema.RADIO_BOTON,
            border_width=tema.BORDE_NORMAL,
        )
        alerta_inner = ctk.CTkFrame(self._banner_alerta, fg_color="transparent")
        alerta_inner.pack(fill="x", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        self._lbl_alerta_icono = ctk.CTkLabel(alerta_inner, text="", width=tema.ICONO_SM)
        self._lbl_alerta_icono.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_alerta_texto = ctk.CTkLabel(
            alerta_inner,
            text="",
            font=tema.fuente("cuerpo"),
            anchor="w",
            justify="left",
            wraplength=760,
        )
        self._lbl_alerta_texto.pack(side="left", fill="x", expand=True)

        # Botones de flujo de firma
        self._plan_botones = ctk.CTkFrame(plan_cont, fg_color="transparent")
        self._plan_botones.pack(fill="x", pady=(tema.ESPACIO_MD, 0))

        self._btn_firma_1 = componentes.BotonCadence(
            self._plan_botones,
            texto="",
            variante="primario",
            icono=iconos.obtener_icono("check", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        )
        self._btn_firma_1.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._btn_firma_2 = componentes.BotonCadence(
            self._plan_botones,
            texto="",
            variante="secundario",
        )
        self._btn_firma_2.pack(side="left")

        componentes.SeparadorCircuito(wrap).pack(fill="x", pady=(tema.ESPACIO_XS, tema.ESPACIO_MD))

        # SECCIÓN: FASE 2 · CIERRE (INDICADORES)
        header_cierre = ctk.CTkFrame(wrap, fg_color="transparent")
        header_cierre.pack(fill="x", pady=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            header_cierre,
            text="Fase 2 · Cierre y Seguimiento de Indicadores",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(side="left")

        componentes.BotonCadence(
            header_cierre,
            texto="Ver vista detallada de indicadores",
            comando=lambda: self.app.navegar_a("indicadores"),
            variante="fantasma",
            tam="sm",
        ).pack(side="right")

        self._contenedor_indicadores = ctk.CTkFrame(wrap, fg_color="transparent")
        self._contenedor_indicadores.pack(fill="x")

        self._pool_indicadores: List[_TarjetaIndicadorPool] = []
        self._estado_vacio_ind = componentes.EstadoVacio(
            self._contenedor_indicadores,
            titulo="Sin indicadores registrados",
            mensaje="Esta asignatura aún no tiene indicadores asociados para el periodo actual.",
            icono_nombre="indicadores",
        )

    def actualizar(self, animar: bool = True) -> None:
        """Actualiza todos los widgets existentes con la asignatura activa."""
        mat = self.app.materia_actual()
        idx_actual = self.app.indice_materia
        cambio_materia = self._ultimo_indice_materia is not None and self._ultimo_indice_materia != idx_actual
        self._ultimo_indice_materia = idx_actual

        self._lbl_materia.configure(text=mat.get("nombre", ""))
        self._lbl_subtitulo.configure(
            text=(
                f"Periodo {self.app.datos.get('periodo', '')}  ·  "
                f"Clave {mat.get('clave', '')}  ·  Grupo {mat.get('grupo', '')}"
            )
        )

        # KPIs
        indicadores = mat.get("indicadores", [])
        completos = sum(1 for i in indicadores if i.get("evidencias") == "completa")
        publicados = sum(1 for i in indicadores if i.get("publicacion") == "publicado")
        plan = mat.get("planeacion", {})
        hallazgos = int(plan.get("hallazgos_verificador", 0))

        self._kpi_clave.actualizar(
            f"{mat.get('clave', '')} · {mat.get('grupo', '')}",
            f"Docente {self.app.datos.get('docente_iniciales', '')}",
        )
        self._kpi_indicadores.actualizar(
            f"{len(indicadores)} indicadores",
            f"{completos} completos · {publicados} publicados",
        )
        self._kpi_hallazgos.actualizar(
            f"{hallazgos} {'abierto' if hallazgos == 1 else 'abiertos'}",
            "Revisión sin observaciones" if hallazgos == 0 else "Requiere atención antes de firmar",
            color_valor=tema.SEMANTICO["error"]["fg"] if hallazgos > 0 else tema.SEMANTICO["exito"]["fg"],
        )
        self._kpi_meta.actualizar(
            mat.get("meta_institucional", "Sin definir"),
            "Objetivo institucional del grupo",
        )

        self.actualizar_energia()

        # Fase 1 · Planeación
        self._lbl_plan_doc.configure(text=plan.get("documento", ""))
        firmado_por = plan.get("firmado_por")
        act = plan.get("ultima_actualizacion", "Sin actividad")
        meta_txt = f"Último movimiento: {act}"
        if firmado_por and plan.get("firma") == "firmado":
            meta_txt += f"  ·  Autorizó: {firmado_por}"
        self._lbl_plan_meta.configure(text=meta_txt)

        estado_firma = plan.get("firma", "sin enviar")
        txt_f, var_f = _estilo_firma(estado_firma)
        self._badge_firma.actualizar(txt_f, var_f)

        alerta = plan.get("firma_alerta")
        if alerta:
            tipo_alerta = "error" if estado_firma == "con hallazgos" else "alerta"
            estilos_alerta = tema.SEMANTICO[tipo_alerta]
            self._banner_alerta.configure(
                fg_color=estilos_alerta["bg"],
                border_color=estilos_alerta["borde"],
            )
            self._lbl_alerta_icono.configure(
                image=iconos.obtener_icono("alert", tema.ICONO_SM, estilos_alerta["fg"])
            )
            self._lbl_alerta_texto.configure(text=alerta, text_color=estilos_alerta["fg"])
            if not self._banner_alerta.winfo_manager():
                self._banner_alerta.pack(fill="x", pady=(tema.ESPACIO_MD, 0), before=self._plan_botones)
        else:
            if self._banner_alerta.winfo_manager():
                self._banner_alerta.pack_forget()

        self._configurar_botones_firma(mat, estado_firma)

        # Fase 2 · Cierre (Pool de indicadores)
        if not indicadores:
            for tarjeta in self._pool_indicadores:
                tarjeta.pack_forget()
            self._estado_vacio_ind.pack(fill="x", pady=tema.ESPACIO_SM)
        else:
            self._estado_vacio_ind.pack_forget()
            while len(self._pool_indicadores) < len(indicadores):
                nueva = _TarjetaIndicadorPool(
                    self._contenedor_indicadores,
                    al_abrir_indicadores=lambda: self.app.navegar_a("indicadores"),
                )
                self._pool_indicadores.append(nueva)

            for idx, tarjeta in enumerate(self._pool_indicadores):
                if idx < len(indicadores):
                    tarjeta.actualizar(indicadores[idx])
                    if not tarjeta.winfo_manager():
                        tarjeta.pack(fill="x", pady=(0, tema.ESPACIO_SM))
                else:
                    tarjeta.pack_forget()

        if animar and cambio_materia:
            objetivos = [
                self._kpi_clave,
                self._kpi_indicadores,
                self._kpi_hallazgos,
                self._kpi_meta,
                self._card_plan,
            ] + self._pool_indicadores[: len(indicadores)]
            animaciones.animar_transicion_cambio_materia(
                self,
                objetivos,
                self.app.gestor_animaciones,
            )

    def actualizar_energia(self) -> None:
        """Refresca la tarjeta de impacto energético desde el estado compartido."""
        eng = self.app.datos.get("impacto_energetico", {})
        kwh = eng.get("kwh_periodo", 1.42)
        co2 = eng.get("co2_kg", 0.61)
        ahorro = eng.get("ahorro_vs_nube_pct", 68)
        ejecs = eng.get("ejecuciones_locales", 34)
        efic = eng.get("eficiencia", "Óptima")

        self._badge_energia.actualizar(f"Eficiencia: {efic}", "exito")
        self._lbl_energia_resumen.configure(
            text=(
                f"Consumo estimado del periodo: {kwh:.2f} kWh  ·  "
                f"Huella: {co2:.2f} kg CO₂e  ·  {ejecs} ejecuciones locales"
            )
        )
        self._lbl_energia_ahorro.configure(text=f"-{ahorro}% vs inferencia en nube")
        self._barra_energia.establecer_progreso(min(1.0, max(0.1, float(ahorro) / 100.0)))

    def _configurar_botones_firma(self, mat: Dict[str, Any], estado: str) -> None:
        """Adapta botones del flujo de firma manteniendo los mismos widgets."""
        if estado == "sin enviar":
            self._btn_firma_1.configure(text="Enviar a revisión")
            self._btn_firma_1.establecer_variante("primario")
            self._btn_firma_1.actualizar_comando(lambda m=mat: self._enviar_a_revision(m))
            self._btn_firma_2.configure(text="Aprobar firma")
            self._btn_firma_2.establecer_variante("exito")
            self._btn_firma_2.actualizar_comando(lambda m=mat: self._abrir_modal_aprobacion(m))

        elif estado == "enviado":
            self._btn_firma_1.configure(text="Aprobar firma")
            self._btn_firma_1.establecer_variante("exito")
            self._btn_firma_1.actualizar_comando(lambda m=mat: self._abrir_modal_aprobacion(m))
            self._btn_firma_2.configure(text="Reportar hallazgo")
            self._btn_firma_2.establecer_variante("peligro")
            self._btn_firma_2.actualizar_comando(lambda m=mat: self._abrir_modal_hallazgo(m))

        elif estado == "con hallazgos":
            self._btn_firma_1.configure(text="Subsanar y reenviar")
            self._btn_firma_1.establecer_variante("primario")
            self._btn_firma_1.actualizar_comando(lambda m=mat: self._enviar_a_revision(m, subsanado=True))
            self._btn_firma_2.configure(text="Aprobar firma")
            self._btn_firma_2.establecer_variante("exito")
            self._btn_firma_2.actualizar_comando(lambda m=mat: self._abrir_modal_aprobacion(m))

        else:  # firmado
            self._btn_firma_1.configure(text="Ver comprobante")
            self._btn_firma_1.establecer_variante("secundario")
            self._btn_firma_1.actualizar_comando(lambda m=mat: self._ver_comprobante(m))
            self._btn_firma_2.configure(text="Revocar firma")
            self._btn_firma_2.establecer_variante("fantasma")
            self._btn_firma_2.actualizar_comando(lambda m=mat: self._confirmar_revocacion(m))

    def _enviar_a_revision(self, mat: Dict[str, Any], subsanado: bool = False) -> None:
        plan = mat["planeacion"]
        anterior = plan["firma"]
        plan["firma"] = "enviado"
        plan["hallazgos_verificador"] = 0
        plan["firma_alerta"] = "En espera de aprobación humana para emitir firma digital."
        accion = "Reenvío tras subsanar hallazgos" if subsanado else "Envío de instrumentación a revisión"
        ev = registrar_evento_firma(
            usuario=self.app.datos.get("docente_nombre", "Docente Titular"),
            rol="Docente Titular",
            materia=mat,
            estado_anterior=anterior,
            estado_nuevo="enviado",
            accion=accion,
            detalle="Documento listo para validación y firma digital.",
            aprobacion_humana=False,
        )
        plan["ultima_actualizacion"] = ev["timestamp"]
        self.app.datos["bitacora_firmas"].append(ev)
        self.app.refrescar_vistas()
        self.app.notificar("Enviado a revisión", f"{mat['clave']} quedó en espera de aprobación.", "alerta")

    def _abrir_modal_aprobacion(self, mat: Dict[str, Any]) -> None:
        doc = mat["planeacion"]["documento"]
        componentes.ModalConfirmacion(
            self.winfo_toplevel(),
            titulo="Aprobar firma digital",
            mensaje=(
                f"Se emitirá la firma digital para '{doc}' ({mat['nombre']} · Grupo {mat['grupo']}) "
                "y quedará registrada en salidas/bitacora-firmas.jsonl."
            ),
            texto_confirmar="Aprobar firma",
            variante_confirmar="exito",
            requerir_check=True,
            texto_check="Confirmo haber revisado el documento y autorizo la firma humana explícita.",
            al_confirmar=lambda m=mat: self._ejecutar_aprobacion(m),
        )

    def _ejecutar_aprobacion(self, mat: Dict[str, Any]) -> None:
        self.app.iniciar_procesamiento()
        try:
            plan = mat["planeacion"]
            anterior = plan["firma"]
            docente = self.app.datos.get("docente_nombre", "M.C. Lamia Hamdan Medina")
            plan["firma"] = "firmado"
            plan["hallazgos_verificador"] = 0
            plan["firma_alerta"] = None
            plan["firmado_por"] = docente
            ev = registrar_evento_firma(
                usuario=docente,
                rol="Docente Titular",
                materia=mat,
                estado_anterior=anterior,
                estado_nuevo="firmado",
                accion="Aprobación explícita de firma digital",
                detalle=f"Firma aprobada por {docente} para {plan['documento']}.",
                aprobacion_humana=True,
            )
            plan["ultima_actualizacion"] = ev["timestamp"]
            self.app.datos["bitacora_firmas"].append(ev)
            self.app.refrescar_vistas()
            self.app.notificar(
                "Firma aprobada y registrada",
                f"{plan['documento']} firmado y guardado en bitácora.",
                "exito",
            )
        finally:
            self.after(600, self.app.detener_procesamiento)

    def _abrir_modal_hallazgo(self, mat: Dict[str, Any]) -> None:
        componentes.ModalHallazgo(
            self.winfo_toplevel(),
            nombre_materia=f"{mat['nombre']} ({mat['clave']})",
            al_guardar=lambda detalle, m=mat: self._registrar_hallazgo(m, detalle),
        )

    def _registrar_hallazgo(self, mat: Dict[str, Any], detalle: str) -> None:
        plan = mat["planeacion"]
        anterior = plan["firma"]
        plan["firma"] = "con hallazgos"
        plan["hallazgos_verificador"] = int(plan.get("hallazgos_verificador", 0)) + 1
        plan["firma_alerta"] = detalle
        ev = registrar_evento_firma(
            usuario="Ing. Valeria Mendoza Cruz",
            rol="Verificador de Calidad",
            materia=mat,
            estado_anterior=anterior,
            estado_nuevo="con hallazgos",
            accion="Registro de hallazgo en instrumentación",
            detalle=detalle,
            aprobacion_humana=False,
        )
        plan["ultima_actualizacion"] = ev["timestamp"]
        self.app.datos["bitacora_firmas"].append(ev)
        self.app.refrescar_vistas()
        self.app.notificar("Hallazgo registrado", f"{mat['clave']} requiere corrección.", "error")

    def _ver_comprobante(self, mat: Dict[str, Any]) -> None:
        plan = mat["planeacion"]
        componentes.ModalConfirmacion(
            self.winfo_toplevel(),
            titulo="Comprobante de firma digital",
            mensaje=(
                f"Documento: {plan.get('documento', '')}\n"
                f"Asignatura: {mat.get('nombre', '')} ({mat.get('clave', '')} · {mat.get('grupo', '')})\n"
                f"Firmado por: {plan.get('firmado_por') or self.app.datos.get('docente_nombre')}\n"
                f"Fecha de registro: {plan.get('ultima_actualizacion', 'Validado')}\n"
                "Respaldo en bitácora: salidas/bitacora-firmas.jsonl"
            ),
            texto_confirmar="Ir a bitácora",
            variante_confirmar="primario",
            al_confirmar=lambda: self.app.navegar_a("bitacora"),
        )

    def _confirmar_revocacion(self, mat: Dict[str, Any]) -> None:
        componentes.ModalConfirmacion(
            self.winfo_toplevel(),
            titulo="Revocar firma digital",
            mensaje=(
                f"¿Deseas regresar '{mat['planeacion']['documento']}' al estado 'Sin enviar' "
                "para realizar una nueva edición?"
            ),
            texto_confirmar="Revocar firma",
            variante_confirmar="peligro",
            al_confirmar=lambda m=mat: self._ejecutar_revocacion(m),
        )

    def _ejecutar_revocacion(self, mat: Dict[str, Any]) -> None:
        plan = mat["planeacion"]
        anterior = plan["firma"]
        plan["firma"] = "sin enviar"
        plan["firmado_por"] = None
        plan["firma_alerta"] = None
        ev = registrar_evento_firma(
            usuario=self.app.datos.get("docente_nombre", "Docente Titular"),
            rol="Docente Titular",
            materia=mat,
            estado_anterior=anterior,
            estado_nuevo="sin enviar",
            accion="Revocación de firma para edición",
            detalle="Documento devuelto a estado borrador.",
            aprobacion_humana=True,
        )
        plan["ultima_actualizacion"] = ev["timestamp"]
        self.app.datos["bitacora_firmas"].append(ev)
        self.app.refrescar_vistas()
        self.app.notificar("Firma revocada", f"{mat['clave']} volvió a estado Sin enviar.", "info")
