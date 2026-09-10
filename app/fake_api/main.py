from fastapi import FastAPI

from fake_customers import router

app = FastAPI(title="Fake Customer API")

app.include_router(router)