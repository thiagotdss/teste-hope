from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.core.exceptions import AppException
from app.api.routes.consultas import router as consultas_router
from fastapi.exceptions import RequestValidationError
from app.fake_api.fake_customers import router as fake_customers_router

app = FastAPI(
    title="Consulta API",
)

#função para tratar exceções da aplicação de maneira padronizada
@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )

#função para tratar exceções de validação de dados de entrada de maneira padronizada
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_DOCUMENT",
                "message": "Documento informado é inválido.",
            }
        },
    )

app.include_router(consultas_router)
app.include_router(fake_customers_router)