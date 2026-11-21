from fastapi import APIRouter, HTTPException

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import ErrorResponse, HealthResponse  # noqa: F401 - pista para S9.1d

SERVICE_NAME = "wine-quality-prediction"

# TODO S9.3a: declara `tags=["health"]` en el router, no en include_router().
router = APIRouter(tags=["health"])
# Añadimos la etiqueta health para indicar que todas las operaciones registradas
# en ese router pertenecen a la categoría health


# TODO S9.3b: añade `summary=`, `response_description=` y un docstring que diga
# cuándo usar el endpoint y qué significa un 503. Documenta el 503 con
# `responses={503: {"model": ErrorResponse, "description": ...}}`.
@router.get(
    "/health",
    summary="Consultar el estado del servicio",  # Título breve con el que aparece la operación en Swagger
    response_description="Información del servicio y del predictor disponible",  # Explica qué devuelve la respuesta correcta, normalmente la del estado 200
    responses={  # Sirve para documentar las posibles respuestas HTTP
        503: {
            "model": ErrorResponse,
            "description": "El predictor no está disponible para atender peticiones",
        }
    },
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep) -> HealthResponse:
    """Comprueba si el servicio y el modelo de predicción están preparados.

    Úsalo parea supervisar el estado de la API. Si el predictor no está listo,
    el servidor responde con un error 503 siguiendo el sobre ErrorResponse.
    """

    # TODO S9.2f: sustituye el HTTPException por `ModelUnavailableError`: el
    # dominio no debería saber de HTTP y el manejador produce el sobre común.
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model not ready")
    # TODO S9.1d: declara `-> HealthResponse` y devuelve una instancia.
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "model_status": "ready",
        "model_version": predictor.model_version,
        "request_id": request_id,
    }
