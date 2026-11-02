from fastapi import APIRouter

from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
from app.services.modelo import predecir

# Creamos un objeto llamado router en el que podemos registrar endpoints.
# Cuando hacemos @router.post, estamos registrando el endpoint POST /predict
# dentro de ese router
router = APIRouter()

# ESTE ARCHIVO CREA EL ENDPOINT DE PREDICCIÓN
# La función predecir() existe dentro del código Python, pero necesitamos
# un endpoint que permita utilizarla desde fuera

# TODO: POST /predict (entrada PrestamoEntrada, salida PrediccionSalida)
# router.post("/predict") le indica a FastAPI que la función situada inmediatamente
# debajo debe ejecutarse cuando llegue una petición POST a la ruta /predict
@router.post("/predict", response_model = PrediccionSalida)
def predict(entrada: PrestamoEntrada):
    return predecir(entrada)