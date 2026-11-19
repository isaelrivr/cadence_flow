"""Modal funcional (simulado) para Inicio y Cierre de Semestre con checklist."""

from __future__ import annotations

from typing import Any, Dict, List

import customtkinter as ctk

from fuentes.persistencia import registrar_evento_firma
from ui import componentes, iconos, tema


class ModalSemestre(ctk.CTkToplevel):
    """Flujo interactivo con checklist y simulación no bloqueante de ciclo escolar."""

    def __init__(self, master, app, modo: str = "inicio") -> None:
        super().__init__(master, fg_color=tema.FONDO_APP)
        self.app = app
        self.modo = modo
        self._ejecutando = False

        es_cierre = modo == "cierre"
        periodo = self.app.datos.get("periodo", "2026AD")
        titulo = f"Cierre de Semestre ({periodo})" if es_cierre else f"Inicio de Semestre ({periodo})"
        self.title(titulo)
        self.resizable(False, False)
        self.transient(master)

        if tema.ICONO_ICO_PATH.exists():
            try:
                self.iconbitmap(str(tema.ICONO_ICO_PATH))
            except Exception:
                pass

        self._pasos: List[Dict[str, Any]] = self.app.datos.get(
            "semestre_cierre" if es_cierre else "semestre_inicio",
            [],
        )
        # Sincronizar pasos automáticos en cierre con el estado real del dashboard
        if es_cierre and len(self._pasos) >= 3:
            asig = self.app.datos.get("asignaturas", [])
            self._pasos[0]["completado"] = all(m["planeacion"]["firma"] == "firmado" for m in asig)
            self._pasos[1]["completado"] = all(
                ind["evidencias"] == "completa" for m in asig for ind in m["indicadores"]
            )
            self._pasos[2]["completado"] = all(
                ind["publicacion"] == "publicado" for m in asig for ind in m["indicadores"]
            )

        tarjeta = componentes.TarjetaCadence(self, con_acento=True)
        tarjeta.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_LG)

        cont = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        # Cabecera del modal
        cab = ctk.CTkFrame(cont, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            cab,
            text="",
            image=iconos.obtener_icono(
                "calendar_end" if es_cierre else "calendar_start",
                tema.ICONO_LG,
                tema.MARCA_AZUL_PETROLEO,
            ),
            width=tema.ICONO_LG,
        ).pack(side="left", padx=(0, tema.ESPACIO_SM))

        ctk.CTkLabel(
            cab,
            text=titulo,
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        self._badge_estado = componentes.BadgeEstado(cab, "Preparación", "info")
        self._badge_estado.pack(side="right")

        ctk.CTkLabel(
            cont,
            text=(
                "Verifica los requisitos de cierre antes de generar el paquete del ciclo."
                if es_cierre
                else "Prepara asignaturas, plantillas y bitácoras para el arranque del periodo."
            ),
            font=tema.fuente("cuerpo"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
            wraplength=540,
            justify="left",
        ).pack(fill="x", pady=(0, tema.ESPACIO_MD))

        # Progreso
        self._lbl_progreso = ctk.CTkLabel(
            cont,
            text="",
            font=tema.fuente("mono_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_progreso.pack(fill="x", pady=(0, tema.ESPACIO_XS))

        self._barra = componentes.BarraProgresoDegradado(cont, progreso=0.0, ancho_inicial=520)
        self._barra.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        # Checklist
        caja = ctk.CTkFrame(
            cont,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
        )
        caja.pack(fill="both", expand=True, pady=(0, tema.ESPACIO_MD))

        lista = ctk.CTkFrame(caja, fg_color="transparent")
        lista.pack(fill="both", expand=True, padx=tema.ESPACIO_MD, pady=tema.ESPACIO_MD)

        self._vars: List[ctk.BooleanVar] = []
        for idx, paso in enumerate(self._pasos):
            var = ctk.BooleanVar(value=bool(paso.get("completado")))
            self._vars.append(var)

            fila = ctk.CTkFrame(lista, fg_color="transparent")
            fila.pack(fill="x", pady=4)

            chk = ctk.CTkCheckBox(
                fila,
                text=paso.get("titulo", ""),
                variable=var,
                command=lambda i=idx: self._toggle_paso(i),
                font=tema.fuente("cuerpo_bold"),
                text_color=tema.TEXTO_PRIMARIO,
                fg_color=tema.BTN_PRIMARIO_BG,
                hover_color=tema.BTN_PRIMARIO_HOVER,
                border_color=tema.BORDE_ACTIVO,
            )
            chk.pack(anchor="w")

            ctk.CTkLabel(
                fila,
                text=paso.get("descripcion", ""),
                font=tema.fuente("etiqueta"),
                text_color=tema.TEXTO_SECUNDARIO,
                anchor="w",
            ).pack(anchor="w", padx=(30, 0))

        acciones = ctk.CTkFrame(cont, fg_color="transparent")
        acciones.pack(fill="x")

        self._btn_ejecutar = componentes.BotonCadence(
            acciones,
            texto="Ejecutar cierre" if es_cierre else "Ejecutar apertura",
            comando=self._ejecutar_protocolo,
            variante="oscuro" if es_cierre else "primario",
            icono=iconos.obtener_icono("play", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
        )
        self._btn_ejecutar.pack(side="right", padx=(tema.ESPACIO_SM, 0))

        componentes.BotonCadence(
            acciones,
            texto="Cerrar",
            comando=self._cerrar_seguro,
            variante="secundario",
        ).pack(side="right")

        self._actualizar_progreso()
        self.bind("<Escape>", lambda _e: self._cerrar_seguro())
        componentes.centrar_ventana(self, 620, 490, padre=master)
        self.grab_set()
        self.focus_set()

    def _toggle_paso(self, idx: int) -> None:
        if idx < len(self._pasos):
            self._pasos[idx]["completado"] = bool(self._vars[idx].get())
        self._actualizar_progreso()

    def _actualizar_progreso(self) -> None:
        total = max(1, len(self._pasos))
        hechos = sum(1 for p in self._pasos if p.get("completado"))
        pct = hechos / float(total)
        self._barra.establecer_progreso(pct)
        self._lbl_progreso.configure(text=f"Progreso del protocolo: {hechos}/{len(self._pasos)} pasos ({round(pct * 100)}%)")
        if hechos == len(self._pasos):
            self._badge_estado.actualizar("Listo para ejecutar", "exito")
        else:
            self._badge_estado.actualizar("Pendiente", "alerta")

    def _ejecutar_protocolo(self) -> None:
        if self._ejecutando:
            return
        self._ejecutando = True
        self._btn_ejecutar.establecer_habilitado(False)
        self.app.iniciar_procesamiento()
        self._badge_estado.actualizar("Procesando...", "info")

        pendientes = [i for i, p in enumerate(self._pasos) if not p.get("completado")]

        def _avanzar(pos: int = 0) -> None:
            if not self.winfo_exists():
                self.app.detener_procesamiento()
                return
            if pos < len(pendientes):
                idx = pendientes[pos]
                self._pasos[idx]["completado"] = True
                self._vars[idx].set(True)
                self._actualizar_progreso()
                self.after(260, lambda: _avanzar(pos + 1))
                return

            mat_ref = self.app.materia_actual()
            es_cierre = self.modo == "cierre"
            accion = "Ejecución de Cierre de Semestre" if es_cierre else "Ejecución de Inicio de Semestre"
            ev = registrar_evento_firma(
                usuario=self.app.datos.get("docente_nombre", "Docente Titular"),
                rol="Docente Titular",
                materia=mat_ref,
                estado_anterior=mat_ref["planeacion"]["firma"],
                estado_nuevo="completado",
                accion=accion,
                detalle=f"Checklist completado ({len(self._pasos)}/{len(self._pasos)} pasos).",
                aprobacion_humana=True,
            )
            self.app.datos["bitacora_firmas"].append(ev)
            self.app.refrescar_vistas()
            self.app.detener_procesamiento()
            self._ejecutando = False
            self._badge_estado.actualizar("Completado", "exito")
            self._btn_ejecutar.establecer_habilitado(True)
            self.app.notificar(
                "Protocolo completado",
                f"{accion} registrado correctamente en bitácora.",
                "exito",
            )

        self.after(240, lambda: _avanzar(0))

    def _cerrar_seguro(self) -> None:
        if self._ejecutando:
            return
        self.destroy()
