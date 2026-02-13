#!/usr/bin/env python
"""Punto de entrada principal de la aplicación.

Usa ApplicationContext para obtener todas las dependencias.
"""

import argparse
import sys
import time
from pathlib import Path

from licitaciones.app_context import ApplicationContext
from licitaciones.db.init import ensure_database_ready
from licitaciones.infrastructure.dependency_injection import DependencyContainer
from licitaciones.logger import get_logger, setup_logging

logger = get_logger(__name__)


def parse_page_ranges(pages_str: str) -> list[tuple[int, int]]:
    """Parse page ranges string into list of tuples.

    Args:
        pages_str: String like "1-10, 15-25, 45-50"

    Returns:
        List of (start, end) tuples, e.g., [(1, 10), (15, 25), (45, 50)]

    Raises:
        ValueError: If format is invalid.
    """
    ranges = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" not in part:
            raise ValueError(f"Invalid range format: '{part}'. Expected 'start-end'.")
        try:
            start_str, end_str = part.split("-")
            start, end = int(start_str.strip()), int(end_str.strip())
        except ValueError as e:
            raise ValueError(f"Invalid range '{part}': {e}") from e

        if start < 1:
            raise ValueError(f"Page numbers must be >= 1, got {start}")
        if start > end:
            raise ValueError(f"Start page ({start}) must be <= end page ({end})")

        ranges.append((start, end))
    return ranges


def wait_for_database(ctx: ApplicationContext, max_retries: int = 30) -> bool:
    """Espera a que la base de datos esté disponible.

    Args:
        ctx: Contexto de la aplicación.
        max_retries: Número máximo de reintentos.

    Returns:
        True si se conectó, False si no.
    """
    logger.info("Esperando conexión a la base de datos...")
    for i in range(max_retries):
        try:
            with ctx.db_connection.get_cursor() as cur:
                cur.execute("SELECT 1")
                logger.info("Conexión a base de datos establecida")
                return True
        except Exception:
            if i < max_retries - 1:
                logger.debug("Reintentando (%d/%d)...", i + 1, max_retries)
                time.sleep(1)
    logger.error("No se pudo conectar a la base de datos")
    return False


def get_dependency_container(session):
    """Factory para obtener el contenedor de dependencias"""
    return DependencyContainer(session)


def run(
    pdf_path: Path,
    page_ranges: list[tuple[int, int]] | None = None,
) -> int:
    """Ejecuta el flujo principal de la aplicación.

    Args:
        pdf_path: Ruta al PDF a procesar.
        page_ranges: Lista opcional de rangos de páginas a procesar.

    Returns:
        Código de salida (0 = éxito, 1 = error).
    """
    ctx = ApplicationContext()
    try:
        # 1. Esperar conexión a BD
        if not wait_for_database(ctx):
            return 1

        # 2. Verificar/crear tablas
        if not ensure_database_ready(ctx.db_connection):
            return 1

        # 3. Procesar PDF
        if page_ranges:
            logger.info("Procesando PDF: %s (páginas: %s)", pdf_path, page_ranges)
        else:
            logger.info("Procesando PDF: %s", pdf_path)
        result = ctx.extraction_pipeline.process_pdf(pdf_path, page_ranges)
        logger.info("Extracción completada: %d items encontrados", len(result.items))
        # TODO: Guardar en BD y hacer matching con catálogo
        json_output = result.model_dump_json(indent=2, ensure_ascii=False)
        output_path = pdf_path.with_suffix(".json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output)
        logger.info("Resultados guardados en: %s", output_path)
        return 0
    finally:
        ctx.close()


def main() -> None:
    """Punto de entrada CLI."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Procesa PDFs de licitaciones y extrae productos")
    parser.add_argument("--pdf", type=Path, required=True, help="Ruta al PDF a procesar")
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Rangos de páginas a procesar (ej: '1-10, 15-25, 45-50'). 1-indexed, inclusive.",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        logger.error("Archivo no encontrado: %s", args.pdf)
        sys.exit(1)

    page_ranges = None
    if args.pages:
        try:
            page_ranges = parse_page_ranges(args.pages)
            logger.info("Rangos de páginas especificados: %s", page_ranges)
        except ValueError as e:
            logger.error("Error en formato de páginas: %s", e)
            sys.exit(1)

    sys.exit(run(args.pdf, page_ranges))


if __name__ == "__main__":
    main()
