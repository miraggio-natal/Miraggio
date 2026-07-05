from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app import models  # noqa: F401
from app.controller import funcionarios_router, candidatos_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Seleção & Funcionários", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(funcionarios_router)
app.include_router(candidatos_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Painel administrativo (pasta frontend-admin)
app.mount("/admin", StaticFiles(directory="../frontend-admin", html=True), name="admin")

# Portal público: portal + currículo (pasta frontend-publico) — precisa ser o ÚLTIMO
app.mount("/", StaticFiles(directory="../frontend-publico", html=True), name="site")