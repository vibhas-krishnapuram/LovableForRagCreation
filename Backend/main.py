from fastapi import FastAPI

from config.cors import setup_cors
from rag.routes import router as rag_router
from auth.routes import router as auth_router
from db.database import *

app = FastAPI()

Base.metadata.create_all(engine)

setup_cors(app)

app.include_router(auth_router, prefix="/auth")
app.include_router(rag_router, prefix="/rag")

@app.get("/")
def home():
    return {"Hello": "World"}

