import time

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/fake/customer")
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
        time.sleep(7)

        return {
            "nome": "Cliente Teste",
            "score": 742,
            "situacao": "REGULAR",
        }