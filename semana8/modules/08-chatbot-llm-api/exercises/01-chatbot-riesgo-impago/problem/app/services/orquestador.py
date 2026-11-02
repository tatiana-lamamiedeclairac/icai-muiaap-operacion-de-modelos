import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
# MAX_VUELTAS establece el número máximo de veces que podemos consultar al LLM
# dentro de una ejecución del orquestador
MAX_VUELTAS = 4

# Texto de instrucciones que enviaremos al LLM para indicarle cómo debe
# comportarse
SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)

# ESTE ARCHIVO SIRVE PARA CONECTAR EL LLM CON NUESTRO MODELO DE MACHINE LEARNING
# El orquestador se encarga de coordinar al LLM y a nuestro modelo de predicción


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
# Esta función no realiza predicciones. Su finalidad es decirle al LLM qué
# herramienta puede utilizar y cómo debe solicitarla
# La herramienta se describe mediante un diccionario Python. Por ejemplo:
#{
#    "type": "function",
#    "function": {
#        "name": "calcular_riesgo_impago",
#        "description": "Calcula el riesgo de impago de un préstamo",
#        "parameters": ...
#    }
#}

# model_json_schema() -> Es un método de Pydantic que
# genera automáticamente un diccionario que describe la estructura de nuestro
# contrato siguiendo el formato JSON Schema. Describe el contrato, pero
# no valida por sí mismo los argumentos cuando se ejecuta una herramienta. 
# Esa validación la haremos después con Pydantic en ejecutar_tool()
def definir_tool():
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": "Calcula el riesgo de impacto de un préstamo",
            "parameters": PrestamoEntrada.model_json_schema()
        }
    }


# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
# nombre -> indica qué herramienta quiere utilizar el LLM. Por ejemplo: "calcular_riesgo_impago"
# argumentos_json -> Contiene los argumentos de esa herramienta en una cadena de texto
# con formato JSON (ej: '{"edad": 30, "ingresos_mensuales": 2500, "importe_prestamo": 12000, "plazo_meses": 36, "antiguedad_laboral_anios": 5, "impagos_previos": 0}')
def ejecutar_tool(nombre, argumentos_json) -> dict:
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": "Herramienta desconodida"}

    # Validar los argumentos con Pydantic
    argumentos = leer_argumentos(argumentos_json)

    # Crear contrato
    try:
        entrada = PrestamoEntrada(**argumentos) # ** para pasar de diccionario a entrada de objeto Pydantic

    except ValidationError as error:
        return {"ok": False, "error": str(error)}

    # Ejecutar el modelo
    # Si Pydantic acepta los datos, podemos llamar a la función de predecir
    prediccion = predecir(entrada)

    return {
        "ok": True,
        "probabilidad_impago": prediccion.probabilidad_impago,
        "decision": prediccion.decision
    }


# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)
# llm -> es el objeto que utilizaremos para consultar al modelo de lenguaje
# mensajes -> es una lista de objetos Mensaje de nuestro contrato Pydantic

def responder(mensajes, llm) -> ChatSalida:
    # Preparar el historial. Crear una lista que incluya el mensaje
    # de sistema y la conversación recibida
    historial = [{"role": "system", "content": SISTEMA}]

    for mensaje in mensajes:
        # Usamos model_dump() poruqe mensajes contiene objetos Pydantic y llm.completar()
        # trabaja con diccionarios
        historial.append(mensaje.model_dump())

    # Indicamos la LLM qué herramientas puede utilizar
    # Hacemos una lista porque completar() espera recibir una lista de 
    # herramientas
    herramientas = [definir_tool()]
    herramienta_usada = None

    # Consultar al LLM
    for _ in range(MAX_VUELTAS):

        respuesta = llm.completar(historial, herramientas)
        historial.append(respuesta)

        if not respuesta.get("tool_calls"):
            return ChatSalida(
                respuesta=respuesta.get("content") or "No se ha generado respuesta.",
                herramienta=herramienta_usada
            )

        for llamada in respuesta["tool_calls"]:

            nombre = llamada["function"]["name"]
            argumentos_json = llamada["function"]["arguments"]

            resultado = ejecutar_tool(nombre, argumentos_json)

            herramienta_usada = HerramientaUsada(
                nombre=nombre,
                argumentos=leer_argumentos(argumentos_json),
                resultado=resultado
            )

            historial.append({
                "role": "tool",
                "tool_call_id": llamada["id"],
                "content": json.dumps(resultado)
            })

    return ChatSalida(
        respuesta="No he podido completar la solicitud. Inténtalo de nuevo.",
        herramienta=herramienta_usada
    )
