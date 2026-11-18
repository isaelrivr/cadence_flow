import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from agente.cliente import MODELO as MODELO_IA_ACTIVO
except ImportError:
    MODELO_IA_ACTIVO = "qwen3:8b"

def leer_jsonl(ruta: str) -> List[Dict[str, Any]]:
    archivo = Path(ruta)
    if not archivo.exists():
        return []
    registros = []
    with archivo.open("r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                registros.append(json.loads(linea))
    return registros

def obtener_estado_dashboard(periodo_normalizado: str = "2026AD") -> Dict[str, Any]:
    drive_configurado = Path("credentials.json").exists()
    _ = leer_jsonl("salidas/bitacora-firmas.jsonl")
    _ = leer_jsonl("salidas/bitacora-subidas.jsonl")

    asignaturas = [
        {
            "nombre": "Gestión de Proyectos de Software",
            "clave": "SCG-1009",
            "grupo": "B17A",
            "meta_institucional": "60% Parcialmente lo logra",
            "planeacion": {
                "documento": f"Instrumentacion_SCG1009_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "sin enviar",
                "firma_alerta": None
            },
            "indicadores": [
                {"clave": inv, "meta": "60 % del grupo", "evidencias": "pendiente", "seleccion": "0/3", "porcentaje_logrado": None, "valoracion": None, "publicacion": "pendiente"}
                for inv in ["AE7-CD2-I1", "AE8-CD1-I2", "AE10-CD1-I1", "AE10-CD2-I1"]
            ]
        },
        {
            "nombre": "Análisis de Datos y ML",
            "clave": "TDB-2405",
            "grupo": "51DA",
            "meta_institucional": "75% Notablemente",
            "planeacion": {
                "documento": f"Instrumentacion_TDB2405_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "sin enviar",
                "firma_alerta": None
            },
            "indicadores": [
                {"clave": inv, "meta": "75 % del grupo", "evidencias": "pendiente", "seleccion": "0/3", "porcentaje_logrado": None, "valoracion": None, "publicacion": "pendiente"}
                for inv in ["AE2-CD2-I2", "AE3-CD1-I1", "AE5-CD2-I2"]
            ]
        },
        {
            "nombre": "Sistemas Programables",
            "clave": "SCC-1023",
            "grupo": "F18A",
            "meta_institucional": "80% Excelente",
            "planeacion": {
                "documento": f"Instrumentacion_SCC1023_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "sin enviar",
                "firma_alerta": None
            },
            "indicadores": [
                {"clave": inv, "meta": "80 % del grupo", "evidencias": "pendiente", "seleccion": "0/3", "porcentaje_logrado": None, "valoracion": None, "publicacion": "pendiente"}
                for inv in ["AE3-CD2-I2", "AE5-CD1-I1"]
            ]
        },
        {
            "nombre": "Inteligencia Artificial",
            "clave": "SCC-1012",
            "grupo": "B18A",
            "meta_institucional": "70% Suficiente",
            "planeacion": {
                "documento": f"Instrumentacion_SCC1012_{periodo_normalizado}.docx",
                "hallazgos_verificador": 0,
                "firma": "sin enviar",
                "firma_alerta": None
            },
            "indicadores": [
                {"clave": "AE7-CD2-I2", "meta": "70 % del grupo", "evidencias": "pendiente", "seleccion": "0/3", "porcentaje_logrado": None, "valoracion": None, "publicacion": "pendiente"}
            ]
        }
    ]

    return {
        "periodo": periodo_normalizado,
        "docente_iniciales": "HML",
        "entorno": {
            "ollama_disponible": True,
            "modelo_activo": MODELO_IA_ACTIVO,
            "drive_autenticado": drive_configurado
        },
        "asignaturas": asignaturas
    }