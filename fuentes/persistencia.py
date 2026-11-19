"""Capa de persistencia local (JSONL, copia de archivos y verificación de entorno).

Gestiona todas las rutas relativas respecto a la raíz del proyecto para garantizar
que la aplicación funcione correctamente sin importar el directorio de ejecución.
"""

from __future__ import annotations

import json
import re
import shutil
import socket
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
SALIDAS_DIR = BASE_DIR / "salidas"
ARCHIVOS_DIR = SALIDAS_DIR / "archivos"
BITACORA_FIRMAS = SALIDAS_DIR / "bitacora-firmas.jsonl"
BITACORA_SUBIDAS = SALIDAS_DIR / "bitacora-subidas.jsonl"


def resolver_ruta(ruta: Path | str) -> Path:
    """Resuelve una ruta relativa tomando como base la raíz del proyecto."""
    p = Path(ruta)
    return p if p.is_absolute() else (BASE_DIR / p)


def ahora_iso() -> str:
    """Devuelve la fecha y hora local formateada de manera legible y ordenable."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def leer_jsonl(ruta: Path | str) -> List[Dict[str, Any]]:
    """Lee un archivo JSONL línea por línea tolerando líneas vacías o malformadas."""
    archivo = resolver_ruta(ruta)
    if not archivo.exists():
        return []
    registros: List[Dict[str, Any]] = []
    with archivo.open("r", encoding="utf-8") as f:
        for linea in f:
            texto = linea.strip()
            if not texto:
                continue
            try:
                dato = json.loads(texto)
                if isinstance(dato, dict):
                    registros.append(dato)
            except json.JSONDecodeError:
                # Se ignora cualquier línea corrupta para no interrumpir la carga
                continue
    return registros


def agregar_jsonl(ruta: Path | str, registro: Dict[str, Any]) -> Dict[str, Any]:
    """Agrega un registro JSON en una nueva línea al archivo JSONL indicado."""
    archivo = resolver_ruta(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    entrada = dict(registro)
    entrada.setdefault("timestamp", ahora_iso())
    with archivo.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    return entrada


def sanitizar_nombre_archivo(nombre: str) -> str:
    """Limpia caracteres problemáticos de un nombre de archivo."""
    limpio = re.sub(r"[^A-Za-z0-9._-]", "_", nombre)
    return limpio or "archivo_sin_nombre"


def copiar_archivo_a_salidas(
    origen: str | Path,
    materia: Dict[str, Any],
    usuario: str,
) -> Dict[str, Any]:
    """Copia un archivo local a salidas/archivos/ y registra la subida en bitácora."""
    src = Path(origen)
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"No se encontró el archivo seleccionado: {src}")

    ARCHIVOS_DIR.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_destino = f"{marca}_{sanitizar_nombre_archivo(src.name)}"
    destino = ARCHIVOS_DIR / nombre_destino
    shutil.copy2(src, destino)

    tamano_kb = max(1, round(destino.stat().st_size / 1024))
    registro = {
        "timestamp": ahora_iso(),
        "tipo": "subida",
        "usuario": usuario,
        "accion": "Subida de archivo local",
        "clave_materia": materia.get("clave", ""),
        "materia": materia.get("nombre", ""),
        "grupo": materia.get("grupo", ""),
        "archivo_original": src.name,
        "archivo_guardado": str(destino.relative_to(BASE_DIR)).replace("\\", "/"),
        "tamano_kb": tamano_kb,
        "estado": "vinculado",
    }
    return agregar_jsonl(BITACORA_SUBIDAS, registro)


def registrar_evento_firma(
    usuario: str,
    rol: str,
    materia: Dict[str, Any],
    estado_anterior: str,
    estado_nuevo: str,
    accion: str,
    detalle: str,
    aprobacion_humana: bool = False,
) -> Dict[str, Any]:
    """Registra una transición o evento de firma digital en bitacora-firmas.jsonl."""
    planeacion = materia.get("planeacion", {})
    registro = {
        "timestamp": ahora_iso(),
        "tipo": "firma",
        "usuario": usuario,
        "rol": rol,
        "accion": accion,
        "clave_materia": materia.get("clave", ""),
        "materia": materia.get("nombre", ""),
        "grupo": materia.get("grupo", ""),
        "documento": planeacion.get("documento", ""),
        "estado_anterior": estado_anterior,
        "estado_nuevo": estado_nuevo,
        "estado": estado_nuevo,
        "detalle": detalle,
        "aprobacion_humana": aprobacion_humana,
    }
    return agregar_jsonl(BITACORA_FIRMAS, registro)


def verificar_entorno_sync() -> Dict[str, Any]:
    """Comprueba credenciales de Drive y disponibilidad de Ollama en localhost."""
    drive_ok = (BASE_DIR / "credentials.json").exists()
    ollama_vivo = False
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=0.45):
            ollama_vivo = True
    except OSError:
        ollama_vivo = False

    return {
        "drive_autenticado": drive_ok,
        "ollama_disponible": True,
        "ollama_en_linea": ollama_vivo,
        "detalle_drive": (
            "Credenciales OAuth detectadas"
            if drive_ok
            else "Modo simulado (falta credentials.json)"
        ),
        "detalle_ollama": (
            "Servicio Ollama activo en 127.0.0.1:11434"
            if ollama_vivo
            else "Motor simulado en modo offline"
        ),
        "verificado_en": ahora_iso(),
    }


def verificar_entorno_async(
    callback: Callable[[Dict[str, Any]], None],
) -> threading.Thread:
    """Lanza la verificación del entorno en un hilo daemon sin bloquear la UI."""

    def _tarea() -> None:
        resultado = verificar_entorno_sync()
        callback(resultado)

    hilo = threading.Thread(target=_tarea, daemon=True)
    hilo.start()
    return hilo
