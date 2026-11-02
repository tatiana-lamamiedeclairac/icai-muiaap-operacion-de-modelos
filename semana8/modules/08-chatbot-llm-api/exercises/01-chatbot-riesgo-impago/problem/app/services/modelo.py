import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada

# ESTE ARCHIVO CARGA EL MODELO Y HACE PREDICCIONES


# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# Tenemos dos contratos: PrestamoEntrada -> Valida la entrada para el modelo
# PrediccionSalida -> Valida la salida para el modelo


# TODO: cargar el modelo joblib una sola vez, al importar el modulo
modelo = joblib.load(MODEL_PATH)

# TODO: funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
def decidir(probabilidad):
    if probabilidad < 0.2:
        return "aprobar"

    if probabilidad < 0.5:
        return "revisar"

    else:
        return "rechazar"

# TODO: funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores
def predecir(entrada: PrestamoEntrada) -> PrediccionSalida:
    # Convertir el objeto Pydantic en un diccionario
    datos = entrada.model_dump() 
    
    # Organizar los valores
    # Recorre la lista VARIABLES y obtiene del diccionario el valor
    # correspondiente a cada nombre. El resultado podría ser: valores = [30, 2500, 12000, 36, 5, 0]
    valores = [datos[variable] for variable in VARIABLES]

    # Calcular probabilidad de impago
    probabilidad = modelo.predict_proba([valores])[0][1]

    decision = decidir(probabilidad)

    return PrediccionSalida(
        probabilidad_impago = probabilidad,
        decision = decision
    )
