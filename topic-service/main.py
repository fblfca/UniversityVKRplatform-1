from fastapi import FastAPI

app = FastAPI(title="VKR Topic Service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "topic"}