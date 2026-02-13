# domain/value_objects.py
"""
Value Objects - Objetos de valor inmutables que representan conceptos del dominio

Los Value Objects:
- Son inmutables (frozen=True)
- Se comparan por valor, no por identidad
- Encapsulan validación de negocio
- No tienen identidad propia
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Codigo:
    """Value Object - Código único del producto Ejemplo: "REC-48V-100A" """

    valor: str

    def __post_init__(self):
        if not self.valor or len(self.valor) > 50:
            raise ValueError("El código debe tener entre 1 y 50 caracteres")
        # Validar formato si es necesario (ajusta el patrón según tus necesidades)
        if not re.match(r"^[A-Z0-9-]+$", self.valor):
            raise ValueError("El código debe contener solo letras mayúsculas, números y guiones")


@dataclass(frozen=True)
class Dimensiones:
    """Value Object - Dimensiones del gabinete"""

    ancho: int | None = None
    alto: int | None = None
    profundidad: int | None = None

    def __post_init__(self):
        if self.ancho and self.ancho <= 0:
            raise ValueError("El ancho debe ser mayor a 0")
        if self.alto and self.alto <= 0:
            raise ValueError("El alto debe ser mayor a 0")
        if self.profundidad and self.profundidad <= 0:
            raise ValueError("La profundidad debe ser mayor a 0")

    def volumen(self) -> int | None:
        """Calcula el volumen en mm³"""
        if all([self.ancho, self.alto, self.profundidad]):
            return self.ancho * self.alto * self.profundidad
        return None

    def __str__(self):
        return f"{self.ancho}x{self.alto}x{self.profundidad} mm"


@dataclass(frozen=True)
class RangoTension:
    """Value Object - Rango de tensión"""

    minimo: float
    maximo: float
    unidad: str = "V"

    def __post_init__(self):
        if self.minimo >= self.maximo:
            raise ValueError("La tensión mínima debe ser menor a la máxima")
        if self.minimo < 0:
            raise ValueError("La tensión no puede ser negativa")

    def contiene(self, valor: float) -> bool:
        """Verifica si un valor está dentro del rango"""
        return self.minimo <= valor <= self.maximo

    @classmethod
    def from_string(cls, rango_str: str) -> "RangoTension":
        """
        Crea un RangoTension desde un string como "220-240V"
        """
        match = re.match(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)([A-Za-z]*)", rango_str)
        if match:
            return cls(
                minimo=float(match.group(1)),
                maximo=float(match.group(2)),
                unidad=match.group(3) or "V",
            )
        raise ValueError(f"Formato de rango inválido: {rango_str}")

    def __str__(self):
        return f"{self.minimo}-{self.maximo}{self.unidad}"


@dataclass(frozen=True)
class Medicion:
    """Value Object - Medición de aparatos"""

    parametro: str
    valor: float
    unidad: str

    def __str__(self):
        return f"{self.valor} {self.unidad}"

    def __eq__(self, other):
        if isinstance(other, Medicion):
            return self.valor == other.valor
        return False

    def __hash__(self):
        return hash(self.valor)
