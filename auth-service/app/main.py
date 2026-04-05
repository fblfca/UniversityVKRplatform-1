from fastapi import FastAPI

from app.routers import auth_router


app = FastAPI(
    title="VKR Auth Service",
    description="Сервис аутентификации, входа и выдачи JWT для VKR Platform",
    version="0.2.0",
)

app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "auth"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Auth Service is running"}
