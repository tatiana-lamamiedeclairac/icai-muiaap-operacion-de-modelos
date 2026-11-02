"""Políticas explícitas que el alumnado puede reutilizar en la UI."""

from dataclasses import dataclass

from model_ui.contracts import ConfidenceLevel, LatencyStatus

# Una policy es un conjunto de reglas que determinan cómo debe comportarse nuestra
# aplicación ante determinados valores. 
# En este ejercicio tendremos dos políticas:
# - Política de confianza -> Establece los límites para clasificar una confianza
#       como baja, media o alta
# - Política de latencia -> Establece cuánto puede tardar una operación para
#       considerarse debtro del objetivo técnico


@dataclass(frozen=True)
class ConfidencePolicy:
    """Umbrales de comunicación, no de aprobación del modelo."""

    low_below: float = 0.60
    high_from: float = 0.85


@dataclass(frozen=True)
class LatencyPolicy:
    """Objetivo técnico de la demo."""

    target_ms: float = 300.0

# Objetos con los valores por defecto
DEFAULT_CONFIDENCE_POLICY = ConfidencePolicy()
DEFAULT_LATENCY_POLICY = LatencyPolicy()


def classify_confidence(
    confidence: float, 
    policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY
) -> ConfidenceLevel:
    """TODO: valida [0, 1] y devuelve low/medium/high según policy."""
    
    # Validar que la confianza esté entre 0 y 1
    if not 0 <= confidence <= 1:
        raise ValueError("La confianza debe estar entre 0 y 1")

    if confidence < policy.low_below:
        return "low"

    if confidence >= policy.high_from:
        return "high"

    return "medium"
    

    


def classify_latency(
    latency_ms: float, 
    policy: LatencyPolicy = DEFAULT_LATENCY_POLICY
) -> LatencyStatus:
    """TODO: devuelve within_target o above_target para una latencia válida."""

    if latency_ms > policy.target_ms:
        return "above_target"

    return "within_target"
