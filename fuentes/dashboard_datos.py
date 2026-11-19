"""Datos simulados e hidratación de estado para Cadence Flow.

Mantiene íntegras las llaves originales devueltas por obtener_estado_dashboard()
y añade información enriquecida para bitácora, agentes, usuarios, impacto
energético y checklist de inicio/cierre de semestre.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from fuentes.persistencia import (
    BITACORA_FIRMAS,
    BITACORA_SUBIDAS,
    leer_jsonl,
    verificar_entorno_sync,
)

try:
    from agente.cliente import MODELO as MODELO_IA_ACTIVO
except ImportError:
    MODELO_IA_ACTIVO = "qwen3:8b"


def _meta_numerica(meta_texto: str) -> int:
    """Extrae el porcentaje numérico de la meta institucional."""
    coincidencia = re.search(r"(\d+)", meta_texto or "")
    return int(coincidencia.group(1)) if coincidencia else 70


def crear_items_evidencia(seleccion_inicial: int = 0) -> List[Dict[str, Any]]:
    """Crea la lista estándar de 3 evidencias por indicador."""
    nombres = [
        "Rúbrica firmada por academia",
        "Muestra de evidencias estudiantiles",
        "Lista de cotejo y acta de cierre",
    ]
    return [
        {"nombre": nombre, "marcada": idx < seleccion_inicial}
        for idx, nombre in enumerate(nombres)
    ]


def recalcular_indicador(indicador: Dict[str, Any]) -> Dict[str, Any]:
    """Recalcula selección, estado de evidencias, porcentaje y valoración."""
    items = indicador.get("evidencias_items", [])
    total = len(items) if items else 3
    marcadas = sum(1 for item in items if item.get("marcada"))
    indicador["seleccion"] = f"{marcadas}/{total}"

    if marcadas == 0:
        indicador["evidencias"] = "pendiente"
        indicador["porcentaje_logrado"] = None
        indicador["valoracion"] = None
        return indicador

    meta_num = _meta_numerica(indicador.get("meta", "70 %"))
    if marcadas == 1:
        indicador["evidencias"] = "en proceso"
        logro = max(35, round(meta_num * 0.55))
    elif marcadas == 2:
        indicador["evidencias"] = "en proceso"
        logro = min(96, round(meta_num * 0.88))
    else:
        indicador["evidencias"] = "completa"
        logro = min(98, max(meta_num + 12, 82))

    indicador["porcentaje_logrado"] = logro
    if logro >= 85:
        indicador["valoracion"] = "Excelente"
    elif logro >= 75:
        indicador["valoracion"] = "Notable"
    elif logro >= 65:
        indicador["valoracion"] = "Suficiente"
    else:
        indicador["valoracion"] = "Parcialmente lo logra"
    return indicador


def _crear_indicador(
    clave: str,
    meta: str,
    descripcion: str,
    seleccion_inicial: int = 0,
    publicacion: str = "pendiente",
) -> Dict[str, Any]:
    """Construye un indicador conservando todas las llaves originales del contrato."""
    ind: Dict[str, Any] = {
        "clave": clave,
        "meta": meta,
        "evidencias": "pendiente",
        "seleccion": f"{seleccion_inicial}/3",
        "porcentaje_logrado": None,
        "valoracion": None,
        "publicacion": publicacion,
        "descripcion": descripcion,
        "evidencias_items": crear_items_evidencia(seleccion_inicial),
    }
    return recalcular_indicador(ind)


def obtener_estado_dashboard(periodo_normalizado: str = "2026AD") -> Dict[str, Any]:
    """Devuelve el estado completo del dashboard preservando las llaves base."""
    entorno_vivo = verificar_entorno_sync()
    bitacora_firmas = leer_jsonl(BITACORA_FIRMAS)
    bitacora_subidas = leer_jsonl(BITACORA_SUBIDAS)

    asignaturas: List[Dict[str, Any]] = [
        {
            "nombre": "Gestión de Proyectos de Software",
            "clave": "SCG-1009",
            "grupo": "B17A",
            "meta_institucional": "60% Parcialmente lo logra",
            "planeacion": {
                "documento": f"Instrumentacion_SCG1009_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "sin enviar",
                "firma_alerta": None,
                "ultima_actualizacion": "Sin movimientos recientes",
                "firmado_por": None,
            },
            "indicadores": [
                _crear_indicador(
                    "AE7-CD2-I1",
                    "60 % del grupo",
                    "Planificación de cronograma y estimación de esfuerzo",
                    seleccion_inicial=2,
                ),
                _crear_indicador(
                    "AE8-CD1-I2",
                    "60 % del grupo",
                    "Gestión de riesgos y control de cambios del proyecto",
                    seleccion_inicial=1,
                ),
                _crear_indicador(
                    "AE10-CD1-I1",
                    "60 % del grupo",
                    "Aseguramiento de calidad y pruebas de integración",
                    seleccion_inicial=0,
                ),
                _crear_indicador(
                    "AE10-CD2-I1",
                    "60 % del grupo",
                    "Cierre documental y entrega de métricas finales",
                    seleccion_inicial=0,
                ),
            ],
        },
        {
            "nombre": "Análisis de Datos y ML",
            "clave": "TDB-2405",
            "grupo": "51DA",
            "meta_institucional": "75% Notablemente",
            "planeacion": {
                "documento": f"Instrumentacion_TDB2405_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "enviado",
                "firma_alerta": "En espera de aprobación humana para emitir firma digital.",
                "ultima_actualizacion": "Enviado a revisión académica",
                "firmado_por": None,
            },
            "indicadores": [
                _crear_indicador(
                    "AE2-CD2-I2",
                    "75 % del grupo",
                    "Limpieza, normalización y análisis exploratorio de datos",
                    seleccion_inicial=3,
                    publicacion="publicado",
                ),
                _crear_indicador(
                    "AE3-CD1-I1",
                    "75 % del grupo",
                    "Entrenamiento y validación cruzada de modelos supervisados",
                    seleccion_inicial=2,
                ),
                _crear_indicador(
                    "AE5-CD2-I2",
                    "75 % del grupo",
                    "Interpretación de métricas y despliegue reproducible",
                    seleccion_inicial=1,
                ),
            ],
        },
        {
            "nombre": "Sistemas Programables",
            "clave": "SCC-1023",
            "grupo": "F18A",
            "meta_institucional": "80% Excelente",
            "planeacion": {
                "documento": f"Instrumentacion_SCC1023_{periodo_normalizado}.docx",
                "hallazgos_verificador": 1,
                "firma": "con hallazgos",
                "firma_alerta": (
                    "Verificador reportó 1 hallazgo: falta adjuntar rúbrica "
                    "de práctica 2 en la sección de evaluación sumativa."
                ),
                "ultima_actualizacion": "Observado por verificador de calidad",
                "firmado_por": None,
            },
            "indicadores": [
                _crear_indicador(
                    "AE3-CD2-I2",
                    "80 % del grupo",
                    "Programación de interrupciones y temporizadores en microcontrolador",
                    seleccion_inicial=2,
                ),
                _crear_indicador(
                    "AE5-CD1-I1",
                    "80 % del grupo",
                    "Integración de sensores, actuadores y comunicación serial",
                    seleccion_inicial=0,
                ),
            ],
        },
        {
            "nombre": "Inteligencia Artificial",
            "clave": "SCC-1012",
            "grupo": "B18A",
            "meta_institucional": "70% Suficiente",
            "planeacion": {
                "documento": f"Instrumentacion_SCC1012_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "firmado",
                "firma_alerta": None,
                "ultima_actualizacion": "Firma digital validada",
                "firmado_por": "M.C. Lamia Hamdan Medina",
            },
            "indicadores": [
                _crear_indicador(
                    "AE7-CD2-I2",
                    "70 % del grupo",
                    "Diseño de agentes inteligentes y búsqueda heurística",
                    seleccion_inicial=3,
                    publicacion="publicado",
                ),
            ],
        },
    ]

    # Hidratar estados de firma desde la bitácora persistida en disco
    por_clave = {m["clave"]: m for m in asignaturas}
    for ev in bitacora_firmas:
        clave = ev.get("clave_materia")
        if clave in por_clave:
            plan = por_clave[clave]["planeacion"]
            estado_nuevo = ev.get("estado_nuevo") or ev.get("estado")
            if estado_nuevo in {"sin enviar", "enviado", "con hallazgos", "firmado"}:
                plan["firma"] = estado_nuevo
                plan["ultima_actualizacion"] = ev.get("timestamp", plan["ultima_actualizacion"])
                if estado_nuevo == "firmado":
                    plan["hallazgos_verificador"] = 0
                    plan["firma_alerta"] = None
                    plan["firmado_por"] = ev.get("usuario", "Docente Titular")
                elif estado_nuevo == "con hallazgos":
                    plan["hallazgos_verificador"] = max(1, int(plan["hallazgos_verificador"]) + 1)
                    plan["firma_alerta"] = ev.get("detalle") or "Hallazgo registrado en bitácora."
                elif estado_nuevo == "enviado":
                    plan["hallazgos_verificador"] = 0
                    plan["firma_alerta"] = "En espera de aprobación humana para emitir firma digital."
                else:
                    plan["firma_alerta"] = None

    historico_base: List[Dict[str, Any]] = [
        {
            "archivo": "Instrumentacion_2026.docx",
            "periodo": "2026EJ",
            "clave_materia": "SCG-1009",
            "materia": "Gestión de Proyectos de Software",
            "origen": "Histórico 2026EJ",
            "estado": "firmado",
            "usuario": "M.C. Lamia Hamdan Medina",
            "timestamp": "2026-06-18 14:20:00",
            "detalle": "Instrumentación didáctica archivada en ciclo anterior.",
        },
        {
            "archivo": "Cedula_2026EJ.pdf",
            "periodo": "2026EJ",
            "clave_materia": "SCC-1012",
            "materia": "Inteligencia Artificial",
            "origen": "Histórico 2026EJ",
            "estado": "publicado",
            "usuario": "M.C. Lamia Hamdan Medina",
            "timestamp": "2026-06-24 11:05:00",
            "detalle": "Cédula de indicadores publicada en cierre 2026EJ.",
        },
    ]

    agentes: List[Dict[str, Any]] = [
        {
            "id": "ag_firma",
            "nombre": "Agente de Firma Digital",
            "rol": "Custodia criptográfica y aprobación humana",
            "descripcion": "Prepara paquetes de instrumentación y exige confirmación humana explícita antes de sellar el registro en bitácora.",
            "estado": "activo",
            "ultima_ejecucion": "Hace 6 min",
            "tareas_hoy": 12,
            "consumo_wh": 4.2,
            "cola": 1,
        },
        {
            "id": "ag_verificador",
            "nombre": "Agente Verificador Académico",
            "rol": "Auditoría de rúbricas y metas",
            "descripcion": "Analiza estructura de instrumentaciones para detectar secciones incompletas o evidencias faltantes.",
            "estado": "activo",
            "ultima_ejecucion": "Hace 14 min",
            "tareas_hoy": 9,
            "consumo_wh": 6.8,
            "cola": 1,
        },
        {
            "id": "ag_drive",
            "nombre": "Agente Sincronizador Drive",
            "rol": "Respaldo e indexación histórica",
            "descripcion": "Indexa archivos locales vinculados hacia Drive Histórico y mantiene consistencia con bitacora-subidas.jsonl.",
            "estado": "pausado" if not entorno_vivo["drive_autenticado"] else "activo",
            "ultima_ejecucion": "Pendiente OAuth" if not entorno_vivo["drive_autenticado"] else "Hace 3 min",
            "tareas_hoy": 4,
            "consumo_wh": 2.1,
            "cola": 0,
        },
        {
            "id": "ag_evaluador",
            "nombre": "Agente Evaluador de Indicadores",
            "rol": "Cálculo de logro y valoración",
            "descripcion": "Consolida evidencias seleccionadas por asignatura para proyectar porcentaje de logro frente a la meta institucional.",
            "estado": "activo",
            "ultima_ejecucion": "Hace 2 min",
            "tareas_hoy": 15,
            "consumo_wh": 5.4,
            "cola": 0,
        },
        {
            "id": "ag_energia",
            "nombre": "Agente Monitor Energético",
            "rol": "Telemetría local eficiente",
            "descripcion": "Mide consumo estimado de inferencia local frente a centros de datos en la nube para optimizar ciclos de ejecución.",
            "estado": "activo",
            "ultima_ejecucion": "Continuo",
            "tareas_hoy": 24,
            "consumo_wh": 1.3,
            "cola": 0,
        },
    ]

    usuarios: List[Dict[str, Any]] = [
        {
            "nombre": "M.C. Lamia Hamdan Medina",
            "iniciales": "HML",
            "correo": "l.hamdan@cadence-academico.edu.mx",
            "rol": "Docente Titular",
            "estado": "activo",
            "permisos": {
                "instrumentaciones": True,
                "firmar_documentos": True,
                "subir_evidencias": True,
                "gestionar_agentes": False,
                "gestion_semestre": True,
                "auditoria_bitacora": True,
            },
        },
        {
            "nombre": "Ing. Valeria Mendoza Cruz",
            "iniciales": "VMC",
            "correo": "v.mendoza@cadence-academico.edu.mx",
            "rol": "Verificador de Calidad",
            "estado": "activo",
            "permisos": {
                "instrumentaciones": True,
                "firmar_documentos": False,
                "subir_evidencias": True,
                "gestionar_agentes": False,
                "gestion_semestre": False,
                "auditoria_bitacora": True,
            },
        },
        {
            "nombre": "Dr. Arturo Salinas Vega",
            "iniciales": "ASV",
            "correo": "a.salinas@cadence-academico.edu.mx",
            "rol": "Coordinador Académico",
            "estado": "activo",
            "permisos": {
                "instrumentaciones": True,
                "firmar_documentos": True,
                "subir_evidencias": True,
                "gestionar_agentes": True,
                "gestion_semestre": True,
                "auditoria_bitacora": True,
            },
        },
        {
            "nombre": "Isael Rivera",
            "iniciales": "IR",
            "correo": "isael@cadencetechnologies.mx",
            "rol": "Administrador Cadence Flow",
            "estado": "activo",
            "permisos": {
                "instrumentaciones": True,
                "firmar_documentos": True,
                "subir_evidencias": True,
                "gestionar_agentes": True,
                "gestion_semestre": True,
                "auditoria_bitacora": True,
            },
        },
    ]

    impacto_energetico: Dict[str, Any] = {
        "kwh_periodo": 1.42,
        "co2_kg": 0.61,
        "ahorro_vs_nube_pct": 68,
        "ejecuciones_locales": 34,
        "eficiencia": "Óptima",
        "modelo_referencia": MODELO_IA_ACTIVO,
    }

    semestre_inicio: List[Dict[str, Any]] = [
        {
            "id": "ini_1",
            "titulo": "Verificar catálogo de asignaturas y grupos",
            "descripcion": f"Confirmar carga académica registrada para el periodo {periodo_normalizado}.",
            "completado": True,
        },
        {
            "id": "ini_2",
            "titulo": "Sincronizar plantillas de instrumentación",
            "descripcion": "Validar encabezados institucionales y metas de aprendizaje por clave.",
            "completado": True,
        },
        {
            "id": "ini_3",
            "titulo": "Inicializar bitácoras y carpeta de evidencias",
            "descripcion": "Preparar salidas/archivos/ y bitácoras JSONL para trazabilidad.",
            "completado": False,
        },
        {
            "id": "ini_4",
            "titulo": "Activar agentes verificadores del ciclo",
            "descripcion": "Habilitar monitoreo de firmas, indicadores y telemetría energética.",
            "completado": False,
        },
    ]

    semestre_cierre: List[Dict[str, Any]] = [
        {
            "id": "cie_1",
            "titulo": "Confirmar firmas digitales de planeación",
            "descripcion": "Todas las asignaturas deben estar firmadas y sin hallazgos abiertos.",
            "completado": all(m["planeacion"]["firma"] == "firmado" for m in asignaturas),
        },
        {
            "id": "cie_2",
            "titulo": "Completar selección de evidencias (3/3)",
            "descripcion": "Verificar rúbricas, muestras estudiantiles y listas de cotejo.",
            "completado": all(
                ind["evidencias"] == "completa"
                for m in asignaturas
                for ind in m["indicadores"]
            ),
        },
        {
            "id": "cie_3",
            "titulo": "Publicar cédulas de indicadores",
            "descripcion": "Marcar indicadores evaluados como publicados para cierre académico.",
            "completado": all(
                ind["publicacion"] == "publicado"
                for m in asignaturas
                for ind in m["indicadores"]
            ),
        },
        {
            "id": "cie_4",
            "titulo": "Respaldar bitácora y paquete de cierre",
            "descripcion": "Consolidar archivos en salidas/ y emitir comprobante del periodo.",
            "completado": False,
        },
    ]

    return {
        "periodo": periodo_normalizado,
        "docente_iniciales": "HML",
        "docente_nombre": "M.C. Lamia Hamdan Medina",
        "empresa": "Cadence Technologies, S.A. de C.V.",
        "eslogan": "Datos en sincronía, decisiones con sentido.",
        "entorno": {
            "ollama_disponible": entorno_vivo["ollama_disponible"],
            "modelo_activo": MODELO_IA_ACTIVO,
            "drive_autenticado": entorno_vivo["drive_autenticado"],
            "ollama_en_linea": entorno_vivo["ollama_en_linea"],
            "detalle_drive": entorno_vivo["detalle_drive"],
            "detalle_ollama": entorno_vivo["detalle_ollama"],
            "verificado_en": entorno_vivo["verificado_en"],
        },
        "asignaturas": asignaturas,
        "bitacora_firmas": bitacora_firmas,
        "bitacora_subidas": bitacora_subidas,
        "historico_base": historico_base,
        "agentes": agentes,
        "usuarios": usuarios,
        "impacto_energetico": impacto_energetico,
        "semestre_inicio": semestre_inicio,
        "semestre_cierre": semestre_cierre,
    }


def construir_historico(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Combina archivos base de Drive Histórico con subidas y firmas registradas."""
    elementos: List[Dict[str, Any]] = []

    for sub in datos.get("bitacora_subidas", []):
        elementos.append(
            {
                "archivo": sub.get("archivo_original", "archivo_local"),
                "ruta_local": sub.get("archivo_guardado", ""),
                "periodo": datos.get("periodo", "2026AD"),
                "clave_materia": sub.get("clave_materia", ""),
                "materia": sub.get("materia", ""),
                "origen": "Subida local",
                "estado": sub.get("estado", "vinculado"),
                "usuario": sub.get("usuario", datos.get("docente_nombre", "HML")),
                "timestamp": sub.get("timestamp", ""),
                "detalle": (
                    f"Copiado a {sub.get('archivo_guardado', 'salidas/archivos')} "
                    f"({sub.get('tamano_kb', 1)} KB)."
                ),
            }
        )

    for frm in datos.get("bitacora_firmas", []):
        elementos.append(
            {
                "archivo": frm.get("documento", "Instrumentacion.docx"),
                "ruta_local": "",
                "periodo": datos.get("periodo", "2026AD"),
                "clave_materia": frm.get("clave_materia", ""),
                "materia": frm.get("materia", ""),
                "origen": "Firma digital",
                "estado": frm.get("estado_nuevo", frm.get("estado", "firmado")),
                "usuario": frm.get("usuario", datos.get("docente_nombre", "HML")),
                "timestamp": frm.get("timestamp", ""),
                "detalle": frm.get("detalle", "Evento registrado en bitácora de firmas."),
            }
        )

    for base in datos.get("historico_base", []):
        elementos.append(dict(base))

    elementos.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return elementos


def construir_bitacora_unificada(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Unifica eventos de bitacora-firmas.jsonl y bitacora-subidas.jsonl."""
    filas: List[Dict[str, Any]] = []

    for ev in datos.get("bitacora_firmas", []):
        filas.append(
            {
                "timestamp": ev.get("timestamp", ""),
                "origen": "Firmas",
                "usuario": ev.get("usuario", "Sistema"),
                "accion": ev.get("accion", "Movimiento de firma"),
                "referencia": f"{ev.get('clave_materia', '')} · {ev.get('documento', '')}".strip(" ·"),
                "estado": ev.get("estado_nuevo", ev.get("estado", "firmado")),
                "detalle": ev.get("detalle", ""),
            }
        )

    for ev in datos.get("bitacora_subidas", []):
        filas.append(
            {
                "timestamp": ev.get("timestamp", ""),
                "origen": "Subidas",
                "usuario": ev.get("usuario", "Sistema"),
                "accion": ev.get("accion", "Subida de archivo"),
                "referencia": f"{ev.get('clave_materia', '')} · {ev.get('archivo_original', '')}".strip(" ·"),
                "estado": ev.get("estado", "vinculado"),
                "detalle": ev.get("archivo_guardado", ""),
            }
        )

    filas.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return filas
