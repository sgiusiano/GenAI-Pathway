from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AlimentacionModel(Base):
    __tablename__ = "alimentacion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    tipo = Column(String(50))
    tension = Column(String(50))
    rango_tension = Column(String(50))
    frecuencia = Column(Integer)
    rango_frecuencia = Column(String(50))
    conexion_neutro = Column(String(50))
    conductor_pe_independiente = Column(Boolean)
    corriente_cortocircuito = Column(String(100))
    tipo_interruptor_acometida = Column(Text)
    potencia_transformador = Column(String(50))
    corriente_conexion_transformador = Column(String(50))

    producto = relationship("ProductoModel", back_populates="alimentacion")

    __table_args__ = (
        Index("idx_alimentacion_producto", "producto_id"),
        Index("idx_alimentacion_tipo", "tipo"),
    )
