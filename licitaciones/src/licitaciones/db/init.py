"""Inicialización de la base de datos.

Verifica el estado de la BD y la inicializa si es necesario:
1. Crea tablas si no existen (migrations)
2. Carga catálogo si está vacío
"""

from pathlib import Path

from licitaciones.db.catalog import load_catalog
from licitaciones.db.connection import DatabaseConnection
from licitaciones.logger import get_logger

logger = get_logger(__name__)

# Directorio de migraciones SQL
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _check_tables_exist(db: DatabaseConnection) -> bool:
    """Verifica si las tablas principales existen."""
    try:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'productos'
                )
            """)
            result = cur.fetchone()
            return result[0] if result else False
    except Exception:
        return False


def _count_products(db: DatabaseConnection) -> int:
    """Cuenta los productos en la base de datos."""
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM productos")
            result = cur.fetchone()
            return result[0] if result else 0
    except Exception:
        return 0


def _run_migrations(db: DatabaseConnection) -> bool:
    """Ejecuta las migraciones SQL para crear el esquema."""
    if not MIGRATIONS_DIR.exists():
        logger.error("Directorio de migraciones no encontrado: %s", MIGRATIONS_DIR)
        return False

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        logger.warning("No se encontraron archivos de migración")
        return True

    logger.info("Ejecutando %d migraciones...", len(migration_files))

    for migration_file in migration_files:
        try:
            db.execute_script(str(migration_file))
            logger.info("  %s OK", migration_file.name)
        except Exception as e:
            logger.error("  %s ERROR: %s", migration_file.name, e)
            return False

    return True


def ensure_database_ready(db: DatabaseConnection) -> bool:
    """Asegura que la base de datos esté lista para usar.

    1. Verifica si las tablas existen, si no las crea
    2. Verifica si hay productos, si no carga el catálogo

    Args:
        db: Conexión a la base de datos.

    Returns:
        True si la base de datos está lista, False si hubo error.
    """
    # 1. Verificar/crear tablas
    if not _check_tables_exist(db):
        logger.info("Tablas no encontradas, ejecutando migraciones...")
        if not _run_migrations(db):
            logger.error("Error ejecutando migraciones")
            return False
        logger.info("Esquema creado correctamente")

    # 2. Verificar/cargar catálogo
    product_count = _count_products(db)
    if product_count == 0:
        logger.info("Base de datos vacía, cargando catálogo...")
        loaded = load_catalog(db)
        if loaded == 0:
            logger.warning("No se cargaron productos (verificar archivos CSV)")
        else:
            logger.info("Catálogo cargado: %d productos", loaded)
    else:
        logger.info("Base de datos lista (%d productos)", product_count)

    return True
