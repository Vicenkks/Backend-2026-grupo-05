
import os

from collections.abc import Generator

from sqlalchemy import create_engine, event, URL
from dotenv import load_dotenv

load_dotenv()
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    URL.create("postgresql+psycopg2",
        username=os.getenv("DB_USER", "coworking"),
        password=os.getenv("DB_PASSWORD", "desarrollo_local"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "coworking")),
)

# SQLite necesita esta configuración para trabajar
# correctamente con FastAPI.
connect_args = {}

if str(DATABASE_URL).startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


if str(DATABASE_URL).startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def crear_tablas() -> None:
    # Importar los modelos permite que SQLAlchemy
    # conozca todas las tablas antes de crearlas.
    import infrastructure.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
