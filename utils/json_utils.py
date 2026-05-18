# -*- coding: utf-8 -*-
"""
Helpers JSON del Sistema Caracterizador de Eventos Afectivos.

Tres utilidades:
  - parse_llm_json:     parsea respuestas del LLM con mensaje de error claro.
  - load_event_from_dict: construye un Event desde el contrato de entrada.
  - save_event_output:  guarda la salida final del pipeline en archivo.
"""

import json
import re

from models.event_model import Event


REQUIRED_INPUT_FIELDS = ("event_id", "timestamp", "raw_description")

_MARKDOWN_FENCE_RE = re.compile(
    r"```(?:json)?\s*(.*?)\s*```",
    flags=re.DOTALL | re.IGNORECASE,
)


def parse_llm_json(raw_text):
    """
    Parsea un string que se espera sea JSON proveniente del LLM.

    Si el LLM envolvió el JSON en un bloque de markdown (```json ... ```),
    lo extrae antes de parsear. Esto ocurre cuando se llama al LLM SIN
    json_mode; con json_mode=True normalmente llega limpio.

    :raises ValueError: con un preview del texto si no se pudo parsear.
    """
    if raw_text is None:
        raise ValueError("El LLM devolvió None (respuesta vacía).")

    text = raw_text.strip()

    fence_match = _MARKDOWN_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        preview = raw_text[:200]
        raise ValueError(
            f"El LLM devolvió texto no parseable como JSON ({err.msg}). "
            f"Preview: {preview!r}"
        ) from err


def load_event_from_dict(data):
    """
    Construye un Event a partir de un diccionario que sigue el contrato
    de entrada:

        {
          "event_id":        str (requerido),
          "timestamp":       str ISO 8601 (requerido),
          "raw_description": str o dict (requerido),
          "context_rules":   list (opcional)
        }

    :raises ValueError: si falta algún campo requerido.
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Se esperaba dict, se recibió {type(data).__name__}."
        )

    missing = [f for f in REQUIRED_INPUT_FIELDS if f not in data]
    if missing:
        raise ValueError(
            f"Faltan campos requeridos en el evento: {missing}"
        )

    return Event(
        event_id=data["event_id"],
        timestamp=data["timestamp"],
        raw_description=data["raw_description"],
        context_rules=data.get("context_rules"),
    )


def save_event_output(event, path):
    """
    Escribe el JSON final de un Event.

    Usa ensure_ascii=False para que los acentos y la ñ se vean tal cual,
    no como secuencias \\uXXXX. Indentación de 2 espacios para que sea
    legible al inspeccionar resultados de pruebas.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(event.to_output_dict(), f, ensure_ascii=False, indent=2)
