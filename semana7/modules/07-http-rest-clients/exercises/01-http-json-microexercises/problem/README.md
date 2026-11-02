# Microejercicios — HTTP, JSON y diseño de recursos

Trabajad por parejas. No hace falta levantar ningún servicio. En el ejercicio 3
sí haréis una comprobación breve con `json.loads()` o un validador local.
Conservad las decisiones: se reutilizarán en el laboratorio de clientes.

## 1. Tres formas de pedir una predicción

Comparad estos tres casos:

A. `infer_measurements(payload)` dentro del mismo programa Python.
B. Un cliente envía `POST /runPumpModel` a otro proceso mediante HTTP.
C. Un cliente envía `POST /v1/predictions` a otro proceso mediante HTTP.

Completad la tabla:

Un proceso es un programa en ejecución. En A todo ocurre en el mismo proceso;
en B y C, el cliente se comunica con el proceso servidor.

| Caso | ¿Sale del proceso Python? | ¿Usa HTTP? | ¿La ruta nombra una acción o un recurso? |
| --- | --- | --- | --- |
| A | No | No | Función/acción |
| B | Sí | Sí | Una acción, porque runPumpModel significa ejecutar el modelo |
| C | Sí | Sí | Un recurso |



## 2. URL, path y query

```text
http://127.0.0.1:8000/v1/predictions/pred-42?include=explanation&limit=1
```

**TODO:** marcad scheme, host, port, path y cada parámetro de query. Después
decidid dónde pondríais:

- el identificador de una predicción concreta; -> en el path
- un límite de resultados; -> en el query
- cuatro medidas de una bomba. -> en el body de la petición

scheme -> http
host -> 127.0.0.1
port -> 8000
path -> predictions/pred-42
parámetros query -> include=explanation, 
                  limit=1





**Comprobación:** las medidas estructuradas no deberían acabar en la URL.

## 3. JSON y Python

```python
{"machine_id": "pump-017", "ready": True, "comment": None, "axes": (1, 2)}
```

**TODO:** convertid esta expresión Python a JSON interoperable. Investigad las
formas JSON de booleano, nulo y colección. Comprobad el resultado con un
validador local o `json.loads()`.

 - json.dumps() -> transforma un objeto Python en una cadena de texto JSON
 - json.loads() -> transforma una cadena de texti JSON en un objeto Python

## 4. Cuatro estados HTTP esenciales

Para cada caso, elegid solo entre `200`, `400`, `422` y `503`. Escribid el
código y una razón de una frase.

1. Predicción correcta y devuelta: código  200 ; razón: La petición se ha procesado correctamente.
2. Texto truncado o que no es JSON: código 400; razón: La petición está mal formada.
3. JSON válido, pero `vibration_mm_s` es la cadena `"alta"`: código 422;
   razón: Los datos no cumplen con el formato esperado.
4. Petición correcta, pero el modelo no está disponible temporalmente: código
   503; razón: El servicio no puede atender la petición.

## 5. Crear y consultar una predicción

Completad estas plantillas:

```text
Crear una predicción:    POST /v1/prediction
Consultar la predicción: GET /v1/prediction/pred-42
```

¿Dónde van las mediciones: en el path, en la query o en el body JSON? En el body ¿Dónde va
`pred-42`? En la url ¿Qué podría pasar si se repite dos veces la creación? Que se crearían predicciones duplicadas ¿Consultar dos
veces debería cambiar el estado del servidor? No, no debería.

- **segura:** está pensada solo para leer, sin cambiar el estado del servidor;
- **idempotente:** repetirla tiene el mismo efecto esperado que ejecutarla una
  sola vez.

Aplicad ambos términos a crear y consultar una predicción.
