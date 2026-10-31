"""TODOs de la vista UX: copy de salida y traducción de errores."""

from __future__ import annotations

from model_ui.contracts import PredictionPayload, PredictionView, UserFacingError
from model_ui.policies import (
    DEFAULT_CONFIDENCE_POLICY,
    DEFAULT_LATENCY_POLICY,
    ConfidencePolicy,
    LatencyPolicy,
)

from model_ui.policies import classify_confidence, classify_latency
from model_ui.errors import InputContractError, ArtifactUnavailableError, InferenceTimeoutError

# Este archivo conecta la información que devuelve el modelo de ML con lo que
# finalmente verá el usuario en la aplicación de Streamlit


QUALITY_LABELS = {
    "needs_review": "Requiere revisión",
    "acceptable": "Resultado aceptable",
    "excellent": "Resultado excelente",
}

CONFIDENCE_COPY = {
    "low": (
        "Confianza baja",
        "El resultado es orientativo y requiere revisión; "
        "la confianza no es una garantía.",
    ),
    "medium": (
        "Confianza intermedia",
        "Usa el resultado como señal orientativa y revisa su contexto antes de actuar.",
    ),
    "high": (
        "Confianza alta",
        "La confianza es alta para este modelo, pero no garantiza "
        "que la decisión sea correcta.",
    ),
}

LATENCY_COPY = {
    "within_target": (
        "Dentro del objetivo",
        "La respuesta quedó dentro del objetivo de la demo.",
    ),
    "above_target": (
        "Por encima del objetivo",
        "La respuesta llegó, pero la latencia supera el objetivo técnico de la demo.",
    ),
}


# El asterico significa que todos los parámetros qye vienen después deben
# pasarse obligatoriamente por nombre, y no por posición
def build_prediction_view(
    prediction: PredictionPayload,
    latency_ms: float,
    *,
    confidence_policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
    latency_policy: LatencyPolicy = DEFAULT_LATENCY_POLICY,
) -> PredictionView:
    
    """TODO: construye la vista con etiquetas, confianza, latencia y versiones."""
    confidence_level = classify_confidence(
        prediction.confidence,
        confidence_policy
    )

    latency_level = classify_latency(
        latency_ms,
        latency_policy
    )

    quality_label = QUALITY_LABELS[prediction.quality_band]

    latency_status = classify_latency(
        latency_ms,
        latency_policy
    )

    # Desempaquetar la tupla CONFIDENCE_COPY
    confidence_label, confidence_message = CONFIDENCE_COPY[confidence_level]

    # Hacemos lo mismo con la latencia
    latency_label, latency_message = LATENCY_COPY[latency_level]

    view = PredictionView(
        quality_band=prediction.quality_band,
        quality_label=quality_label,
        confidence= prediction.confidence,
        confidence_level=confidence_level,
        confidence_label=confidence_label,
        confidence_message=confidence_message,
        latency_ms=latency_ms,
        latency_status=latency_status,
        latency_label=latency_label,
        latency_message=latency_message,
        model_version=prediction.model_version,
        preprocessing_version=prediction.preprocessing_version
    )

    return view


# error -> representa una excepción que ha ocurrido al intentar realizar la inferencia
def to_user_facing_error(error: Exception, request_id: str) -> UserFacingError:
    """TODO: asigna código estable, mensaje accionable y recuperación."""

    
    if isinstance(error, InputContractError):
        code = "invalid_input"
        title = "Datos no válidos"
        message = "La muestra no cumple los requisitos de entrada."
        recovery = "Revisa los campos y vuelve a enviar el formulario."

    elif isinstance(error, ArtifactUnavailableError):
        code = "artifact_unavailable"
        title = "Modelo no disponible"
        message = "El modelo no está disponible en este momento."
        recovery = "Comprueba la disponibilidad del modelo antes de reintentar."

    elif isinstance(error, InferenceTimeoutError):
        code = "timeout"
        title = "Tiempo de espera superado"
        message = "La inferencia no se ha completado a tiempo."
        recovery = "Vuelve a intentar la petición."

    else:
        code = "prediction_error"
        title = "Error en la predicción"
        message = "No se ha podido completar la inferencia."
        recovery = "Inténtalo de nuevo o solicita ayuda si el problema continúa."

    error = UserFacingError(
        code=code,
        title=title,
        message=message,
        recovery=recovery,
        request_id=request_id,
    )

    return error
    
