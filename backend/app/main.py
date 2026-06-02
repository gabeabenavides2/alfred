from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(title="Alfred API")

app.include_router(chat_router)

@app.get("/health")
def health_check():
    return {"message": "Alfred backend running"}
