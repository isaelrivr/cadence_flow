"""Ventana principal (Shell) de Cadence Flow."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Dict, Optional

import customtkinter as ctk

from fuentes.dashboard_datos import obtener_estado_dashboard
from fuentes.persistencia import (
    copiar_archivo_a_salidas,
    leer_jsonl,
    BITACORA_FIRMAS,
    BITACORA_SUBIDAS,
    verificar_entorno_async,
)
from ui import animaciones, componentes, iconos, splash, tema
from ui.vistas.agentes import VistaAgentes
from ui.vistas.bitacora import VistaBitacora
from ui.vistas.dashboard import VistaDashboard
from ui.vistas.historico import VistaHistorico
from ui.vistas.indicadores import VistaIndicadores
from ui.vistas.semestre import ModalSemestre
from ui.vistas.usuarios import VistaUsuarios


class CadenceFlowApp(ctk.CTk):
    """Contenedor principal que coordina navegación, estado y ciclo de vida."""

    _ELEMENTOS_NAV = [
        ("dashboard", "Panel principal", "dashboard"),
        ("indicadores", "Indicadores", "indicadores"),
        ("historico", "Drive Histórico", "historico"),
        ("bitacora", "Bitácora", "bitacora"),
        ("agentes", "Agentes IA", "agentes"),
        ("usuarios", "Usuarios y permisos", "usuarios"),
    ]

    def __init__(self, con_splash: bool = True) -> None:
        tema.cargar_fuentes_locales()
        ctk.set_appearance_mode("Light")
        super().__init__(fg_color=tema.FONDO_APP)

        self.title(f"{tema.NOMBRE_PRODUCTO} · Gestión Académica")
        self.minsize(tema.ANCHO_MIN_VENTANA, tema.ALTO_MIN_VENTANA)
        self._configurar_icono_ventana()

        self.gestor_animaciones = animaciones.GestorAnimacionesGlobal()
        self.datos = obtener_estado_dashboard("2026AD")
        self.indice_materia: int = 0
        self._vista_activa: str = "dashboard"
        self._vistas: Dict[str, ctk.CTkBaseClass] = {}
        self._botones_nav: Dict[str, Dict[str, ctk.CTkBaseClass]] = {}
        self._splash: Optional[splash.SplashCadence] = None
        self._icon_photo: Optional[tk.PhotoImage] = None

        self.withdraw()
        componentes.centrar_ventana(
            self,
            tema.ANCHO_DEFECTO_VENTANA,
            tema.ALTO_DEFECTO_VENTANA,
        )

        self._construir_shell()
        self._toast = componentes.ToastManager(self)
        self._vincular_ciclo_vida()
        self.navegar_a("dashboard")
        self.actualizar_entorno_async(silencioso=True)

        if con_splash:
            self._splash = splash.SplashCadence(
                self,
                self.gestor_animaciones,
                al_finalizar=self._mostrar_ventana_principal,
            )
        else:
            self._mostrar_ventana_principal()

    def _configurar_icono_ventana(self) -> None:
        if tema.ICONO_ICO_PATH.exists():
            try:
                self.iconbitmap(str(tema.ICONO_ICO_PATH))
            except Exception:
                pass
        if tema.ICONO_PNG_PATH.exists():
            try:
                self._icon_photo = tk.PhotoImage(file=str(tema.ICONO_PNG_PATH))
                self.iconphoto(True, self._icon_photo)
            except Exception:
                pass

    def _mostrar_ventana_principal(self) -> None:
        self._splash = None
        if not self.winfo_exists():
            return
        self.deiconify()
        self.lift()
        self.focus_force()

    def _vincular_ciclo_vida(self) -> None:
        self.bind("<Unmap>", self._al_minimizar, add="+")
        self.bind("<Map>", self._al_restaurar, add="+")
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _al_minimizar(self, event=None) -> None:
        if event is not None and event.widget is not self:
            return
        try:
            if self.state() == "iconic":
                self.gestor_animaciones.establecer_minimizada(True)
        except Exception:
            pass

    def _al_restaurar(self, event=None) -> None:
        if event is not None and event.widget is not self:
            return
        self.gestor_animaciones.establecer_minimizada(False)

    def _al_cerrar(self) -> None:
        if self._splash is not None:
            try:
                self._splash.cerrar()
            except Exception:
                pass
        self.gestor_animaciones.detener_todo()
        self.destroy()

    def _construir_shell(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._construir_header()
        self._construir_sidebar()

        self._area_vistas = ctk.CTkFrame(
            self,
            fg_color=tema.FONDO_APP,
            corner_radius=0,
        )
        self._area_vistas.grid(row=1, column=1, sticky="nsew")
        self._area_vistas.grid_rowconfigure(0, weight=1)
        self._area_vistas.grid_columnconfigure(0, weight=1)

        self._fabricas_vistas = {
            "dashboard": lambda: VistaDashboard(self._area_vistas, self),
            "indicadores": lambda: VistaIndicadores(self._area_vistas, self),
            "historico": lambda: VistaHistorico(self._area_vistas, self),
            "bitacora": lambda: VistaBitacora(self._area_vistas, self),
            "agentes": lambda: VistaAgentes(self._area_vistas, self),
            "usuarios": lambda: VistaUsuarios(self._area_vistas, self),
        }
        self._vistas = {}
        self._obtener_o_crear_vista("dashboard")

    def _obtener_o_crear_vista(self, vista_id: str) -> Optional[ctk.CTkBaseClass]:
        if vista_id in self._vistas:
            return self._vistas[vista_id]
        fabrica = self._fabricas_vistas.get(vista_id)
        if fabrica is None:
            return None
        vista = fabrica()
        vista.grid(row=0, column=0, sticky="nsew")
        self._vistas[vista_id] = vista
        return vista

    def _construir_header(self) -> None:
        header = ctk.CTkFrame(
            self,
            height=tema.ALTO_HEADER,
            corner_radius=0,
            fg_color=tema.FONDO_HEADER,
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)

        margen_c = tema.margen_libre_logo(tema.ALTO_LOGO_HEADER)
        logo_box = ctk.CTkFrame(header, fg_color="transparent")
        logo_box.pack(side="left", padx=(margen_c + tema.ESPACIO_SM, tema.ESPACIO_MD), pady=margen_c)

        lbl_logo = ctk.CTkLabel(
            logo_box,
            text="",
            width=tema.ANCHO_LOGO_HEADER,
            height=tema.ALTO_LOGO_HEADER,
            cursor=tema.CURSOR_MANO,
        )
        lbl_logo.pack()
        lbl_logo.bind("<Button-1>", lambda _e: self.navegar_a("dashboard"))

        self._ctrl_logo_header = animaciones.ControladorLogoAnimado(
            lbl_logo,
            ancho=tema.ANCHO_LOGO_HEADER,
            alto=tema.ALTO_LOGO_HEADER,
            variante="blanco",  # Monocromático blanco obligatorio sobre header oscuro
            siempre_activo=False,
            gestor=self.gestor_animaciones,
        )

        # Título / periodo y selector de asignatura
        marca_info = ctk.CTkFrame(header, fg_color="transparent")
        marca_info.pack(side="left", padx=(0, tema.ESPACIO_LG))

        ctk.CTkLabel(
            marca_info,
            text=f"{tema.NOMBRE_PRODUCTO} · Periodo {self.datos.get('periodo', '')}",
            font=tema.fuente("cuerpo_bold"),
            text_color=tema.TEXTO_SOBRE_OSCURO,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            marca_info,
            text=tema.ESLOGAN,
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_CIAN_SOBRE_OSCURO,
            anchor="w",
        ).pack(anchor="w")

        # Selector global de asignatura
        sel_box = ctk.CTkFrame(header, fg_color="transparent")
        sel_box.pack(side="left", padx=tema.ESPACIO_SM)

        nombres = [
            f"{m['nombre']} ({m['clave']} · {m['grupo']})"
            for m in self.datos.get("asignaturas", [])
        ]
        self._combo_materia = ctk.CTkOptionMenu(
            sel_box,
            values=nombres,
            command=self._al_seleccionar_nombre_materia,
            width=310,
            height=tema.ALTO_BOTON_MD,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.HOVER_HEADER,
            button_color=tema.BTN_PRIMARIO_BG,
            button_hover_color=tema.BTN_PRIMARIO_HOVER,
            text_color=tema.TEXTO_SOBRE_OSCURO,
            font=tema.fuente("cuerpo"),
            dropdown_font=tema.fuente("cuerpo"),
        )
        if nombres:
            self._combo_materia.set(nombres[0])
        self._combo_materia.pack()

        # Controles derechos: entorno asíncrono, tema y reducir movimiento
        der = ctk.CTkFrame(header, fg_color="transparent")
        der.pack(side="right", padx=tema.ESPACIO_LG)

        self._var_reducir_mov = ctk.BooleanVar(value=False)
        self._switch_mov = ctk.CTkSwitch(
            der,
            text="Reducir movimiento",
            variable=self._var_reducir_mov,
            command=self._toggle_reducir_movimiento,
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SOBRE_OSCURO,
            progress_color=tema.MARCA_CIAN,
            button_color=tema.MARCA_BLANCO,
            fg_color=tema.BTN_PRIMARIO_BG,
            switch_width=36,
            switch_height=18,
        )
        self._switch_mov.pack(side="right", padx=(tema.ESPACIO_MD, 0))

        self._btn_tema = componentes.BotonCadence(
            der,
            texto="Oscuro",
            comando=self._alternar_tema,
            variante="oscuro",
            tam="sm",
            icono=iconos.obtener_icono("moon", tema.ICONO_SM, tema.TEXTO_CIAN_SOBRE_OSCURO),
        )
        self._btn_tema.pack(side="right", padx=(tema.ESPACIO_SM, 0))

        self._badge_ia = componentes.BadgeEstado(der, "IA Local", "cian_oscuro")
        self._badge_ia.pack(side="right", padx=(tema.ESPACIO_SM, 0))
        self._tooltip_ia = componentes.TooltipCadence(self._badge_ia, "Haz clic para actualizar estado de IA local")
        self._badge_ia.bind("<Button-1>", lambda _e: self.actualizar_entorno_async(silencioso=False))

        self._badge_drive = componentes.BadgeEstado(der, "Drive", "cian_oscuro")
        self._badge_drive.pack(side="right", padx=(tema.ESPACIO_SM, 0))
        self._tooltip_drive = componentes.TooltipCadence(self._badge_drive, "Haz clic para comprobar credenciales Drive")
        self._badge_drive.bind("<Button-1>", lambda _e: self.actualizar_entorno_async(silencioso=False))

        self._pintar_badges_entorno()

    def _construir_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=tema.ANCHO_SIDEBAR,
            corner_radius=0,
            fg_color=tema.FONDO_SIDEBAR,
            border_width=0,
        )
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        borde_der = ctk.CTkFrame(sidebar, width=1, fg_color=tema.BORDE, corner_radius=0)
        borde_der.pack(side="right", fill="y")

        cuerpo = ctk.CTkFrame(sidebar, fg_color="transparent")
        cuerpo.pack(side="left", fill="both", expand=True, padx=tema.ESPACIO_MD, pady=tema.ESPACIO_LG)

        ctk.CTkLabel(
            cuerpo,
            text="Navegación",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=tema.ESPACIO_SM, pady=(0, tema.ESPACIO_SM))

        for vista_id, etiqueta, icono_nom in self._ELEMENTOS_NAV:
            fila = ctk.CTkFrame(cuerpo, fg_color="transparent", corner_radius=tema.RADIO_BOTON)
            fila.pack(fill="x", pady=2)

            indicador = ctk.CTkFrame(fila, width=4, height=24, corner_radius=2, fg_color="transparent")
            indicador.pack(side="left", padx=(2, 4), pady=6)

            btn = componentes.BotonCadence(
                fila,
                texto=etiqueta,
                comando=lambda vid=vista_id: self.navegar_a(vid),
                variante="fantasma",
                tam="md",
                icono=iconos.obtener_icono(icono_nom, tema.ICONO_MD, tema.TEXTO_PRIMARIO),
                anchor="w",
            )
            btn.configure(border_width=0)
            btn.pack(side="left", fill="x", expand=True)

            self._botones_nav[vista_id] = {"fila": fila, "indicador": indicador, "boton": btn, "icono": icono_nom}

        componentes.SeparadorCircuito(cuerpo).pack(fill="x", pady=tema.ESPACIO_MD)

        ctk.CTkLabel(
            cuerpo,
            text="Acciones del ciclo",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=tema.ESPACIO_SM, pady=(0, tema.ESPACIO_SM))

        componentes.BotonCadence(
            cuerpo,
            texto="Cargar archivo local",
            comando=self.cargar_archivo_local,
            variante="secundario",
            icono=iconos.obtener_icono("upload", tema.ICONO_SM, tema.TEXTO_PRIMARIO),
            anchor="w",
        ).pack(fill="x", pady=3)

        componentes.BotonCadence(
            cuerpo,
            texto="Inicio de semestre",
            comando=lambda: self.abrir_modal_semestre("inicio"),
            variante="primario",
            icono=iconos.obtener_icono("calendar_start", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
            anchor="w",
        ).pack(fill="x", pady=3)

        componentes.BotonCadence(
            cuerpo,
            texto="Cierre de semestre",
            comando=lambda: self.abrir_modal_semestre("cierre"),
            variante="oscuro",
            icono=iconos.obtener_icono("calendar_end", tema.ICONO_SM, tema.TEXTO_SOBRE_OSCURO),
            anchor="w",
        ).pack(fill="x", pady=3)

        # Pie de sidebar con docente y empresa
        pie = ctk.CTkFrame(
            cuerpo,
            corner_radius=tema.RADIO_BOTON,
            fg_color=tema.SUPERFICIE_SUTIL,
        )
        pie.pack(side="bottom", fill="x", pady=(tema.ESPACIO_MD, 0))

        pie_in = ctk.CTkFrame(pie, fg_color="transparent")
        pie_in.pack(fill="x", padx=tema.ESPACIO_MD, pady=tema.ESPACIO_SM)

        ctk.CTkLabel(
            pie_in,
            text=self.datos.get("docente_nombre", "Docente"),
            font=tema.fuente("cuerpo_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            pie_in,
            text=f"Iniciales: {self.datos.get('docente_iniciales', '')}  ·  {tema.NOMBRE_EMPRESA}",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
            wraplength=196,
            justify="left",
        ).pack(fill="x")

    # ------------------------------------------------------------------
    # Navegación y estado compartido
    # ------------------------------------------------------------------
    def materia_actual(self) -> dict:
        asig = self.datos.get("asignaturas", [])
        if not asig:
            return {"nombre": "Sin asignaturas", "clave": "-", "grupo": "-", "planeacion": {}, "indicadores": []}
        idx = max(0, min(self.indice_materia, len(asig) - 1))
        return asig[idx]

    def _al_seleccionar_nombre_materia(self, texto: str) -> None:
        for idx, mat in enumerate(self.datos.get("asignaturas", [])):
            etq = f"{mat['nombre']} ({mat['clave']} · {mat['grupo']})"
            if etq == texto:
                self.seleccionar_materia(idx)
                return

    def seleccionar_materia(self, indice: int) -> None:
        self.indice_materia = indice
        if "dashboard" in self._vistas:
            self._vistas["dashboard"].actualizar(animar=True)  # type: ignore[attr-defined]
        if "indicadores" in self._vistas:
            self._vistas["indicadores"].actualizar(animar=True)  # type: ignore[attr-defined]

    def navegar_a(self, vista_id: str) -> None:
        creando = vista_id not in self._vistas
        vista = self._obtener_o_crear_vista(vista_id)
        if vista is None:
            return
        self._vista_activa = vista_id
        if not creando and hasattr(vista, "actualizar"):
            try:
                if vista_id in {"dashboard", "indicadores"}:
                    vista.actualizar(animar=False)  # type: ignore[attr-defined]
                else:
                    vista.actualizar()  # type: ignore[attr-defined]
            except Exception:
                pass
        vista.tkraise()

        for vid, refs in self._botones_nav.items():
            activo = vid == vista_id
            refs["fila"].configure(fg_color=tema.NAV_ACTIVO_BG if activo else "transparent")
            refs["indicador"].configure(fg_color=tema.NAV_INDICADOR if activo else "transparent")
            refs["boton"].configure(
                font=tema.fuente("cuerpo_bold" if activo else "cuerpo"),
                text_color=tema.TEXTO_PRIMARIO if activo else tema.TEXTO_SECUNDARIO,
                hover_color=tema.NAV_ACTIVO_BG if activo else tema.NAV_HOVER_BG,
            )

    def refrescar_vistas(self, origen: str = "") -> None:
        if origen != "dashboard" and "dashboard" in self._vistas:
            self._vistas["dashboard"].actualizar(animar=False)  # type: ignore[attr-defined]
        if origen != "indicadores" and "indicadores" in self._vistas:
            self._vistas["indicadores"].actualizar(animar=False)  # type: ignore[attr-defined]
        if "historico" in self._vistas:
            self._vistas["historico"].actualizar()  # type: ignore[attr-defined]
        if "bitacora" in self._vistas:
            self._vistas["bitacora"].actualizar()  # type: ignore[attr-defined]

    def recargar_bitacoras_desde_disco(self) -> None:
        self.datos["bitacora_firmas"] = leer_jsonl(BITACORA_FIRMAS)
        self.datos["bitacora_subidas"] = leer_jsonl(BITACORA_SUBIDAS)
        self.refrescar_vistas()

    # ------------------------------------------------------------------
    # Acciones globales (subida, entorno asíncrono, tema, movimiento)
    # ------------------------------------------------------------------
    def cargar_archivo_local(self) -> None:
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo para vincular a Cadence Flow",
            filetypes=[
                ("Documentos académicos", "*.pdf *.docx *.doc *.xlsx *.csv *.txt *.png *.jpg"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return
        self.iniciar_procesamiento()
        try:
            mat = self.materia_actual()
            usuario = self.datos.get("docente_nombre", "Docente Titular")
            registro = copiar_archivo_a_salidas(ruta, mat, usuario)
            self.datos["bitacora_subidas"].append(registro)
            self.refrescar_vistas()
            self.notificar(
                "Archivo vinculado en salidas/",
                f"{Path(ruta).name} copiado y registrado en bitacora-subidas.jsonl.",
                "exito",
            )
        except Exception as exc:
            self.notificar("Error al cargar archivo", str(exc), "error")
        finally:
            self.after(600, self.detener_procesamiento)

    def abrir_modal_semestre(self, modo: str) -> None:
        ModalSemestre(self, self, modo=modo)

    def actualizar_entorno_async(self, silencioso: bool = False) -> None:
        self.iniciar_procesamiento()

        def _aplicar(res: dict) -> None:
            if not self.winfo_exists():
                return
            ent = self.datos.get("entorno", {})
            ent.update(res)
            self._pintar_badges_entorno()
            self.detener_procesamiento()
            if not silencioso:
                self.notificar(
                    "Entorno verificado",
                    f"{res.get('detalle_drive', '')} · {res.get('detalle_ollama', '')}",
                    "info",
                )

        verificar_entorno_async(lambda r: self.after(0, lambda: _aplicar(r)))

    def _pintar_badges_entorno(self) -> None:
        ent = self.datos.get("entorno", {})
        drive_ok = bool(ent.get("drive_autenticado"))
        modelo = ent.get("modelo_activo", "qwen3:8b")
        ollama_vivo = bool(ent.get("ollama_en_linea"))

        self._badge_drive.actualizar(
            "Drive: Conectado" if drive_ok else "Drive: Simulado",
            "exito" if drive_ok else "cian_oscuro",
        )
        self._tooltip_drive.actualizar_texto(ent.get("detalle_drive", "Verificar estado Drive"))

        sufijo_ia = "en línea" if ollama_vivo else "local"
        self._badge_ia.actualizar(f"IA: {modelo} ({sufijo_ia})", "cian_oscuro")
        self._tooltip_ia.actualizar_texto(ent.get("detalle_ollama", "Verificar IA local"))

    def _alternar_tema(self) -> None:
        actual = tema.obtener_modo_actual()
        nuevo = "Dark" if actual == "Light" else "Light"
        tema.cambiar_modo_apariencia(nuevo)
        if nuevo == "Dark":
            self._btn_tema.configure(
                text="Claro",
                image=iconos.obtener_icono("sun", tema.ICONO_SM, tema.TEXTO_CIAN_SOBRE_OSCURO),
            )
        else:
            self._btn_tema.configure(
                text="Oscuro",
                image=iconos.obtener_icono("moon", tema.ICONO_SM, tema.TEXTO_CIAN_SOBRE_OSCURO),
            )

    def _toggle_reducir_movimiento(self) -> None:
        activo = bool(self._var_reducir_mov.get())
        self.gestor_animaciones.establecer_reducir_movimiento(activo)
        self.notificar(
            "Accesibilidad actualizada",
            "Animaciones pausadas." if activo else "Animaciones activadas.",
            "info",
        )

    def iniciar_procesamiento(self) -> None:
        if hasattr(self, "_ctrl_logo_header"):
            self._ctrl_logo_header.iniciar_procesamiento()

    def detener_procesamiento(self) -> None:
        if hasattr(self, "_ctrl_logo_header"):
            self._ctrl_logo_header.detener_procesamiento()

    def notificar(self, titulo: str, mensaje: str = "", tipo: str = "info") -> None:
        if hasattr(self, "_toast"):
            self._toast.mostrar(titulo, mensaje, tipo)
