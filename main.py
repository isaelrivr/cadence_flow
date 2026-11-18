import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from fuentes.dashboard_datos import obtener_estado_dashboard

def crear_boton_moderno(parent, texto, bg_color, fg_color, hover_color, comando, padx=14, pady=7, font_size=10):
    cursor_mano = "pointinghand" if sys.platform == "darwin" else "hand2"
    btn = tk.Label(
        parent, text=texto, bg=bg_color, fg=fg_color,
        font=("SF Pro Display", font_size, "bold"),
        padx=padx, pady=pady, cursor=cursor_mano
    )
    btn.bind("<Button-1>", lambda e: comando())
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
    return btn

def crear_badge(parent, texto, bg_color, fg_color):
    return tk.Label(
        parent, text=texto, bg=bg_color, fg=fg_color,
        font=("SF Pro Text", 9, "bold"), padx=10, pady=3
    )

class CadenceFlowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cadence Flow · Gestión Académica")
        self.geometry("1380x820")
        self.configure(bg="#F1F5F9")

        self.datos = obtener_estado_dashboard("2026AD")
        self.materia_seleccionada = 0
        self.crear_ui()

    def crear_ui(self):
        # 1. BARRA SUPERIOR (Nueva paleta)
        header = tk.Frame(self, bg="#0D3BA7", height=68, padx=28)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand_box = tk.Frame(header, bg="#0D3BA7")
        brand_box.pack(side="left", pady=14)

        tk.Label(
            brand_box, text="◆ CADENCE FLOW", bg="#0D3BA7", fg="#85C8FE",
            font=("SF Pro Display", 15, "bold")
        ).pack(side="left")

        tk.Label(
            brand_box,
            text=f"   |   Periodo {self.datos['periodo']}   ·   M.C. Lamia Hamdan Medina ({self.datos['docente_iniciales']})",
            bg="#0D3BA7", fg="#E0F2FF", font=("SF Pro Text", 11)
        ).pack(side="left")

        env_box = tk.Frame(header, bg="#0D3BA7")
        env_box.pack(side="right", pady=18)

        drive_ok = self.datos["entorno"]["drive_autenticado"]
        drive_txt = "● Drive: Conectado" if drive_ok else "○ Drive: Sin configurar"
        crear_badge(env_box, drive_txt, "#008FFB", "#FFFFFF").pack(side="right", padx=(10, 0))
        crear_badge(env_box, f"⚡ IA Local: {self.datos['entorno']['modelo_activo']}", "#E0F2FF", "#0D3BA7").pack(side="right")

        # 2. BARRA DE CONTROL
        toolbar = tk.Frame(self, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=24, pady=12)
        toolbar.pack(fill="x", padx=20, pady=(16, 12))

        tk.Label(toolbar, text="ASIGNATURA ACTIVA (D2):", bg="#FFFFFF", fg="#475569", font=("SF Pro Text", 9, "bold")).pack(side="left", padx=(0, 10))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        
        nombres_materias = [f"{m['nombre']}  ({m['clave']} · Grupo {m['grupo']})" for m in self.datos["asignaturas"]]
        self.combo_materias = ttk.Combobox(toolbar, values=nombres_materias, state="readonly", width=48, font=("SF Pro Text", 11))
        self.combo_materias.current(0)
        self.combo_materias.bind("<<ComboboxSelected>>", self.cambiar_materia)
        self.combo_materias.pack(side="left")

        # Botones modernos con la nueva paleta
        crear_boton_moderno(toolbar, "Cierre de Semestre (2026AD)", "#0D3BA7", "#FFFFFF", "#008FFB", lambda: None).pack(side="right", padx=(8, 0))
        crear_boton_moderno(toolbar, "Inicio de Semestre", "#008FFB", "#FFFFFF", "#85C8FE", lambda: None).pack(side="right", padx=8)
        crear_boton_moderno(toolbar, "+ Cargar Archivo Local", "#E0F2FF", "#0D3BA7", "#85C8FE", self.cargar_archivo_local).pack(side="right", padx=8)

        # 3. CUERPO DIVIDIDO
        main_body = tk.Frame(self, bg="#F1F5F9")
        main_body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        sidebar = tk.Frame(main_body, bg="#FFFFFF", width=340, highlightbackground="#E2E8F0", highlightthickness=1)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)

        side_head = tk.Frame(sidebar, bg="#E0F2FF", padx=18, pady=14)
        side_head.pack(fill="x")
        tk.Label(side_head, text="📁  Drive Histórico", bg="#E0F2FF", fg="#0D3BA7", font=("SF Pro Display", 11, "bold")).pack(anchor="w")

        tk.Frame(sidebar, bg="#85C8FE", height=1).pack(fill="x")

        self.lista_historicos = tk.Frame(sidebar, bg="#FFFFFF", padx=14, pady=14)
        self.lista_historicos.pack(fill="both", expand=True)
        self.renderizar_historicos()

        workspace = tk.Frame(main_body, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        workspace.pack(side="left", fill="both", expand=True)

        ws_head = tk.Frame(workspace, bg="#FFFFFF", padx=22, pady=14)
        ws_head.pack(fill="x")

        self.lbl_titulo_der = tk.Label(ws_head, text="", bg="#FFFFFF", fg="#0D3BA7", font=("SF Pro Display", 13, "bold"))
        self.lbl_titulo_der.pack(side="left")

        crear_badge(ws_head, "PERIODO ACTIVO · 2026AD", "#E0F2FF", "#0D3BA7").pack(side="right")
        tk.Frame(workspace, bg="#E2E8F0", height=1).pack(fill="x")

        canvas = tk.Canvas(workspace, bg="#F8FAFC", highlightthickness=0)
        scrollbar = ttk.Scrollbar(workspace, orient="vertical", command=canvas.yview)
        self.area_tarjetas = tk.Frame(canvas, bg="#F8FAFC", padx=22, pady=18)

        self.area_tarjetas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.area_tarjetas, anchor="nw", width=940)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.renderizar_panel_derecho()

    def renderizar_historicos(self):
        historicos = [
            ("Instrumentacion_2026.docx", "2026EJ · Firmado", "#E0F2FE", "#008FFB"),
            ("Cedula_2026EJ.pdf", "2026EJ · Publicado", "#E0F2FF", "#0D3BA7")
        ]
        for archivo, detalle, bg_tag, fg_tag in historicos:
            card = tk.Frame(self.lista_historicos, bg="#FFFFFF", highlightbackground="#E0F2FF", highlightthickness=1, padx=12, pady=10)
            card.pack(fill="x", pady=6)
            tk.Label(card, text=f"📄 {archivo}", bg="#FFFFFF", fg="#0D3BA7", font=("SF Pro Text", 10, "bold")).pack(anchor="w")
            tk.Label(card, text=detalle, bg=bg_tag, fg=fg_tag, font=("SF Pro Text", 8, "bold"), padx=6, pady=2).pack(anchor="w", pady=(6, 0))

    def cambiar_materia(self, event=None):
        self.materia_seleccionada = self.combo_materias.current()
        self.renderizar_panel_derecho()

    def renderizar_panel_derecho(self):
        for widget in self.area_tarjetas.winfo_children():
            widget.destroy()

        mat = self.datos["asignaturas"][self.materia_seleccionada]
        self.lbl_titulo_der.config(text=f"{mat['nombre']}  ({mat['clave']} · Grupo {mat['grupo']})")

        # AQUÍ SE IMPLEMENTA EL CAMBIO DINÁMICO DE LA META INSTITUCIONAL
        kpi_row = tk.Frame(self.area_tarjetas, bg="#F8FAFC")
        kpi_row.pack(fill="x", pady=(0, 16))

        kpis = [
            ("CLAVE / GRUPO", f"{mat['clave']} · {mat['grupo']}", "#0D3BA7"),
            ("INDICADORES", f"{len(mat['indicadores'])} filas reales", "#008FFB"),
            ("HALLAZGOS", f"{mat['planeacion']['hallazgos_verificador']} pendientes", "#85C8FE"),
            ("META INSTITUCIONAL", mat.get("meta_institucional", "Sin definir"), "#B45309")  # <-- Lee del JSON directamente
        ]
        for titulo_kpi, valor_kpi, color_kpi in kpis:
            box = tk.Frame(kpi_row, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=14, pady=10)
            box.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(box, text=titulo_kpi, bg="#FFFFFF", fg="#64748B", font=("SF Pro Text", 8, "bold")).pack(anchor="w")
            tk.Label(box, text=valor_kpi, bg="#FFFFFF", fg=color_kpi, font=("SF Pro Display", 12, "bold")).pack(anchor="w", pady=(2, 0))

        # Resto del renderizado con acentos en azul de la paleta
        plan = mat["planeacion"]
        card_plan = tk.Frame(self.area_tarjetas, bg="#FFFFFF", highlightbackground="#85C8FE", highlightthickness=1, padx=18, pady=16)
        card_plan.pack(fill="x", pady=(0, 18))

        top_plan = tk.Frame(card_plan, bg="#FFFFFF")
        top_plan.pack(fill="x")

        tk.Label(top_plan, text="FASE 1 · PLANEACIÓN", bg="#FFFFFF", fg="#0D3BA7", font=("SF Pro Text", 10, "bold")).pack(side="left")
        crear_badge(top_plan, f"FIRMA: {plan['firma'].upper()}", "#E0F2FF", "#008FFB").pack(side="right")
        
        tk.Label(card_plan, text=f"Documento: {plan['documento']}", bg="#FFFFFF", fg="#334155", font=("SF Pro Text", 10)).pack(anchor="w", pady=(8, 14))

        btns_rn01 = tk.Frame(card_plan, bg="#FFFFFF")
        btns_rn01.pack(fill="x")
        crear_boton_moderno(btns_rn01, "✓ Aprobar Firma", "#008FFB", "#FFFFFF", "#0D3BA7", lambda: self.aprobar_firma(mat)).pack(side="left", padx=(0, 10))
        
        tk.Label(self.area_tarjetas, text=f"FASE 2 · CIERRE", bg="#F8FAFC", fg="#0D3BA7", font=("SF Pro Text", 10, "bold")).pack(anchor="w", pady=(2, 8))

        for ind in mat["indicadores"]:
            card_ind = tk.Frame(self.area_tarjetas, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, padx=16, pady=12)
            card_ind.pack(fill="x", pady=5)
            tk.Label(card_ind, text=f"🎯 Indicador: {ind['clave']}", bg="#FFFFFF", fg="#0D3BA7", font=("SF Pro Display", 11, "bold")).pack(side="left")

    def aprobar_firma(self, mat):
        mat["planeacion"]["firma"] = "firmado"
        self.renderizar_panel_derecho()

    def cargar_archivo_local(self):
        ruta = filedialog.askopenfilename()
        if ruta: messagebox.showinfo("Cargado", f"Archivo vinculado.")

if __name__ == "__main__":
    app = CadenceFlowApp()
    app.mainloop()