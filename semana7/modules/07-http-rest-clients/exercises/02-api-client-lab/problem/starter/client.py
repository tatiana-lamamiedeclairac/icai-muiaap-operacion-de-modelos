"""Starter del cliente HTTP. Completa los TODO sin modificar la API."""

from __future__ import annotations

from typing import Any

# El TODO de la práctica usará este cliente para realizar la petición HTTP.
import requests  # noqa: F401


class PredictionClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


# Envía mediciones de una bomba a la API y recibe una predicción
def request_prediction(
    payload: dict[str, Any], # conjunto de datos que enviaremos al servidor
    *,
    base_url: str = "http://127.0.0.1:8000",
    timeout: float = 5.0,
    session: Any | None = None, # Objeto que utilizaremos para realizar la petición HTTP
) -> dict[str, Any]:
    """Envía una predicción y devuelve un objeto JSON de respuesta."""
    # TODO 3: selecciona `session` o `requests` y envía POST con `json=`,
    # `Accept` y `timeout`. Comprueba los argumentos con test_client.py.
    cliente = session if session is not None else requests
    url = base_url.rstrip("/") + "/v1/perdictions" # rstrip() elimina las barras laterales que pudiera tener la dirección base, avitando construir una URL con dos barras

    try: 
        response = cliente.post(
            url, 
            json = payload,
            headers = {"Accept": "application/json"},
            timeout=timeout
        )

    # TODO 4: llama a `raise_for_status()` y conserva el status de HTTPError.
    # raise_for_status() comprueba el código HTTP. Si indica un error del cliente
    # o del servidor (4xx o 5xx), genera una excepción requests.HTTPError
        response.raise_for_status()

    # TODO 5: traduce Timeout y ConnectionError a PredictionClientError.


    # TODO 6: convierte la respuesta con `.json()` y exige un diccionario.
        datos = response.json() # interpreta el body de la respuesta como json y lo convierte en un diccionario de Python

    except requests.Timeout as error:
        raise PredictionClientError(
            "Se agotó el tiempo de espera."
        ) from error

    except requests.ConnectionError as error:
        raise PredictionClientError(
            "No se pudo conectar con el servidor."
        ) from error

    except requests.HTTPError as error:
        codigo = error.response.status_code if error.response is not None else None

        raise PredictionClientError(
            f"Error HTTP {codigo}",
            status_code=codigo,
        ) from error

    except ValueError as error:
        raise PredictionClientError(
            "La respuesta no contiene un JSON válido."
        ) from error

    except requests.RequestException as error:
        raise PredictionClientError(
            "Error en la petición HTTP."
        ) from error
    
    if not isinstance(datos, dict):
        raise PredictionClientError(
            "La respuesta JSON no es un objeto"
        )

    return datos
