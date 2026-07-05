import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# No Render, a variável DATABASE_URL é fornecida automaticamente (PostgreSQL).
# No Codespace (sem essa variável), cai no SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./funcionarios.db")

# O Render entrega a URL começando com "postgres://", mas o SQLAlchemy
# moderno espera "postgresql://". Ajuste automático:
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args só é necessário para SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()