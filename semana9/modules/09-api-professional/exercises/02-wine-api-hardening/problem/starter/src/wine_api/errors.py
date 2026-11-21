"""Errores de dominio y su traducción a un único sobre HTTP."""

import logging
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from wine_api.request_id import REQUEST_ID_HEADER, current_request_id
from wine_api.schemas import ErrorCode, ErrorDetail, ErrorResponse, FieldError

logger = logging.getLogger("wine_api")

HTTP_ERROR_CODES = {
    404: (ErrorCode.NOT_FOUND, "The requested resource does not exist"),
    405: (ErrorCode.METHOD_NOT_ALLOWED, "Method not allowed for this resource"),
}


class WineApiError(Exception):
    """Base de los errores que la API sabe explicar al consumidor."""

    status_code = 500
    code = ErrorCode.INTERNAL_ERROR
    message = "Unexpected server error"


class ModelUnavailableError(WineApiError):
    status_code = 503
    code = ErrorCode.MODEL_UNAVAILABLE
    message = "The prediction model is not ready"


def error_response(
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    fields: list[FieldError] | None = None,
) -> JSONResponse:
    """Construye el sobre de error; `fields` desaparece si no aplica."""

    request_id = current_request_id(request)
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, fields=fields),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", exclude_none=True),
        headers={REQUEST_ID_HEADER: request_id},
    )


def field_path(loc: Sequence[Any]) -> str:
    """Convierte `("body", "features", "alcohol")` en `features.alcohol`."""

    parts = [str(part) for part in loc if part != "body"]
    return ".".join(parts) or "body"


# ESTAS FUNCIONES ASYNC DEVUELVEN EL ERROR QUE EL USUARIO VA A VER
# request es un parámetro de tipo Request, que contiene la petición HTTP
# exc es una parámetro de tipo RequestValidationError, que contiene información sobre el error de validación
async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # TODO S9.2a: FastAPI responde 422 con {"detail": [...]}, que no es nuestro
    # contrato. Recorre `exc.errors()`: cada error trae `type`, `loc` y `msg`.
    # - Si algún `type` es "json_invalid", el cuerpo no es JSON: 400 con
    #   `ErrorCode.INVALID_JSON` y sin `fields`.
    # - Si no, 422 con `ErrorCode.VALIDATION_ERROR` y una lista de FieldError
    #   (usa `field_path`). Nunca copies `input`: puede contener datos del
    #   usuario. Comprobación: tests/test_s9_2_errors.py
    errors = exc.errors()

    if any(error["type"] == "json_invalid" for error in errors):
        return error_response(
            request, 400, ErrorCode.INVALID_JSON, "The request body is not valid JSON"
        )

    # FieldError es un contrato Pydantic
    fields = [
        FieldError(
            field=field_path(error["loc"]),
            message=error["msg"],
        )
        for error in errors
    ]

    # Construye la respuesta HTTP
    return error_response(
        request,
        422,
        ErrorCode.VALIDATION_ERROR,
        "The request contains invalid fields",
        fields=fields,
    )


async def handle_api_error(request: Request, exc: WineApiError) -> JSONResponse:
    # TODO S9.2b: traduce cualquier WineApiError usando los atributos de clase
    # `status_code`, `code` y `message`. Una línea con `error_response`.

    return error_response(request, exc.status_code, exc.code, exc.message)


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # TODO S9.2c: 404 y 405 los genera Starlette, no tus rutas. Busca el código
    # en HTTP_ERROR_CODES (ErrorCode.HTTP_ERROR si no está) y responde con el
    # mismo sobre. ¿Por qué se registra la clase de Starlette y no la de FastAPI?
    code, message = HTTP_ERROR_CODES.get(
        exc.status_code, (ErrorCode.HTTP_ERROR, "HTTP request failed")
    )
    return error_response(request, exc.status_code, code, message)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # TODO S9.2d: último recurso. Registra el detalle con `logger.exception`
    # (incluye el request_id) y devuelve 500 `internal_error` con un mensaje
    # genérico. El texto de `exc` nunca sale en la respuesta.
    request_id = current_request_id(request)
    logger.exception("Unexpected server error. request_id=%s", request_id, exc_info=exc)
    return error_response(
        request, 500, ErrorCode.INTERNAL_ERROR, "Unexpected server error"
    )


def install_error_handlers(app: FastAPI) -> None:
    # TODO S9.2e: registra los cuatro manejadores con `app.add_exception_handler`
    # cuando estén implementados. Hasta entonces la API usa los errores por
    # defecto de FastAPI ({"detail": ...}), que es justo lo que queremos cambiar.

    # Le dice a FastAPI que cuando se produce una excepción de tipo RequestValidationError,
    # ejecute la función handle_validation_error()
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(WineApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
