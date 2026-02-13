"""Configuración de logging para la aplicación."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configura el logging de la aplicación.

    Args:
        level: Nivel de logging (default: INFO).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del logger (típicamente __name__).

    Returns:
        Logger configurado.
    """
    return logging.getLogger(name)
