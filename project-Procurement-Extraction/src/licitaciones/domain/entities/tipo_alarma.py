from dataclasses import dataclass


@dataclass
class TipoAlarma:
    """Entity - Catálogo de tipos de alarma"""

    id: int | None = None
    codigo: str = ""
    descripcion: str = ""
