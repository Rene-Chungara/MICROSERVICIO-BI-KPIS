import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de la BD desde variables de entorno con defaults locales
# IMPORTANTE: Usar mismo puerto y contraseña que Backend Java (application.properties)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")  # Backend Java usa puerto 5433
DB_NAME = os.getenv("DB_NAME", "historialclinico")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")  # Backend Java usa "password"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
