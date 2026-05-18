# -*- coding: utf-8 -*-


VALENCE_POSITIVE = "POSITIVE"
VALENCE_NEGATIVE = "NEGATIVE"
VALENCE_NEUTRAL = "NEUTRAL"

VALID_VALENCES = (VALENCE_POSITIVE, VALENCE_NEGATIVE, VALENCE_NEUTRAL)

DEFAULT_FAMILIARITY = 1.0
DEFAULT_PERCEPTION = 0.0


class Entity:
    """Sujeto lógico del evento (source o target)."""

    def __init__(self, object_name,
                 familiarity=DEFAULT_FAMILIARITY,
                 perception=DEFAULT_PERCEPTION):
        self.object_name = object_name
        self.familiarity = familiarity
        self.perception = perception

    def to_dict(self):
        return {
            "objectName": self.object_name,
            "familiarity": self.familiarity,
            "perception": self.perception,
        }


class Action:
    """Acción inferida con su valencia cualitativa y grado cuantitativo."""

    def __init__(self, action_name,
                 action_valence=VALENCE_NEUTRAL,
                 action_degree=0.0):
        self.action_name = action_name
        self.action_valence = action_valence
        self.action_degree = action_degree

    def to_dict(self):
        return {
            "actionName": self.action_name,
            "actionValence": self.action_valence,
            "actionDegree": self.action_degree,
        }


class Event:
    """
    Evento que atraviesa el pipeline. Carga los campos del contrato de entrada
    (event_id, timestamp, raw_description, context_rules) y se enriquece con
    source, action y target conforme avanza por los modulos.
    """

    def __init__(self, event_id, timestamp, raw_description, context_rules=None):
        self.event_id = event_id
        self.timestamp = timestamp
        self.raw_description = raw_description
        self.context_rules = context_rules or []

        self.source = None
        self.action = None
        self.target = None

        self.relevant = None

    def to_output_dict(self):
        """
        Devuelve el JSON final tal como lo especifica el paper (Sección 3.4).
        event_id y context_rules NO se incluyen: son metadatos de entrada,
        no parte del contrato de salida.
        """
        return {
            "event": {
                "source": self.source.to_dict() if self.source else None,
                "action": self.action.to_dict() if self.action else None,
                "target": self.target.to_dict() if self.target else None,
                "dateTime": self.timestamp,
            }
        }
