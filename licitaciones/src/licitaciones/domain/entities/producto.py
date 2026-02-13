# domain/entities/producto.py
from dataclasses import dataclass, field
from datetime import datetime
from licitaciones.domain.entities.accesorios import Accesorios
from licitaciones.domain.entities.alarma import Alarma
from licitaciones.domain.entities.alimentacion import Alimentacion
from licitaciones.domain.entities.aparato_medida import AparatosMedida
from licitaciones.domain.entities.ensayo import Ensayo
from licitaciones.domain.entities.especificaciones import Especificaciones
from licitaciones.domain.entities.gabinete import Gabinete
from licitaciones.domain.entities.garantia import Garantia
from licitaciones.domain.entities.salida import Salida
from licitaciones.domain.entities.senalizacion import Senalizacion
from licitaciones.domain.valueObjects.value_objects import Codigo


@dataclass
class Producto:
    """Aggregate Root - Entidad principal del dominio"""

    id: int | None = None
    codigo: Codigo = None
    marca: str = ""
    modelo: str = ""
    tension_nominal: int = 0
    corriente_nominal: int = 0
    regulador_diodos: str | None = None
    origen: str = "Argentina"
    tipo: str = "Autorregulado"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Relaciones - Agregados internos
    accesorios: "Accesorios | None" = None
    alarmas: list["Alarma"] = field(default_factory=list)
    alimentacion: "Alimentacion | None" = None
    aparatos_medida: "AparatosMedida | None" = None
    ensayos: list["Ensayo"] = field(default_factory=list)
    especificaciones: "Especificaciones | None" = None
    gabinete: "Gabinete | None" = None
    garantia: "Garantia | None" = None
    salida: "Salida | None" = None
    senalizaciones: list["Senalizacion"] = field(default_factory=list)

    def __post_init__(self):
        if self.codigo and isinstance(self.codigo, str):
            self.codigo = Codigo(self.codigo)

    def agregar_alarma(self, alarma: "Alarma") -> None:
        """Método de dominio para agregar alarma"""
        if alarma not in self.alarmas:
            self.alarmas.append(alarma)
            alarma.producto_id = self.id

    def agregar_ensayo(self, ensayo: "Ensayo") -> None:
        """Método de dominio para agregar ensayo"""
        if ensayo not in self.ensayos:
            self.ensayos.append(ensayo)
            ensayo.producto_id = self.id

    def es_valido(self) -> bool:
        """Validación de negocio"""
        return (
            self.codigo is not None
            and len(self.marca) > 0
            and len(self.modelo) > 0
            and self.tension_nominal > 0
            and self.corriente_nominal > 0
        )
