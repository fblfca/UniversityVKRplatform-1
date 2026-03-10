from fastapi import FastAPI

app = FastAPI(title="VKR Auth Service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth"}