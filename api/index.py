from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "service": "vir2oz-bot"}

@app.get("/health")
async def health():
    return {"status": "ok"}
