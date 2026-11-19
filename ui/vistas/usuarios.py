"""Vista de Usuarios y Permisos (RBAC simulado) de Cadence Flow."""

from __future__ import annotations

from typing import Any, Dict, List

import customtkinter as ctk

from ui import componentes, iconos, tema

_CAPACIDADES = [
    ("instrumentaciones", "Instrumentaciones"),
    ("firmar_documentos", "Firmar documentos"),
    ("subir_evidencias", "Subir evidencias"),
    ("gestionar_agentes", "Gestionar agentes"),
    ("gestion_semestre", "Inicio/Cierre semestre"),
    ("auditoria_bitacora", "Auditoría bitácora"),
]


class _TarjetaUsuario(componentes.TarjetaCadence):
    """Tarjeta de usuario con iniciales, rol y estado."""

    def __init__(self, master) -> None:
        super().__init__(master)
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        top = ctk.CTkFrame(cont, fg_color="transparent")
        top.pack(fill="x")

        self._avatar = ctk.CTkLabel(
            top,
            text="",
            width=40,
            height=40,
            corner_radius=tema.RADIO_PILL,
            fg_color=tema.FONDO_HEADER,
            text_color=tema.TEXTO_CIAN_SOBRE_OSCURO,
            font=tema.fuente("cuerpo_bold"),
        )
        self._avatar.pack(side="left", padx=(0, tema.ESPACIO_MD))

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        self._lbl_nombre = ctk.CTkLabel(
            info,
            text="",
            font=tema.fuente("titulo_tarjeta"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        )
        self._lbl_nombre.pack(fill="x")

        self._lbl_correo = ctk.CTkLabel(
            info,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        )
        self._lbl_correo.pack(fill="x")

        self._badge_rol = componentes.BadgeEstado(top, "Docente", "info")
        self._badge_rol.pack(side="right")

        self._lbl_permisos = ctk.CTkLabel(
            cont,
            text="",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
            wraplength=440,
            justify="left",
        )
        self._lbl_permisos.pack(fill="x", pady=(tema.ESPACIO_SM, 0))

    def actualizar(self, usr: Dict[str, Any]) -> None:
        self._avatar.configure(text=usr.get("iniciales", "CF"))
        self._lbl_nombre.configure(text=usr.get("nombre", ""))
        self._lbl_correo.configure(text=usr.get("correo", ""))
        rol = usr.get("rol", "Usuario")
        var = "exito" if "Administrador" in rol or "Coordinador" in rol else "info"
        self._badge_rol.actualizar(rol, var)

        perm = usr.get("permisos", {})
        activos = [etq for clave, etq in _CAPACIDADES if perm.get(clave)]
        self._lbl_permisos.configure(text="Permisos: " + " · ".join(activos))


class VistaUsuarios(componentes.ScrollableCadence):
    """Directorio de usuarios y matriz visual de permisos por rol (simulado)."""

    def __init__(self, master, app) -> None:
        super().__init__(master)
        self.app = app
        self._rol_filtro = "Todos"

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=tema.ESPACIO_XL, pady=tema.ESPACIO_LG)

        cab = ctk.CTkFrame(wrap, fg_color="transparent")
        cab.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        izq = ctk.CTkFrame(cab, fg_color="transparent")
        izq.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            izq,
            text="Usuarios y Permisos",
            font=tema.fuente("titulo_pagina"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            izq,
            text="Control de acceso basado en roles (simulación frontend sin backend de autenticación).",
            font=tema.fuente("etiqueta"),
            text_color=tema.TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        componentes.BadgeEstado(cab, "Sesión activa: HML · Docente Titular", "info").pack(side="right")

        # Filtro de roles
        roles = ["Todos"] + [u.get("rol", "") for u in self.app.datos.get("usuarios", [])]
        self._seg_rol = ctk.CTkSegmentedButton(
            wrap,
            values=roles,
            command=self._filtrar_rol,
            font=tema.fuente("boton_sm"),
            fg_color=tema.SUPERFICIE_SUTIL,
            selected_color=tema.BTN_PRIMARIO_BG,
            selected_hover_color=tema.BTN_PRIMARIO_HOVER,
            unselected_color=tema.SUPERFICIE_SUTIL,
            unselected_hover_color=tema.SUPERFICIE_HOVER,
            text_color=tema.TEXTO_PRIMARIO,
        )
        self._seg_rol.set("Todos")
        self._seg_rol.pack(fill="x", pady=(0, tema.ESPACIO_MD))

        self._grid = ctk.CTkFrame(wrap, fg_color="transparent")
        self._grid.pack(fill="x")
        self._grid.grid_columnconfigure(0, weight=1, uniform="usr_col")
        self._grid.grid_columnconfigure(1, weight=1, uniform="usr_col")
        self._pool: List[_TarjetaUsuario] = []

        componentes.SeparadorCircuito(wrap).pack(fill="x", pady=tema.ESPACIO_MD)

        # Matriz de capacidades por rol
        ctk.CTkLabel(
            wrap,
            text="Matriz de capacidades por rol",
            font=tema.fuente("subtitulo"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", pady=(0, tema.ESPACIO_SM))

        self._matriz = componentes.TarjetaCadence(wrap)
        self._matriz.pack(fill="x")
        self._construir_matriz()
        self.actualizar()

    def _construir_matriz(self) -> None:
        tabla = ctk.CTkFrame(self._matriz, fg_color="transparent")
        tabla.pack(fill="x", padx=tema.ESPACIO_LG, pady=tema.ESPACIO_MD)

        tabla.grid_columnconfigure(0, weight=2)
        for col in range(1, len(_CAPACIDADES) + 1):
            tabla.grid_columnconfigure(col, weight=1)

        # Encabezados
        ctk.CTkLabel(
            tabla,
            text="Rol",
            font=tema.fuente("cuerpo_bold"),
            text_color=tema.TEXTO_PRIMARIO,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, tema.ESPACIO_SM))

        for col, (_, etiqueta) in enumerate(_CAPACIDADES, start=1):
            ctk.CTkLabel(
                tabla,
                text=etiqueta,
                font=tema.fuente("etiqueta"),
                text_color=tema.TEXTO_SECUNDARIO,
                anchor="center",
            ).grid(row=0, column=col, sticky="ew", pady=(0, tema.ESPACIO_SM))

        usuarios = self.app.datos.get("usuarios", [])
        for fila_idx, usr in enumerate(usuarios, start=1):
            ctk.CTkLabel(
                tabla,
                text=usr.get("rol", ""),
                font=tema.fuente("cuerpo_bold"),
                text_color=tema.TEXTO_PRIMARIO,
                anchor="w",
            ).grid(row=fila_idx, column=0, sticky="w", pady=4)

            perm = usr.get("permisos", {})
            for col, (clave, _) in enumerate(_CAPACIDADES, start=1):
                permitido = bool(perm.get(clave))
                icono = iconos.obtener_icono(
                    "check" if permitido else "pause",
                    14,
                    tema.SEMANTICO["exito"]["fg"] if permitido else tema.TEXTO_SECUNDARIO,
                )
                lbl = ctk.CTkLabel(
                    tabla,
                    text="Permitido" if permitido else "Restringido",
                    image=icono,
                    compound="left",
                    font=tema.fuente("etiqueta"),
                    text_color=tema.SEMANTICO["exito"]["fg"] if permitido else tema.TEXTO_SECUNDARIO,
                    padx=4,
                )
                lbl.grid(row=fila_idx, column=col, pady=4)

    def _filtrar_rol(self, valor: str) -> None:
        self._rol_filtro = valor
        self.actualizar()

    def actualizar(self) -> None:
        usuarios = self.app.datos.get("usuarios", [])
        if self._rol_filtro != "Todos":
            filtrados = [u for u in usuarios if u.get("rol") == self._rol_filtro]
        else:
            filtrados = list(usuarios)

        while len(self._pool) < len(filtrados):
            self._pool.append(_TarjetaUsuario(self._grid))

        for idx, card in enumerate(self._pool):
            if idx < len(filtrados):
                card.actualizar(filtrados[idx])
                fila = idx // 2
                col = idx % 2
                padx = (0, tema.ESPACIO_SM) if col == 0 else (tema.ESPACIO_SM, 0)
                card.grid(row=fila, column=col, sticky="nsew", padx=padx, pady=(0, tema.ESPACIO_MD))
            else:
                card.grid_forget()
