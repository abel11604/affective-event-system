# -*- coding: utf-8 -*-
"""
Cliente para hablar con la API de OpenAI.

Variables que debe contener .env (raíz del proyecto):
    OPENAI_API_KEY    Clave de la API (REQUERIDA)
    OPENAI_MODEL      Modelo a usar (opcional, default: gpt-4o-mini)

Este módulo NO contiene ninguna credencial. Todo se lee desde .env.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2


class OpenAIService:
    """

    Lo usan las fases A (normalización contextual) y C (estimación del impacto
    intrínseco) del pipeline para enviar prompts al LLM y recibir respuestas
    en formato JSON.
    """

    def __init__(self, model=None, temperature=DEFAULT_TEMPERATURE):
        load_dotenv(ENV_PATH)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Falta OPENAI_API_KEY en .env. "
                f"Esperado en: {ENV_PATH}"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.temperature = temperature

    def chat(self, system_prompt, user_prompt, json_mode=False):
        """
        Envía  (system, user) al modelo y devuelve el texto crudo.

        :param system_prompt: instrucción de rol (qué debe hacer el modelo).
        :param user_prompt: contenido a procesar (el evento + reglas, etc.).
        :param json_mode: si True, fuerza al modelo a devolver JSON válido.
                          Importante: cuando json_mode=True, el prompt debe
                          contener la palabra "json" en algún lado o la API
                          de OpenAI lo rechaza.
        :return: contenido de la respuesta como string.
        """
        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
