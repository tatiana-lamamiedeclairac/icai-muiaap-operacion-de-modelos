from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

# TODO S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.
# TODO S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.
router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {"model": ErrorResponse, "description": "El cuerpo no es JSON válido"},
        422: {
            "model": ErrorResponse,
            "description": "Los datos no cumplen el contrato",
        },
        503: {"model": ErrorResponse, "description": "El modelo no está disponible"},
    },
)


# Es la función que atiende a una petición de predicción
# La función create prediction le pide al predictor que haga el cálculo
# y prepara la respuesta que recibirá el cliente
@router.post(
    "",
    summary="Predecir la calidad de un vino",
    response_description="Predicción pública, identificador y fecha de respuesta",
)
def create_prediction(
    payload: Annotated[
        PredictionRequest,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Ejemplo válido",
                    "value": {"features": VALID_FEATURES_EXAMPLE},
                },
                "invalid_type": {
                    "summary": "Alcohol como texto (inválido)",
                    "value": {
                        "features": {
                            **VALID_FEATURES_EXAMPLE,
                            "alcohol": "mucho",
                        }
                    },
                },
                "invalid_range": {
                    "summary": "Alcohol fuera del rango (inválido)",
                    "value": {
                        "features": {
                            **VALID_FEATURES_EXAMPLE,
                            "alcohol": 25,
                        }
                    },
                },
            }
        ),
    ],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    """Recibe once características fisicoquímicas de un vino tinto.

    Comprueba sus tipos y rangos, calcula la categoría de calidad
    y devuelve `confidence` con dos decimales junto con las versiones,
    el identificador de la petición y la fecha en UTC.
    """
    # TODO S9.3e: añade summary, response_description y un docstring útil para
    # quien consume la API (campos, rangos, decimales de confidence).
    # TODO S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
    # y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
    # `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.
    output = predictor.predict(
        payload.features
    )  # Le pide al predictor que calcule la calidad
    prediction = Prediction.model_validate(
        output, from_attributes=True
    )  # Construye un objeto Prediction leyendo los atributos de output.

    # TODO S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.
    return PredictionResponse(
        prediction=prediction,
        request_id=request_id,
        served_at=datetime.now(UTC),
    )
