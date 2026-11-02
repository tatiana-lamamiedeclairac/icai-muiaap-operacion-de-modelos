from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# CONTRATOS Pydantic


# TODO: clase PrestamoEntrada (BaseModel) con las 6 variables del modelo, con sus rangos (ver enunciado).
#       Debe rechazar campos que no existan.

# Valida la entrada para el modelo
class PrestamoEntrada(BaseModel):

    model_config = ConfigDict(extra="forbid")

    edad: int = Field(ge=18, le=75)
    ingresos_mensuales: float = Field(gt=0)
    importe_prestamo: float = Field(gt=0)
    plazo_meses: int = Field(ge=6, le=84)
    antiguedad_laboral_anios: int = Field(ge=0, le=50)
    impagos_previos: int = Field(ge=0, le=20)

    @field_validator("antiguedad_laboral_anios")
    @classmethod
    def mayor_edad_dieciseis(cls, valor, info):
        edad = info.data.get("edad")
        if edad is not None and valor > edad - 16:
            raise ValueError("La antiguedad laboral no puede ser mayor que edad - 16")

        return valor


# TODO: field_validator (con classmethod) para antiguedad_laboral_anios: no puede ser incoherente con la edad.
# TODO: clase PrediccionSalida con probabilidad_impago (entre 0 y 1) y decision (aprobar, revisar o rechazar).

# Valida la salida para el modelo
class PrediccionSalida(BaseModel):
    probabilidad_impago: float = Field(ge=0, le=1)
    decision: Literal["aprobar", "revisar", "rechazar"]
