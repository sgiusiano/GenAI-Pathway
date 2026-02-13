from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AparatosMedidaModel(Base):
    __tablename__ = "aparatos_medida"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    unidad_digital_centralizada = Column(Boolean)
    protocolo_comunicacion = Column(String(50))
    puerto_comunicacion = Column(String(100))
    medicion = Column(JSONB)

    producto = relationship("ProductoModel", back_populates="aparatos_medida")

    __table_args__ = (
        Index("idx_aparatos_medida_producto", "producto_id"),
        Index("idx_aparatos_medida_medicion", "medicion", postgresql_using="gin"),
    )
