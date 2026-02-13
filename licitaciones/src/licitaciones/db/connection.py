"""Gestión de conexiones a PostgreSQL."""

from collections.abc import Generator
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as Connection  # noqa: N812
from psycopg2.pool import ThreadedConnectionPool

from licitaciones.config import Settings, get_settings


class DatabaseConnection:
    """Gestiona el pool de conexiones a PostgreSQL."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa el pool de conexiones.

        Args:
            settings: Configuración de la aplicación. Si no se proporciona,
                    se obtiene de get_settings().
        """
        self._settings = settings or get_settings()
        self._pool: ThreadedConnectionPool | None = None

    def _get_pool(self) -> ThreadedConnectionPool:
        """Obtiene o crea el pool de conexiones."""
        if self._pool is None:
            self._pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self._settings.database_url,
            )
        return self._pool

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """Context manager para obtener una conexión del pool.

        Yields:
            Connection: Conexión a PostgreSQL.

        Example:
            ```python
            db = DatabaseConnection()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM productos")
            ```
        """
        pool = self._get_pool()
        conn = pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.putconn(conn)

    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        """Context manager para obtener un cursor directamente.

        Yields:
            cursor: Cursor de PostgreSQL.

        Example:
            ```python
            db = DatabaseConnection()
            with db.get_cursor() as cur:
                cur.execute("SELECT * FROM productos")
                rows = cur.fetchall()
            ```
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                yield cur

    def close(self) -> None:
        """Cierra el pool de conexiones."""
        if self._pool:
            self._pool.closeall()
            self._pool = None

    def execute_script(self, script_path: str) -> None:
        """Ejecuta un script SQL desde un archivo.

        Args:
            script_path: Ruta al archivo SQL.
        """
        with open(script_path, encoding="utf-8") as f:
            script = f.read()

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(script)
