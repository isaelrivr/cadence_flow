# Notas de Implementación y Decisiones Técnicas — Cadence Flow

**Fecha:** 2026-11-18  
**Empresa / Producto:** Cadence Technologies, S.A. de C.V. — *Cadence Flow*

---

## 1. Respaldo Inicial (Git)

- Antes de iniciar la refactorización se verificó que el repositorio Git local en `c:\Users\isael\Desktop\cadence_flow\cadence_flow` ya contaba con respaldo limpio en la rama `main` (commit inicial `98a9f2f: Initial commit: Cadence Flow`, sincronizado con `origin`). No fue necesario crear una carpeta duplicada en `../cadence_flow_backup`.

---

## 2. Skills Instalados y Referencias de Diseño

- **UI/UX Pro Max (`nextlevelbuilder/ui-ux-pro-max-skill`):**
  - El paquete npm vigente según el README oficial es `ui-ux-pro-max-cli` (que instala el comando `uipro`, reemplazando al antiguo `uipro-cli`).
  - Se instaló globalmente con `npm install -g ui-ux-pro-max-cli` y se inicializó en el proyecto con `uipro init --ai antigravity`, generando `.agents/skills/` (incluyendo `ui-ux-pro-max`, `brand`, `design`, `design-system`, `ui-styling`, `banner-design`, `slides`).
  - Se consultó `scripts/search.py` con `--design-system` y búsquedas de dominio `ux` (`keyboard focus modal`, `dark mode accessible contrast`).
- **Frontend Design (`anthropics/skills`):**
  - Instalado desde `skills/frontend-design` hacia `.agent/skills/frontend-design/` (`SKILL.md` y `LICENSE.txt`).
- **Skills previos (`hig-*`):**
  - Al revisar `.agent/skills/` al inicio no había skills `hig-*` preinstalados en el repositorio ni en `~/.gemini/antigravity`. Se aplicaron directamente sus principios universales de jerarquía visual, claridad de acciones y accesibilidad sin copiar la estética de Apple.
- **Sistema de diseño:** Generado y guardado antes de programar la UI en `design-system/MASTER.md`.

---

## 3. Logotipo Oficial, Íconos y Tipografía

- **Logotipo oficial:** Se copió intacto el PNG RGBA transparente proporcionado (`646 × 373 px`) a `assets/logo_cadence_transparente.png`.
  - No se rediseñó, deformó ni recoloró la versión original; esta se muestra únicamente sobre fondos claros (`ui/splash.py`).
  - Para el encabezado oscuro (`#00304E`), `ui/animaciones.py` deriva en memoria la variante **monocromática blanca** usando el canal alfa original.
  - Se respeta en todo momento un margen libre mínimo equivalente a la altura de la letra `"C"` (`~22.8%` de la altura renderizada del logotipo).
  - La animación opera a ~30 fps (`33 ms`) usando **36 fotogramas precalculados y cacheados** en `CTkImage` (destello cian `#00F0F0` diagonal recortado al canal alfa + pulso sinusoidal suave), pausándose automáticamente al minimizar la ventana o al activar **"Reducir movimiento"**.
- **Ícono de ventana:** Derivado directamente del recorte del isotipo (clave de sol + circuito) y exportado como `assets/cadence_icon.ico` (multi-resolución 16–256 px) y `assets/cadence_icon.png` (256×256 px).
- **Íconos geométricos de interfaz:** Generados con `Pillow` (antialiasing 2x) en `ui/iconos.py` bajo la estética circuito/nodos circulares y hexagonales (sin emojis estructurales).
- **Tipografía Inter:** Se descargó `Inter` v4.1 desde el repositorio oficial (`rsms/inter`) y se extrajeron las fuentes estáticas `Inter-Regular.ttf`, `Inter-Medium.ttf`, `Inter-SemiBold.ttf` e `Inter-Bold.ttf` en `assets/fonts/`. Se cargan antes de instanciar la raíz Tk mediante `ctk.FontManager.load_font()` con respaldo multiplataforma (`Segoe UI` / `Helvetica Neue` / `Arial`).

---

## 4. Alternativas Técnicas en CustomTkinter (Limitaciones de Tk)

1. **Sombras difusas nativas (`box-shadow`):**
   - Tkinter/CustomTkinter no soporta sombras CSS difusas por widget sin imágenes de fondo por tamaño variable. Se resolvió aplicando contraste nítido entre niveles de superficie (`FONDO_APP` vs `SUPERFICIE`), bordes definidos de `1 px` (`BORDE`) y líneas superiores sutiles de énfasis (`con_acento=True`).
2. **Transición suave al cambiar de materia sin opacidad por widget:**
   - Tk no ofrece transparencia alfa independiente por `Frame`. Para evitar destruir y recrear widgets, `ui/animaciones.py` ejecuta una transición breve (~180 ms) de énfasis cromático en los bordes de las tarjetas reutilizadas (`animar_transicion_cambio_materia`), respetando `"Reducir movimiento"`.
3. **Foco por teclado en `CTkButton` (CustomTkinter 6.0.0):**
   - `CTkButton` no expone `takefocus` en su constructor. `BotonCadence` configura `self._canvas.configure(takefocus=1)` internamente y vincula `<FocusIn>`, `<FocusOut>`, `<Return>` y `<space>` para navegación completa con teclado y anillo de foco visible.
4. **Scroll seguro con rueda y estabilidad HiDPI en CustomTkinter 6.0.0:**
   - `CTkScrollableFrame._check_if_valid_scroll` puede recibir referencias de cadena si un tooltip o menú se cierra durante el desplazamiento; `habilitar_scroll_fluido` añade resguardo de tipo y visibilidad (`winfo_ismapped()`).
   - Bajo escalado HiDPI de Windows (>100%), `CTkScrollbar._draw()` invoca `update_idletasks()`, lo que puede disparar recursión si `CTkImage` o `scrollbar.set()` cambian el tamaño solicitado en `<Configure>`. Se mitigó con una guarda de reentrancia en `_proteger_scrollbar_ctk` y renderizando `BarraProgresoDegradado` directamente sobre `tk.Canvas` con `ImageTk.PhotoImage`.
5. **Alcance simulado (solo frontend):**
   - Todas las métricas de **Impacto energético**, **Agentes IA**, **Usuarios y permisos**, la verificación de **Drive** (cuando no existe `credentials.json`) y la simulación de **Ollama** cuando no está escuchando en `127.0.0.1:11434` operan en modo frontend simulado. Las firmas digitales y subidas de archivos sí persisten localmente en `salidas/bitacora-firmas.jsonl`, `salidas/bitacora-subidas.jsonl` y `salidas/archivos/`.
