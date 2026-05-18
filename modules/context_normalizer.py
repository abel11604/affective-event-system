# -*- coding: utf-8 -*-
"""
Fase A: Normalización Contextual.

Recibe el evento crudo y consulta al LLM para extraer los sujetos lógicos
del evento (source, target, actionName). El LLM opera EXCLUSIVAMENTE como
analizador sintáctico-semántico.

"""

import json

from services.openai_service import OpenAIService
from utils.json_utils import parse_llm_json


_SYSTEM_PROMPT = """Eres un analizador sintáctico-semántico de eventos. Tu única tarea es leer la descripción de un evento y extraer tres elementos lógicos en formato JSON:

  - "source":     el agente o entidad que ejecuta la acción (string o null).
  - "target":     la entidad afectada por la acción (string o null).
  - "actionName": un identificador corto, en snake_case, que nombre la acción (string o null).

NO interpretes el impacto emocional, valencia ni magnitud — eso lo hará otra etapa del sistema. Tu trabajo es PURAMENTE estructural.

Reglas:
1. Devuelve EXCLUSIVAMENTE un objeto JSON con las tres llaves indicadas.
2. Si alguno de los tres elementos no puede deducirse con claridad de la descripción, devuelve null en su valor. NO inventes información.
3. Si se proporcionan reglas contextuales, úsalas para desambiguar nombres de actores o acciones.
4. "actionName" debe ser un verbo o frase verbal en snake_case (ejemplos: "reprobar_examen", "ayudar_al_usuario").
"""


def normalize_context(event, llm_service=None):
    """
    Ejecuta la Fase A sobre un Event.

    :param event: instancia de models.event_model.Event con raw_description
                  (string o dict) y opcionalmente context_rules (list).
    :param llm_service: instancia compartida de OpenAIService. Si es None,
                        se crea una nueva.
    :return: dict con llaves "source", "target", "actionName". Los valores
             pueden ser strings o None. El parseo lo hace utils.json_utils.
    """
    if llm_service is None:
        llm_service = OpenAIService()

    user_prompt = _build_user_prompt(event)
    raw_response = llm_service.chat(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_mode=True,
    )
    return parse_llm_json(raw_response)


def _build_user_prompt(event):
    """
    Construye el mensaje 'user' inyectando la descripción del evento y sus
    reglas contextuales. si es un dict, lo serializa como JSON; si es string, lo usa tal cual.
    """
    raw = event.raw_description
    if isinstance(raw, dict):
        raw_text = json.dumps(raw, ensure_ascii=False)
    else:
        raw_text = str(raw)

    if event.context_rules:
        rules_text = "\n".join(f"- {r}" for r in event.context_rules)
    else:
        rules_text = "(ninguna)"

    return (
        f"Descripción del evento:\n{raw_text}\n\n"
        f"Reglas contextuales:\n{rules_text}"
    )
