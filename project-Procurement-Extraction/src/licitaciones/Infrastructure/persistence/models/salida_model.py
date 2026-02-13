from sqlalchemy import Column, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SalidaModel(Base):
    __tablename__ = "salida"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    tension_nominal = Column(Integer)
    corriente_nominal = Column(Integer)
    maxima_corriente_consumos = Column(Integer)
    tipo_interruptor_consumo = Column(Text)
    tipo_interruptor_baterias = Column(Text)
    sistema_rectificacion = Column(Text)

    producto = relationship("ProductoModel", back_populates="salida")

    __table_args__ = (Index("idx_salida_producto", "producto_id"),)
