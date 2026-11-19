"""Vista de orquestación de agentes de IA de Cadence Flow (simulada)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import customtkinter as ctk

from ui import componentes, iconos, tema


class _TarjetaAgente(componentes.TarjetaCadence):
    """Tarjeta individual para inspeccionar, pausar/reanudar y ejecutar un agente."""

    def __init__(self, master, al_alternar, al_ejecutar) -> None:
        super().__init__(master, con_acento=True)
        self._al_alternar = al_alternar
        self._al_ejecutar = al_ejecutar
        self._agente: Dict[str, Any] = {}

        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        top = ctk.CTkFrame(cont, fg_color="transparent")
        top.pack(fill="x")

        izq = ctk.CTkFrame(top, fg_color="transparent")
        izq.pack(side="left", fill="x", expand=True)

        fila_tit = ctk.CTkFrame(izq, fg_color="transparent")
        fila_tit.pack(fill="x")

        ctk.CTkLabel(
            fila_tit,
            text="",
            image=iconos.obtener_icono("agentes", tema.ICONO_MD, tema.MARCA_AZUL_PETROLEO),
            width=tema.ICONO_MD,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._lbl_nombre = ctk.CTkLabel(
            fila_tit,
            text="",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_nombre.pack(side="left")

        self._lbl_rol = ctk.CTkLabel(
            izq,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_rol.pack(fill="x", pady=(2, 0))

        self._badge = componentes.BadgeEstado(top, "Activo", "exito")
        self._badge.pack(side="right")

        self._lbl_desc = ctk.CTkLabel(
            cont,
            text="",
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        self._lbl_desc.pack(fill="x", pady=(tema.ESPACIO_SM, tema.ESPACIO_MD))

        metricas = ctk.CTkFrame(
            cont,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
        )
        metricas.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        m_in = ctk.CTkFrame(metricas, fg_color="transparent")
        m_in.pack(fill="x", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        self._lbl_metricas = ctk.CTkLabel(
            m_in,
            text="",
            font=tema.fuente("mono"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_metricas.pack(fill="x")

        acciones = ctk.CTkFrame(cont, fg_color="transparent")
        acciones.pack(fill="x")

        self._btn_toggle = componentes.BotonCadence(
            acciones,
            texto="Pausar",
            comando=lambda: self._al_alternar(self._agente),
            variante="secundario",
            tam="sm",
        )
        self._btn_toggle.pack(side="left", padx=(0, tema.ESPACIO_SM))

        self._btn_run = componentes.BotonCadence(
            acciones,
            texto="Ejecutar ciclo",
            comando=lambda: self._al_ejecutar(self._agente),
            variante="primario",
            tam="sm",
            icono=iconos.obtener_icono("play", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        )
        self._btn_run.pack(side="left")

    def actualizar(self, agente: Dict[str, Any]) -> None:
        self._agente = agente
        self._lbl_nombre.configure(text=agente.get("nombre", ""))
        self._lbl_rol.configure(text=agente.get("rol", ""))
        self._lbl_desc.configure(text=agente.get("descripcion", ""))

        estado = agente.get("estado", "activo")
        if estado == "ejecutando":
            self._badge.actualizar("Ejecutando...", "info")
            self._btn_toggle.establecer_habilitado(False)
            self._btn_run.establecer_habilitado(False)
        elif estado == "activo":
            self._badge.actualizar("Activo", "exito")
            self._btn_toggle.configure(
                text="Pausar",
                image=iconos.obtener_icono("pause", tema.ICONO_SM, tema.TEXTO_PRIMARIO),
            )
            self._btn_toggle.establecer_habilitado(True)
            self._btn_run.establecer_habilitado(True)
        else:
            self._badge.actualizar("Pausado", "neutro")
            self._btn_toggle.configure(
                text="Reanudar",
                image=iconos.obtener_icono("play", tema.ICONO_SM, tema.TEXTO_PRIMARIO),
            )
            self._btn_toggle.establecer_habilitado(True)
            self._btn_run.establecer_habilitado(False)

        self._lbl_metricas.configure(
            text=(
                f"Última ejecución: {agente.get('ultima_ejecucion', '')}  ·  "
                f"Tareas hoy: {agente.get('tareas_hoy', 0)}  ·  "
                f"Consumo: {agente.get('consumo_wh', 0.0):.1f} Wh"
            )
        )


class VistaAgentes(componentes.ScrollableCadence):
    """Panel de orquestación de agentes internos de Cadence Flow."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        cab = ctk.CTkFrame(wrap, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        ctk.CTkLabel(
            cab,
            text="Orquestador de Agentes IA",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            cab,
            text="Control simulado de agentes encargados de firma digital, validación académica y sincronía.",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # KPIs del orquestador
        kpi_row = ctk.CTkFrame(wrap, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, tema.ESPACIO_MD))
        for col in range(3):
            kpi_row.grid_columnconfigure(col, weight=1, uniform="ag_kpi")

        self._kpi_activos = componentes.TarjetaKPI(kpi_row, "Agentes activos", "", "", "agentes")
        self._kpi_activos.grid(row=0, column=0, sticky="nsew", padx=(0, tema.ESPACIO_SM))

        self._kpi_tareas = componentes.TarjetaKPI(kpi_row, "Tareas procesadas hoy", "", "", "check")
        self._kpi_tareas.grid(row=0, column=1, sticky="nsew", padx=tema.ESPACIO_SM)

        self._kpi_consumo = componentes.TarjetaKPI(kpi_row, "Consumo de agentes", "", "", "bolt")
        self._kpi_consumo.grid(row=0, column=2, sticky="nsew", padx=(tema.ESPACIO_SM, 0))

        self._grid = ctk.CTkFrame(wrap, fg_color="transparent")
        self._grid.pack(fill="both", expand=True)
        self._grid.grid_columnconfigure(0, weight=1, uniform="ag_col")
        self._grid.grid_columnconfigure(1, weight=1, uniform="ag_col")

        self._tarjetas: List[_TarjetaAgente] = []
        self.actualizar()

    def actualizar(self) -> None:
        agentes = self.app.datos.get("agentes", [])
        activos = sum(1 for a in agentes if a.get("estado") in {"activo", "ejecutando"})
        tareas = sum(int(a.get("tareas_hoy", 0)) for a in agentes)
        wh = sum(float(a.get("consumo_wh", 0.0)) for a in agentes)

        self._kpi_activos.actualizar(f"{activos} / {len(agentes)}", "En sincronía operativa")
        self._kpi_tareas.actualizar(f"{tareas} ciclos", "Ejecuciones acumuladas del día")
        self._kpi_consumo.actualizar(f"{wh:.1f} Wh", "Inferencia local de bajo impacto")

        while len(self._tarjetas) < len(agentes):
            card = _TarjetaAgente(self._grid, self._alternar_agente, self._ejecutar_agente)
            self._tarjetas.append(card)

        for idx, card in enumerate(self._tarjetas):
            if idx < len(agentes):
                card.actualizar(agentes[idx])
                fila = idx // 2
                col = idx % 2
                padx = (0, tema.ESPACIO_SM) if col == 0 else (tema.ESPACIO_SM, 0)
                card.grid(row=fila, column=col, sticky="nsew", padx=padx, pady=(0, tema.ESPACIO_MD))
            else:
                card.grid_forget()

    def _alternar_agente(self, agente: Dict[str, Any]) -> None:
        nuevo = "pausado" if agente.get("estado") == "activo" else "activo"
        agente["estado"] = nuevo
        self.actualizar()
        verbo = "activado" if nuevo == "activo" else "pausado"
        self.app.notificar(f"Agente {verbo}", agente.get("nombre", ""), "info" if nuevo == "pausado" else "exito")

    def _ejecutar_agente(self, agente: Dict[str, Any]) -> None:
        if agente.get("estado") != "activo":
            return
        agente["estado"] = "ejecutando"
        self.app.iniciar_procesamiento()
        self.actualizar()

        def _finalizar() -> None:
            try:
                if not self.winfo_exists():
                    return
                agente["estado"] = "activo"
                agente["tareas_hoy"] = int(agente.get("tareas_hoy", 0)) + 1
                agente["consumo_wh"] = round(float(agente.get("consumo_wh", 0.0)) + 0.2, 2)
                agente["ultima_ejecucion"] = datetime.now().strftime("%H:%M:%S")

                eng = self.app.datos.get("impacto_energetico", {})
                eng["ejecuciones_locales"] = int(eng.get("ejecuciones_locales", 34)) + 1
                eng["kwh_periodo"] = round(float(eng.get("kwh_periodo", 1.42)) + 0.01, 2)

                self.actualizar()
                self.app.refrescar_vistas(origen="agentes")
                self.app.notificar("Ciclo completado", f"{agente.get('nombre', '')} finalizó sin incidencias.", "exito")
            finally:
                self.app.detener_procesamiento()

        self.after(1200, _finalizar)
