"""Starter: conecta una función de inferencia pura con Streamlit."""

from collections.abc import Callable
from typing import Any

from churn_demo.model import ChurnPrediction, predict

# Callable significa que un objeto se puede llamar como una función
# Callable[..., ChurnPrediction] indica que esperamos algo que pueda recibir
# argumentos y devolver un resultado del tipo ChurnPrediction. En esta aplicación,
# ese predictor será la funición predict() de model.py
# Los puntos suspensivos significan que aquí no se detallan los tipos concretos
# de sus argumentos
Predictor = Callable[..., ChurnPrediction]

# Construir el formulario de entrada. Necesitamos que el usuario pueda introducir
# los cuatro datos del cliente y enviarlos pulsando un botón.
# Un widget es un elemento interactivo de una interfaz gráfica. Por ejemplo:
#    - st.slider() -> crea un control deslizante
#    - st.number_input() -> crea una entrada numérica
#    - st.checkbox() -> crea una casilla que se puede marcar o desmarcar 
#    - st.from_submit_button() -> crea el botón que envía el formulario
# st es el parámetro que utulizaremos para acceder a las funcionalidades de streamlit
# Any indica que no estamos restringiendo ese parámetro a un tipo concreto mediante la anotación
# La función devuelve un booleano que indique si se ha pulsado el botón y un diccionario
# con las 4 variables del cliente
# Streamlit funciona de manera diferente a un programa tradicional de python: Cuando el 
# usuario interactúa con determinados widgets, Streamlit puede volver a ejecutar el script.
# Si tenemos 4 entradas y cambiamos sus valores de manera independiente, no queremos que se
# ejecute el modelo cada vez que cambiamos una de ellas. Por eso utilizamos: with st.form("churn_form")
# st.form() crea un formulario. 
# "churn_form" es el identificador del formulario. Los tests esperan exactamente ese nombre.
# Cuando los widgets están dentro de ese formulario, sus campos se agrupan y se envían al pulsar el 
# botón correspondiente
def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:
    """Renderiza cuatro widgets dentro de un único formulario."""
    # TODO 1 (alumno): usa st.form("churn_form"), los cuatro widgets con las
    # claves indicadas en el README y st.form_submit_button. El formulario evita
    # inferencias durante cada edición. Compruébalo con el primer test de app.
    
    # st.form crea un formulario en nuestra aplicación web. Un formulario es un conjunto de campos
    # donde el usuario puede introducir información antes de enviarla
    # with es para que todo lo que esté dentro del with vaya dentro del formulario,
    # y lo que vaya fuera del with no. 
    with st.form("churn_form"):
    
        tenure_months = st.slider( # guardamos en la variable tenure_months el valor que devuelve el widget
            "Antiguedad del cliente (meses)", # texto que verá el usuario junto al widget
            min_value=0,
            max_value=120,
            value=12, # indica el valor inicial
            key="tenure_months" # proporciona un identificador al widget
        )

        monthly_spend_eur = st.number_input(
            "Gasto mensual",
            min_value=0,
            max_value=300,
            value=60,
            key="monthly_spend_eur"
        )

        suppor_calls = st.slider(
            "Número de llamadas a soporte",
            min_value=0,
            max_value=20,
            value=1,
            key="support_calls"
        )

        has_annual_contract = st.checkbox(
            "Contrato anual",
            value = False,
            key="has_annual_contract"
        )

        # Crea el botón Calcular riesgo y devuleve un booleano. En la ejecución
        # correspondiente al envío del formulario, submitted será True. Cuando no
        # se haya enviado, será False. Así podemos decidir posteriormente si debemos
        # llamar a predict()
        submitted = st.form_submit_button("Calcular riesgo")

    values = {
        "tenure_months": tenure_months,
        "monthly_spend_eur": monthly_spend_eur,
        "support_calls": suppor_calls,
        "has_annual_contract": has_annual_contract
    }

    # El orden del return importa!!! No podemos hacer: return values, submitted
    # Mirar al principio de la función lo que pone que devuelve
    return submitted, values



# Mostrar el resultado de la predicción
def render_prediction(st: Any, result: ChurnPrediction) -> None:
    """Muestra etiqueta, score orientativo y explicación."""
    # TODO 3 (alumno): presenta label, risk_score y explanation con componentes
    # Streamlit. No recalcules el score. Compruébalo con el test de presentación.
    
    if result["will_churn"]: # will_churn es un booleano
        st.warning(result["label"]) # st.warning muestra un mensaje de advertencia
    else:
        st.success(result["label"]) # st.success muestra un mensaje de éxito

    st.metric("Score de riesgo", f"{result['risk_score']:.2f}") # st.metric() sirve para mostrar una etiqueta de forma destacada en Streamlit

    st.write(result["explanation"])



# Esta función:
# - Recoge los valores introducidos en el formulario
# - Comprueba si el usuario ha pulsado Calcular riesgo
# - Si no ha pulsado el botón, no ejecuta ninguna predicción
# - Muestra el resultado o un mensaje de error
def run_app(st: Any, predictor: Predictor) -> None:
    """Conecta submit, llamada al predictor y actualización visible."""
    # TODO 2 (alumno): llama a collect_profile, ejecuta predictor(**values) solo
    # tras el submit y una única vez; convierte ValueError en un mensaje seguro.
    # Los tests de 0/1 llamadas y de error verifican este contrato.

    submitted, values = collect_profile(st)

    # Comprobar si el usuario ha pulsado el botón
    if not submitted:
        st.info("Introduce los datos y pulsa Calcular riesgo") # Muestra un mensaje informativo dentro de la aplicación de Streamlit
        return # Termina la ejecución de la función

    # Si tenemos este diccionario:
    # values{
    #   tenure_months=12,
    #   monthly_spend_eur=60.0,
    #   support_calls=1,
    #   has_annual_contract=False,
    # }
    # Al hacer (**values) -> Python desempaqueta el diccionario y utiliza sus claves como nombres de los
    # argumentos. Es quivalente a escribir:
    # predictor(
    #   tenure_months=12,
    #   monthly_spend_eur=60.0,
    #   support_calls=1,
    #   has_annual_contract=False,
    # )
    try:        # predictor es la función predict() de model.py, esto viene de la función main (mirar final del archivo)
        result = predictor(**values) # Esto funciona porque las claves del diccionario coinciden exactamente con los nombres de los parámetros de predict()
    except ValueError:
        st.error("No se pudo calcular el riesgo. Revisa los datos introducidos")
        return

    render_prediction(st, result)
    


def main() -> None:
    """Configura la página real y delega el flujo comprobable en run_app."""
    import streamlit as st

    st.set_page_config(page_title="Churn sintético · S5", page_icon="📉")
    st.title("¿Qué cliente podría darse de baja?")
    st.caption("Caso docente sintético; el score no es una probabilidad calibrada.")
    run_app(st, predict) # Indica que el objeto Predictor va a ser la función predict() de model.py


if __name__ == "__main__":
    main()