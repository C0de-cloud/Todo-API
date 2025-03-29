import os
from fastapi import FastAPI
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.routes import router as todo_router

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(
    title="Todo API",
    description="API для управления задачами с тегами",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB_NAME")]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Подключение роутеров
app.include_router(todo_router, prefix="/api", tags=["todos"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 