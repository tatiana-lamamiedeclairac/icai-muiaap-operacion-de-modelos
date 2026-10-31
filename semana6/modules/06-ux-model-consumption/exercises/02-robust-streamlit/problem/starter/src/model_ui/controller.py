"""TODOs del controlador de estados independiente de Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import perf_counter
from uuid import uuid4

from model_ui.contracts import UiState, PredictionPayload
from model_ui.gateway import InferenceGateway
from model_ui.telemetry import Telemetry

from model_ui.presentation import (
    build_prediction_view,
    to_user_facing_error,
)

# StateEmitter representa una función que recibe un objeto UiState y no devuelve ningún valor
StateEmitter = Callable[[UiState], None]
Clock = Callable[[], float]
RequestIdFactory = Callable[[], str]

# El controlador es el que se encarga de coordinar toda la operación desde que
# el usuario introduce las características y pulsa Ejecutar inferencia

# Las responsabilidades del controlador son:
# - Generar un identificador para la petición (request_id).
# - Avisar de que la inferencia está comenzando (loading).
# - Llamar al gateway para obtener la predicción.
# - Medir cuánto tarda en responder.
# - Si todo va bien, preparar el resultado y registrar el éxito.
# - Si algo falla, traducir el error y registrarlo.
# - Devolver el estado final (success o error).

# Callable sirve para pasar funciones como argumentos a otras funciones
# saludar -> hace referencia a una función, sin ejecutarla
# saludar() -> ejecuta la función

class PredictionController:
    """Orquesta loading, gateway, errores y telemetría."""

    # __init__ se ejecuta cuando creamos un objeto de esa clase
    def __init__(
        self,
        gateway: InferenceGateway, # Representa el objeto que utilizará el controlador para solicitar predicciones
        *,
        telemetry: Telemetry | None = None,
        clock: Clock = perf_counter,
        request_id_factory: RequestIdFactory | None = None,
    ) -> None:
        self.gateway = gateway
        self.telemetry = telemetry or Telemetry()
        self._clock = clock
        self._request_id_factory = request_id_factory or (lambda: uuid4().hex[:10])


    # Esta función es la que ejecutaremos cada vez que el usuario solicite una predicción
    def submit(
        self,
        values: Mapping[str, object],
        *,
        emit: StateEmitter | None = None, # Permite proporcionar una función que recibirá los cambios de estado
    ) -> UiState:
        """TODO: emite loading, mide, valida la salida y devuelve success/error."""

        request_id = self._request_id_factory()

        # Creamos el estado inicial de la petición
        loading = UiState(
            phase="loading",
            request_id=request_id
        )

        if emit is not None:
            emit(loading)

        start = self._clock()

        try:
            prediction = PredictionPayload.model_validate(
                self.gateway.predict(values)
            )

        except Exception as error:
            latency_ms = round((self._clock() - start) * 1000, 3)

            user_error = to_user_facing_error(error, request_id)

            self.telemetry.record_error(user_error.code, latency_ms)

            state = UiState(
                phase="error",
                request_id=request_id,
                error=user_error,
            )

        else:
            latency_ms = round((self._clock() - start) * 1000, 3)

            view = build_prediction_view(prediction, latency_ms)

            self.telemetry.record_success(
                latency_ms,
                model_version=prediction.model_version,
                preprocessing_version=prediction.preprocessing_version,
            )

            state = UiState(
                phase="success",
                request_id=request_id,
                view=view,
            )

        if emit is not None:
            emit(state)

        return state
        
