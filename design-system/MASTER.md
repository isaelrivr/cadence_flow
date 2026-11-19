# Design System — Cadence Flow (`MASTER.md`)

**Empresa:** Cadence Technologies, S.A. de C.V.  
**Producto:** Cadence Flow (Orquestador de procesos académicos y agentes de IA)  
**Eslogan:** *"Datos en sincronía, decisiones con sentido."*  
**Versión:** 1.0  
**Plataforma:** Escritorio Python (`CustomTkinter` + `Pillow`) — Windows / macOS / Linux

---

## 1. Dirección Estética y Principios (UI/UX Pro Max + Frontend Design)

1. **Identidad "Música + Circuito" sin saturación:**
   - El sistema visual combina el ritmo armónico (onda sonora, progresión ordenada) con precisión electrónica (líneas finas tipo pista de PCB con nodos circulares y hexagonales como divisores e indicadores de estado).
   - **Disciplina visual:** un solo punto focal expresivo por vista (logo animado en splash/header y barras de progreso en degradado). El resto de la interfaz permanece sobrio, estructurado y legible.
   - **Cero relleno decorativo:** evitar etiquetas innecesarias en MAYÚSCULAS sobre cada tarjeta, evitar emojis estructurales en navegación/controles (usar íconos geométricos generados en Pillow) y evitar sombras grises idénticas por todas partes.
2. **Lenguaje claro y orientado a la acción:**
   - Voz activa en español natural (*"Aprobar firma"*, *"Cargar archivo local"*, *"Publicar indicador"*).
   - Coherencia nominal en todo el flujo: el botón *"Aprobar firma"* produce la confirmación y el toast *"Firma aprobada y registrada"*.
   - Estados vacíos y errores como guía práctica para actuar, nunca mensajes vagos.

---

## 2. Paleta Oficial y Tokens de Color (Verificados WCAG AA >= 4.5:1)

> **Regla absoluta:** Todos los valores hexadecimales viven exclusivamente en `ui/tema.py`. Ningún otro módulo de `ui/` ni `main.py` puede declarar colores literales.

### 2.1 Colores de Marca
| Token | Hex | Rol |
|---|---|---|
| `MARCA_AZUL_PROFUNDO` | `#00304E` | Fondos oscuros de marca (header), títulos principales en modo claro, texto de marca |
| `MARCA_AZUL_PETROLEO` | `#006080` | Subtítulos, encabezados secundarios, botones primarios sobre fondo claro, enlaces |
| `MARCA_CIAN` | `#00F0F0` | Acentos de circuito, rieles activos, inicio del degradado, anillo de foco por teclado, texto/ícono de acento **solo sobre fondos oscuros** |
| `MARCA_BLANCO` | `#FFFFFF` | Superficie de tarjetas (modo claro) y texto principal sobre fondos oscuros |
| `MARCA_GRIS_AZULADO` | `#5B6770` | Texto secundario y metadatos en modo claro (`5.8:1` sobre `#FFFFFF`) |

> **Prohibición de contraste:** Nunca usar `#00F0F0` como color de texto sobre `#FFFFFF` o `#F4F7FA` (`1.43:1` — falla WCAG). Sobre superficies claras se usa `#006080` (`7.04:1`) o `#00304E` (`13.7:1`).

### 2.2 Superficies, Bordes y Texto (Modo Claro / Modo Oscuro)
| Token | Modo Claro | Modo Oscuro | Contraste verificado |
|---|---|---|---|
| `FONDO_APP` | `#F4F7FA` | `#081B29` | Base general |
| `FONDO_SIDEBAR` | `#FFFFFF` | `#0B2233` | Barra lateral |
| `FONDO_HEADER` | `#00304E` | `#002238` | Header institucional oscuro |
| `SUPERFICIE` | `#FFFFFF` | `#0D2538` | Tarjetas principales |
| `SUPERFICIE_SUTIL` | `#EBF1F5` | `#133148` | Contenedores anidados / hover suave |
| `BORDE` | `#D6E1E8` | `#1E435E` | Contorno de tarjetas y divisores |
| `BORDE_ACTIVO` | `#006080` | `#00F0F0` | Selección / foco / énfasis |
| `TEXTO_PRIMARIO` | `#00304E` | `#E8F2F7` | `13.7:1` claro / `13.8:1` oscuro |
| `TEXTO_SECUNDARIO` | `#5B6770` | `#9BB1C0` | `5.8:1` claro / `7.05:1` oscuro |
| `TEXTO_SOBRE_HEADER` | `#FFFFFF` | `#FFFFFF` | `13.7:1` sobre `#00304E` |

### 2.3 Colores Semánticos (Armónicos con la paleta fría y verificados AA)
| Estado | Modo Claro (Texto / Fondo) | Modo Oscuro (Texto / Fondo) | Ratio |
|---|---|---|---|
| **Éxito** (`firmado`, `publicado`, `activo`, `conectado`) | `#0F6B5D` / `#E5F6F3` | `#5CE1CB` / `#0E3330` | `5.73:1` / `8.53:1` |
| **Alerta** (`enviado`, `en proceso`, `revisión`) | `#9A4A06` / `#FEF3E2` | `#FBBF4D` / `#38260E` | `5.70:1` / `8.72:1` |
| **Error** (`con hallazgos`, `error`, `sin configurar`) | `#B41E3A` / `#FDECEF` | `#FB7185` / `#3B1420` | `5.78:1` / `5.97:1` |
| **Info** (`sin enviar`, `ejecutando`, `info`) | `#006080` / `#E5F5FA` | `#5CE6F5` / `#0E2F42` | `6.29:1` / `9.37:1` |
| **Neutro** (`pendiente`, `pausado`) | `#5B6770` / `#EBF1F5` | `#9BB1C0` / `#133148` | `5.25:1` / `6.00:1` |

### 2.4 Degradado Oficial
- **Paradas:** `#00F0F0` (0%) → `#006080` (58%) → `#00304E` (100%).
- **Uso moderado exclusivo:** barra de carga del splash, barras de progreso de indicadores, franja superior de énfasis y acento de eficiencia energética.

---

## 3. Reglas de Uso del Logotipo Oficial

- **Archivo oficial intacto:** `assets/logo_cadence_transparente.png` (`646 × 373 px`, RGBA transparente).
- **Prohibido:** deformar relación de aspecto, redibujar, alterar colores del original o superponer texto encima.
- **Contraste por superficie:**
  - **Versión original a color:** únicamente sobre fondos claros (`#FFFFFF` / `#F4F7FA`, p. ej. pantalla splash).
  - **Versión monocromática blanca:** derivada directamente del canal alfa original (`RGB = 255, A = alpha`), utilizada sobre fondos oscuros (`#00304E`, p. ej. barra superior).
- **Área libre mínima (clearspace):** equivalente a la altura de la letra `"C"` de `CADENCE` (`~22.8%` de la altura total renderizada del logo; mínimo `8 px` en tamaños reducidos).
- **Ícono de ventana:** recortado del isotipo (clave de sol + circuito) y exportado a `assets/cadence_icon.ico` y `assets/cadence_icon.png`.

---

## 4. Tipografía

- **Familia principal:** `Inter` (cargada localmente desde `assets/fonts/Inter-{Regular,Medium,SemiBold,Bold}.ttf` mediante `ctk.FontManager.load_font` antes de crear la raíz Tk).
- **Respaldo multiplataforma:** `"Segoe UI"` (Windows), `"Helvetica Neue"` (macOS), `"Arial"` (Linux/fallback general).
- **Monoespaciada (códigos, claves, marcas de tiempo):** `"Cascadia Mono"` / `"Consolas"` (Windows), `"Menlo"` (macOS), `"DejaVu Sans Mono"` (Linux).

| Rol | Tamaño (pt) | Peso | Uso |
|---|---|---|---|
| `titulo_pagina` | `20` | `bold` | Encabezado principal de cada vista |
| `kpi_valor` | `18` | `bold` | Valor principal en tarjetas KPI |
| `subtitulo` | `14` | `bold` | Encabezados de sección (`Fase 1 · Planeación`, `Fase 2 · Cierre`) |
| `titulo_tarjeta` | `13` | `bold` | Títulos de tarjetas de asignatura, indicador o agente |
| `cuerpo_bold` | `12` | `bold` | Botones, ítems de navegación activos, etiquetas clave |
| `cuerpo` | `12` | `normal` | Texto general, descripciones, filas de tabla |
| `etiqueta` | `11` | `normal` | Subtextos, ayuda contextual, tooltips |
| `badge` | `11` | `bold` | Chips de estado y etiquetas compactas |
| `mono` | `11` | `normal` | Claves (`SCG-1009`), porcentajes, fechas ISO |

---

## 5. Escala de Espaciado, Radios y Dimensiones

- **Base 4 px:** `XS=4`, `SM=8`, `MD=12`, `LG=16`, `XL=20`, `XXL=24`, `XXXL=32`.
- **Radios de borde:**
  - Tarjetas y contenedores: `12 px`
  - Botones, inputs, menús desplegables y alertas: `8 px`
  - Chips/badges y barras de progreso: `999 px` (pill) / `6 px`
  - Modales: `14 px`
- **Bordes / Elevación:** Dado que Tkinter/CustomTkinter no implementa `box-shadow` difuso nativo por widget, la profundidad se construye mediante contraste limpio entre `FONDO_APP` y `SUPERFICIE` más borde nítido de `1 px` (`BORDE`), reservando `2 px` de borde o línea superior de circuito para elementos activos o enfocados.
- **Ventana principal:** mínimo `1040 × 680 px`, apertura centrada adaptada a resolución disponible (`<= 1320 × 840 px`), ancho fluido sin contenedores fijos de `940 px`.

---

## 6. Motion, Animaciones y Accesibilidad

- **Logo animado (30 fps / `33 ms`):**
  - 36 fotogramas precalculados y cacheados en `ui/animaciones.py` (sin reconstruir imágenes dentro de `after()`).
  - Efecto: destello cian (`#00F0F0`) diagonal recorriendo de izquierda a derecha recortado exactamente por el canal alfa del logo, más pulso sinusoidal suave de brillo (`±7%`).
  - **Comportamiento contextual:** loop continuo durante el splash (~2.0 s); en el header permanece estático en fotograma 0 y se anima solo al pasar el cursor o mientras una operación asíncrona/simulación está en curso.
  - **Ahorro de energía y accesibilidad:** pausa automática cuando la ventana se minimiza (`<Unmap>`) y detención inmediata al activar el interruptor **"Reducir movimiento"**.
- **Transición al cambiar de materia (~180 ms):**
  - Reutilización de widgets existentes (sin destruir tarjetas), aplicando una breve transición de énfasis en el borde/acento superior de las tarjetas activas (omitida si "Reducir movimiento" está activo).
- **Accesibilidad obligatoria:**
  - Cursor interactivo estándar `hand2` en todos los botones y controles clicables.
  - `takefocus=True`, navegación con `Tab`/`Shift+Tab`, activación con `Enter`/`Espacio` y anillo de foco visible (`#00F0F0` / `#006080`) en botones.
  - Estado `disabled` explícito en botones cuando no aplican.
  - Modales con `grab_set()`, cierre con `Escape` y scroll fluido con rueda del mouse en todas las vistas.
