"""Estado de sesión de Streamlit aislado para poder probarlo sin Streamlit."""

from __future__ import annotations

from collections.abc import MutableMapping
from model_ui.contracts import UiState
from model_ui.telemetry import Telemetry

LAST_STATE_KEY = "last_state"
TELEMETRY_KEY = "telemetry"
LAST_VALUES_KEY = "last_values"

# El objetivo de este archivo es gestionar 3 elementos:
# - last_state -> Último estado de la aplicación (idle, loading, success, error)
# - last_values -> Los valores del último formulario enviado (que el usuario no tenga que volver 
#                  a escribir las 11 características si ocurre un fallo temporal en la predicción)
# - telemetry -> Las estadísticas acumuladas durante la sesión

# Idempotente -> Una aplicación es idempotente cuando ejecutarla varias veces
# tiene el mismo efecto final que ejecutarla una sola vez, partiendo del mismo estado.
# En nuestro caso significa que llamar repetidamente a initialize_session_state() no
# debe reiniciar ni sobrescribir los datos que ya existían


# MutableMapping es una clase base abstracta (ABC) que define cómo debe comportarse una 
# estructura de datos que funciona como un diccionario mutable. MutableMapping define una
# interfaz común para cualquier estructura que se comporte como un diccionario mutable.
# Es una notación de tipo que indica que esperamos recibir una estructura pareceida a un
# diccionario, pero que pueda modificarse. 

# object indica que los valores pueden ser objetos de distintos tipos
# La función no devuelve información, modifica el objeto session_state que 
# recibe como argumento.
# Esta función se ejecuta en cada run. Los valores de last_state, telemetry y last_values
# cambian en cada run, no se acumulan
def initialize_session_state(
    session_state: MutableMapping[str, object],
) -> None:
    """TODO: crea solo las entradas de sesión que todavía no existan."""
    # Si todavía no existe last_state (LAST_STATE_KEY) en el diccionario, crea esa entrada 
    # y le asigna un objeto UiState con phase="idle"
    session_state.setdefault(LAST_STATE_KEY, UiState(phase="idle"))
    session_state.setdefault(TELEMETRY_KEY, Telemetry())
    # Si todavía no existe last_values, creamos un diccionario vacío. Si ya existe, conservamos
    # los valores anteriores
    session_state.setdefault(LAST_VALUES_KEY, {})


# Esta función se ejecuta cuando el usuario pulse Limpiar último resultado
def clear_last_state(session_state: MutableMapping[str, object]) -> None:
    """TODO: vuelve a idle sin perder la telemetría acumulada."""
    session_state[LAST_STATE_KEY] = UiState(phase="idle")
    session_state[LAST_VALUES_KEY] = {}
    # Dejamos la telemetría 
    