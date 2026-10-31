"""Contratos públicos que usa la capa de presentación."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

QualityBand = Literal["needs_review", "acceptable", "excellent"]
UiPhase = Literal["idle", "loading", "success", "error"]
ConfidenceLevel = Literal["low", "medium", "high"]
LatencyStatus = Literal["within_target", "above_target"]
ErrorCode = Literal[
    "invalid_input",
    "artifact_unavailable",
    "timeout",
    "prediction_error",
]

# predicción devuelta por nuestro gateway
class PredictionPayload(BaseModel):
    """Salida equivalente a la que producen los módulos de S3/S4."""

    model_config = ConfigDict(extra="forbid")

    quality_band: QualityBand
    confidence: FiniteFloat = Field(ge=0, le=1)
    model_version: str = Field(min_length=1)
    preprocessing_version: str = Field(min_length=1)


# predicción preparada para el usuario. 
# Esta clase presenta un View Model, es decir, un objeto que contiene
# la infromación ya preparada para que la interfaz pueda mostrarla fácilmente.
# Toma la predicción que ya existe y añade información para poder presentarla
@dataclass(frozen=True)
class PredictionView:
    """Datos ya preparados para renderizar en la interfaz."""

    quality_band: QualityBand
    quality_label: str
    confidence: float
    confidence_level: ConfidenceLevel
    confidence_label: str
    confidence_message: str
    latency_ms: float
    latency_status: LatencyStatus
    latency_label: str
    latency_message: str
    model_version: str
    preprocessing_version: str


class UserFacingError(BaseModel):
    """Error estable para la persona y para los contadores."""

    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    title: str
    message: str
    recovery: str
    request_id: str = Field(min_length=1)


@dataclass(frozen=True)
class UiState:
    """Estado observable de una petición."""

    phase: UiPhase
    request_id: str | None = None
    view: PredictionView | None = None
    error: UserFacingError | None = None
