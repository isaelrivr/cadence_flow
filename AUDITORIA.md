# Auditoría Técnica y de UX — Cadence Flow (Estado Inicial)

**Fecha:** 2026-11-18  
**Archivos auditados:** `main.py` (199 líneas) y `fuentes/dashboard_datos.py` (101 líneas), junto con la estructura inicial del proyecto (`salidas/`).

---

## 1. Resumen Ejecutivo

La versión inicial de **Cadence Flow** presenta un prototipo funcional básico en Tkinter estándar (`tk`/`ttk`), con interfaz monolítica en `main.py`, datos estáticos en `fuentes/dashboard_datos.py` y ausencia total de identidad de marca corporativa (**Cadence Technologies, S.A. de C.V.**). Existen fallas críticas de funcionalidad, accesibilidad, compatibilidad multiplataforma, arquitectura y experiencia de usuario que impiden usar la aplicación como producto profesional.

---

## 2. Hallazgos Críticos de Funcionalidad (Requerimientos Detectados)

1. **Botones de ciclo escolar sin acción ("Cierre de Semestre" e "Inicio de Semestre")**
   - *Evidencia (`main.py`, líneas 80–81):* Ambos botones ejecutan `lambda: None`. No abren flujos de verificación, checklist ni confirmación.
2. **Tarjetas de indicadores incompletas**
   - *Evidencia (`main.py`, líneas 184–187 vs. `fuentes/dashboard_datos.py`, líneas 38–40):* El modelo devuelve 7 propiedades clave por indicador (`clave`, `meta`, `evidencias`, `seleccion`, `porcentaje_logrado`, `valoracion`, `publicacion`), pero la UI únicamente dibuja `ind['clave']`. Se omiten meta, estado de evidencias, selección (`0/3`), porcentaje de logro (y su barra de progreso), valoración y estado de publicación.
3. **Drive Histórico hardcodeado y bitácoras `.jsonl` ignoradas**
   - *Evidencia (`main.py`, líneas 127–136; `fuentes/dashboard_datos.py`, líneas 23–24):* `renderizar_historicos()` muestra dos tuplas fijas en código (`Instrumentacion_2026.docx` y `Cedula_2026EJ.pdf`), mientras `obtener_estado_dashboard()` lee `salidas/bitacora-firmas.jsonl` y `salidas/bitacora-subidas.jsonl` en variables anónimas (`_`) que descarta de inmediato.
4. **Flujo de firma digital incompleto y sin persistencia ni alertas**
   - *Evidencia (`main.py`, líneas 173–191; `fuentes/dashboard_datos.py`, líneas 35–36):* Solo existe el botón `"✓ Aprobar Firma"`, que muta `mat["planeacion"]["firma"] = "firmado"` en memoria sin confirmación humana explícita, sin estados intermedios ni flujo real (`sin enviar → enviado → firmado / con hallazgos`), sin escritura en `bitacora-firmas.jsonl` y sin mostrar nunca el campo `firma_alerta` ni permitir reportar hallazgos.
5. **Ancho fijo de 940 px, sin scroll con rueda y destrucción total de widgets**
   - *Evidencia (`main.py`, líneas 114–120, 142–144):* `canvas.create_window(..., width=940)` impide la responsividad al redimensionar la ventana; no existen bindings `<MouseWheel>` / `<Button-4>` / `<Button-5>`; `renderizar_panel_derecho()` invoca `widget.destroy()` sobre todos los hijos cada vez que cambia la materia seleccionada, generando parpadeo y pérdida de foco/estado.
6. **Colores hexadecimales dispersos y ajenos a la identidad de marca**
   - *Evidencia (`main.py`, líneas 30–188):* Usa colores genéricos hardcodeados (`#0D3BA7`, `#008FFB`, `#85C8FE`, `#E0F2FF`, `#F1F5F9`, `#B45309`, etc.) repetidos por todo el archivo sin archivo central de tokens (`tema.py`), ignorando la paleta oficial de Cadence Technologies (`#00304E`, `#006080`, `#00F0F0`, `#FFFFFF`, `#5B6770`).
7. **`"Cargar Archivo Local"` sin funcionalidad real**
   - *Evidencia (`main.py`, líneas 193–195):* Solo abre `filedialog.askopenfilename()` y muestra un `messagebox.showinfo("Cargado", "Archivo vinculado.")` sin copiar el archivo a `salidas/`, sin registrar en `salidas/bitacora-subidas.jsonl` y sin reflejarlo en Drive Histórico.
8. **Ausencia de estados vacíos, confirmaciones, toasts y feedback de carga**
   - No hay retroalimentación no bloqueante (toasts), ni modales de confirmación para acciones críticas, ni estados vacíos con guía accionable, ni indicadores de carga o procesamiento en curso.

---

## 3. Hallazgos Adicionales Detectados en la Auditoría

9. **Incompatibilidad multiplataforma en fuentes y cursores**
   - *Evidencia (`main.py`, líneas 8, 11, 22, 47, etc.):* Se usa `cursor="pointinghand"` (exclusivo de macOS; genera `TclError` o comportamiento errático en Windows/Linux si cambia la lógica) y tipografías propietarias de Apple (`"SF Pro Display"`, `"SF Pro Text"`) inexistentes en Windows/Linux.
10. **Falsos botones construidos con `tk.Label` (falla grave de accesibilidad)**
    - *Evidencia (`main.py`, líneas 7–17):* `crear_boton_moderno()` usa `tk.Label` con `<Button-1>`. No recibe foco por teclado (`Tab`), no responde a `Enter` ni `Espacio`, no muestra anillo de foco visible y carece de estado deshabilitado (`disabled`).
11. **Fallo grave de contraste WCAG AA**
    - *Evidencia (`main.py`, línea 156):* El KPI `HALLAZGOS` renderiza texto `#85C8FE` sobre fondo `#FFFFFF`, obteniendo un ratio de contraste de ~1.7:1 (muy por debajo del mínimo WCAG AA de 4.5:1 para texto normal).
12. **Gestión deficiente de ventana y DPI**
    - *Evidencia (`main.py`, líneas 28–30):* Tamaño fijo `1380x820` (puede desbordar pantallas de 1366x768 o 1280x720), sin `minsize`, sin centrado inicial ni activación de DPI awareness en Windows (provocando renderizado borroso en pantallas HiDPI).
13. **Arquitectura monolítica y acoplada**
    - Toda la UI vive en `main.py` sin separación en tokens (`tema.py`), componentes reutilizables (`componentes.py`), animaciones (`animaciones.py`) ni vistas dedicadas (`dashboard`, `indicadores`, `historico`, `bitacora`, `agentes`, `usuarios`).
14. **Rutas relativas frágiles y lectura JSONL sin tolerancia a fallos**
    - *Evidencia (`fuentes/dashboard_datos.py`, líneas 10–25):* `Path("credentials.json")` y `"salidas/..."` dependen del directorio actual de trabajo (`cwd`); si el usuario ejecuta `python camino/main.py` desde otro directorio, fallará o leerá vacío. Además, `json.loads(linea)` no captura `JSONDecodeError` ante líneas corruptas.
15. **Estado de entorno síncrono y hardcodeado**
    - *Evidencia (`fuentes/dashboard_datos.py`, línea 96):* `ollama_disponible` está fijo en `True` y la verificación de entorno no se ejecuta en segundo plano ni permite actualización reactiva sin bloquear el hilo de UI.
16. **Falta de identidad visual oficial, vistas operativas y dependencias declaradas**
    - No existía `requirements.txt`, ni carpeta `assets/` con el logo oficial animado e ícono de ventana, ni vistas para Bitácora, Agentes IA (orquestación), Usuarios/Permisos ni tarjeta de Impacto Energético.

---

## 4. Plan de Remediación Implementado

Cada punto de esta auditoría se corrige mediante:
- Definición del sistema de diseño en `design-system/MASTER.md`.
- Migración a `CustomTkinter` + `Pillow` fijados en `requirements.txt`.
- Arquitectura modular en `fuentes/` (`persistencia.py`, `dashboard_datos.py`) y `ui/` (`tema.py`, `iconos.py`, `animaciones.py`, `componentes.py`, `splash.py`, `app.py`, `vistas/*`).
- Incorporación del logo oficial animado (`assets/logo_cadence_transparente.png`) con respeto estricto de proporciones, área libre y contraste según superficie.
