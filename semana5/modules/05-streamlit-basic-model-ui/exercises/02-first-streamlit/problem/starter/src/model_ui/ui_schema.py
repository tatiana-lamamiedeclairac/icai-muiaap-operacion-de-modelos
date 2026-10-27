"""Contrato completo del formulario Wine Quality para la Práctica 5.2."""

from __future__ import annotations

from dataclasses import dataclass

# frozen = True impide reasignar normalmente los atributos de los objetos una vez creados
# slots = True hace que los objetos utilicen una estructura de atributos más restringida, que suele ahorrar memoria
@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Describe cómo representa la UI un campo del contrato de inferencia."""

    name: str
    label: str
    min_value: float
    max_value: float
    default: float
    step: float

# Diferencia entre tupla y lista en Python: Las listas se pueden modificar después de crearlas,
# mientras que las tuplas son inmutables

# Describe cómo debe construirse cada widget, para que no lo tengamos que 
# hacer nosotros uno por uno. 
FIELD_SPECS: tuple[FieldSpec, ...] = (
    FieldSpec(
        name="fixed_acidity",
        label="Acidez fija",
        min_value=0.0,
        max_value=20.0,
        default=7.4,
        step=0.1,
    ),
    FieldSpec(
        name="volatile_acidity",
        label="Acidez volátil",
        min_value=0.0,
        max_value=2.0,
        default=0.7,
        step=0.01,
    ),
    FieldSpec(
        name="citric_acid",
        label="Ácido cítrico",
        min_value=0.0,
        max_value=2.0,
        default=0.0,
        step=0.01,
    ),
    FieldSpec(
        name="residual_sugar",
        label="Azúcar residual",
        min_value=0.0,
        max_value=20.0,
        default=1.9,
        step=0.1,
    ),
    FieldSpec(
        name="chlorides",
        label="Cloruros",
        min_value=0.0,
        max_value=1.0,
        default=0.076,
        step=0.001,
    ),
    FieldSpec(
        name="free_sulfur_dioxide",
        label="Dióxido de azufre libre",
        min_value=0.0,
        max_value=100.0,
        default=11.0,
        step=1.0,
    ),
    FieldSpec(
        name="total_sulfur_dioxide",
        label="Dióxido de azufre total",
        min_value=0.0,
        max_value=300.0,
        default=34.0,
        step=1.0,
    ),
    FieldSpec(
        name="density",
        label="Densidad",
        min_value=0.98,
        max_value=1.01,
        default=0.9978,
        step=0.0001,
    ),
    FieldSpec(
        name="ph",
        label="pH",
        min_value=2.5,
        max_value=4.5,
        default=3.51,
        step=0.01,
    ),
    FieldSpec(
        name="sulphates",
        label="Sulfatos",
        min_value=0.0,
        max_value=3.0,
        default=0.56,
        step=0.01,
    ),
    FieldSpec(
        name="alcohol",
        label="Alcohol",
        min_value=5.0,
        max_value=20.0,
        default=9.4,
        step=0.1,
    ),
)
