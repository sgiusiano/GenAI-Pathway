from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ProductoModel(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True, index=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(50), nullable=False)
    tension_nominal = Column(Integer, nullable=False)
    corriente_nominal = Column(Integer, nullable=False)
    regulador_diodos = Column(String(20))
    origen = Column(String(100), default="Argentina")
    tipo = Column(String(100), default="Autorregulado")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    accesorios = relationship(
        "AccesoriosModel", back_populates="producto", uselist=False, cascade="all, delete-orphan"
    )
    alarmas = relationship("AlarmaModel", back_populates="producto", cascade="all, delete-orphan")
    alimentacion = relationship(
        "AlimentacionModel", back_populates="producto", uselist=False, cascade="all, delete-orphan"
    )
    aparatos_medida = relationship(
        "AparatosMedidaModel",
        back_populates="producto",
        uselist=False,
        cascade="all, delete-orphan",
    )
    ensayos = relationship("EnsayoModel", back_populates="producto", cascade="all, delete-orphan")
    especificaciones = relationship(
        "EspecificacionesModel",
        back_populates="producto",
        uselist=False,
        cascade="all, delete-orphan",
    )
    gabinete = relationship(
        "GabineteModel", back_populates="producto", uselist=False, cascade="all, delete-orphan"
    )
    garantia = relationship(
        "GarantiaModel", back_populates="producto", uselist=False, cascade="all, delete-orphan"
    )
    salida = relationship(
        "SalidaModel", back_populates="producto", uselist=False, cascade="all, delete-orphan"
    )
    senalizaciones = relationship(
        "SenalizacionModel", back_populates="producto", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_productos_marca_modelo", "marca", "modelo"),
        Index("idx_productos_tension", "tension_nominal"),
        Index("idx_productos_corriente", "corriente_nominal"),
    )
