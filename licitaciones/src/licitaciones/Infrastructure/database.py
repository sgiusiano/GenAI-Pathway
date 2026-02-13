from collections.abc import Generator
from contextlib import contextmanager

from infrastructure.persistence.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseConfig:
    """Configuración de la base de datos"""

    def __init__(self, database_url: str):
        """
        Args:
            database_url: URL de conexión a PostgreSQL
                Ejemplo: "postgresql://user:password@localhost:5432/dbname"
        """
        self.engine = create_engine(
            database_url,
            echo=False,  # Cambiar a True para ver queries SQL
            pool_pre_ping=True,  # Verifica conexiones antes de usarlas
            pool_size=5,
            max_overflow=10,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Crea todas las tablas en la base de datos"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Elimina todas las tablas (usar con cuidado)"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager para obtener una sesión de base de datos"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
