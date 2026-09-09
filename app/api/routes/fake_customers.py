from fastapi import APIRouter
from fastapi import Query
from fastapi.responses import JSONResponse
import time

router = APIRouter(
    prefix="/fake",
    tags=["Fake API"],
)

@router.post("/customer")
def fake_customer(
    cenario: str = Query(default="sucesso"),
):
    if cenario == "sucesso":
        return {
            "nome": "Cliente Teste",
            "score": 742,
            "situacao": "REGULAR",
        }

    if cenario == "erro":
        return JSONResponse(
            status_code=503,
            content={
                "error": "Serviço temporariamente indisponível."
            },
        )

    if cenario == "timeout":
        time.sleep(35)

        return {
            "nome": "Cliente Teste",
            "score": 742,
            "situacao": "REGULAR",
        }
    
    if cenario == "lento":
        time.sleep(15)

        return {
            "nome": "Cliente Teste",
            "score": 742,
            "situacao": "REGULAR",
        }