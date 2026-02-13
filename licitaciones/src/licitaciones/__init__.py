"""Licitaciones - Sistema de procesamiento de licitaciones eléctricas."""

__version__ = "0.1.0"


# Lazy imports to avoid loading heavy dependencies when importing the package
def __getattr__(name):
    if name == "main":
        from licitaciones.app import main

        return main
    if name == "run":
        from licitaciones.app import run

        return run
    if name == "ApplicationContext":
        from licitaciones.app_context import ApplicationContext

        return ApplicationContext
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["ApplicationContext", "main", "run"]
