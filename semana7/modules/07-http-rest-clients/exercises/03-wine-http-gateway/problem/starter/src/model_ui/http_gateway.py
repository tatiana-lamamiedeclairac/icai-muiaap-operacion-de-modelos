"""Cliente HTTP que adapta la API Wine al contrato de inferencia de la UI."""

from __future__ import annotations

from collections.abc import Mapping
from threading import local
from typing import Any

import requests
from pydantic import ValidationError  # noqa: F401 - pista para el TODO S7.4

from model_ui.contracts import PredictionPayload
from model_ui.errors import (  # noqa: F401 - pistas para el TODO S7.2
    ArtifactUnavailableError,
    BackendInferenceError,
    InferenceTimeoutError,
    InputContractError,
)

from model_ui.errors import InferenceTimeoutError, ArtifactUnavailableError, BackendInferenceError, InputContractError

# Esta clase es el gatewat HTTP. Un gateway es una capa intermedia
# que permite a nuestra aplicación comunicarse con otro componente.
# El gateway recibirá las características de un vino, enviará una 
# petición HTTP a la API del profesir y devolverá una predicción.
class HttpInferenceGateway:
    """Implementa la frontera de inferencia mediante una llamada HTTP REST."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        session: Any | None = None,
    ) -> None:
        normalized = base_url.strip().rstrip("/")
        if not normalized:
            raise ValueError("base_url no puede estar vacia")
        if timeout <= 0:
            raise ValueError("timeout debe ser positivo")

        # self hace referencia al objeto concreto que estamos creando o utilizando
        # self._prediction_url es una variable del objeto donde guardamos la URL
        # completa del endpoint
        self._prediction_url = f"{normalized}/v1/predictions"
        self._timeout = float(timeout)
        # La librería requests puede crear objeos de tipo Session. Una sesión
        # proporciona métodos como: session.get() o session.post(). Es decir, 
        # podemos realizar peticiones HTTP a través de ese objeto
        self._session = session if session is not None else requests.Session()
        self._request_context = local()
        self.last_request_id: str | None = None

    @property
    def last_request_id(self) -> str | None:
        """Devuelve el identificador de la ultima llamada en el contexto actual."""

        return getattr(self._request_context, "request_id", None)

    @last_request_id.setter
    def last_request_id(self, value: str | None) -> None:
        self._request_context.request_id = value

    # values contiene las características del vino
    # Mapping[str, object] indica que recibimos una estructura de pares
    # clave-valor, parecida a un diccionario
    def predict(self, values: Mapping[str, object]) -> PredictionPayload:
        """Envia la muestra por HTTP y devuelve el contrato interno de S6."""

        # TODO S7.1: envia POST a self._prediction_url con json={"features": ...},
        # Accept application/json y self._timeout. Compruebalo con el test de llamada.
        self.last_request_id = None
        try:
            response = self._session.post(
                self._prediction_url,
                json={"features": dict(values)},
                headers= {"Accept": "application/json"},
                timeout= self._timeout
            )

        # Traducir errores significa capturar una excepción de una librería externa
        # y generar otra excepción que nuestra aplicación entiende. La aplicación de 
        # Streamlit envía una petición a la API para obtener la calidad de un vino. 
        # Pueden producirse varios problemas (servidor apagado o tarda mucho en responder).
        # Cuando ocurren estos problemas, la librería requests genera excepciones propias.
        # Pero nuestro PredictionController no está diseñado para trabajar directamente
        # con los errores de requests. En su lugar, conoce los errores que el profesor ya ha
        # definido en errors.py. Entonces tenemos que capturar la excepción de la librería requests
        # y generar otra excepción que nuestra librería entienda
        # TODO S7.2: traduce Timeout, ConnectionError y RequestException a los
        # errores de dominio que ya entiende PredictionController.
        except requests.Timeout as error:
            raise InferenceTimeoutError(
                "La API ha tardado demasiado en responder"
            ) from error

        except requests.ConnectionError as error:
            raise ArtifactUnavailableError(
                "No se pudo conectar con la api"
            ) from error

        except requests.RequestException as error:
            raise BackendInferenceError(
                "Error al realizar la petición HTTP"
            ) from error
        


        # TODO S7.3: lee un objeto JSON, conserva request_id y diferencia 422/503
        # del resto de errores HTTP.
        self.last_request_id = self._header_request_id(response)

        if response.status_code == 422:
            raise InputContractError(
                "La API ha rechazado los datos de entrada"
            )

        if response.status_code == 503:
            raise ArtifactUnavailableError(
                "La API no está disponible"
            )

        if not 200 <= response.status_code < 300:
            raise BackendInferenceError(
                f"Error HTTP {response.status_code}"
            )

        # TODO S7.4: valida body["prediction"] como PredictionPayload; un dict sin
        # validar no satisface el contrato de salida.
        body = self._read_object(response)
        # Guarda el identificador remoto de la petición
        self.last_request_id = self._request_id(response, body) 
        # Validar la predicción
        try:
            # Los asteriscos desempaquetan el diccionario y pasan sus elementos
            # como argumentos al constructor
            return PredictionPayload(**body["prediction"])

        except (KeyError, ValidationError) as error:
            raise BackendInferenceError(
                "La predicción no cumple el contrato."
            ) from error

        

    # Leer los datos que contiene la respuesta API
    @staticmethod
    def _read_object(response: Any) -> dict[str, Any]:
        """Lee una respuesta JSON que debe representar un objeto."""

        # TODO S7.3: usa response.json(), traduce ValueError y rechaza listas u
        # otros valores que no sean un objeto JSON.
        try:
            body = response.json()

        except ValueError as error:
            raise BackendInferenceError(
                "La respuesta no contiene un JSON válido"
            ) from error

        if not isinstance(body, dict):
            raise BackendInferenceError(
                "La respuesta JSON no es un objeto"
            )

        return body
        


    
    @staticmethod
    def _request_id(response: Any, body: dict[str, Any]) -> str | None:
        """Obtiene request_id del cuerpo y usa la cabecera como alternativa."""

        # TODO S7.3: prioriza body["request_id"] y usa X-Request-Id como fallback.
        # Usamos .get en vez de body["request_id"] porque, si no existe la clave 
        # request_id, devuelve None en lugar de generar un KeyError
        request_id = body.get("request_id")

        if isinstance(request_id, str) and request_id:
            return request_id

        # Si no cumple las condiciones del if, llamamos a otro método de la clase
        # Este método busca el identificador en la cabecera X-Request-Id
        return HttpInferenceGateway._header_request_id(response)


    @staticmethod
    def _header_request_id(response: Any) -> str | None:
        headers = getattr(response, "headers", {})
        return headers.get("X-Request-Id")
