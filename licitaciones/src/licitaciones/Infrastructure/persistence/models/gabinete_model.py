from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GabineteModel(Base):
    __tablename__ = "gabinete"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    material = Column(String(100))
    acceso = Column(String(100))
    grado_proteccion = Column(String(10))
    espesor_chapa = Column(Numeric(5, 2))
    tipo_pintura = Column(String(100))
    color = Column(String(20))
    espesor_pintura = Column(Numeric(5, 2))
    ancho = Column(Integer)
    alto = Column(Integer)
    profundidad = Column(Integer)
    peso = Column(Integer)

    producto = relationship("ProductoModel", back_populates="gabinete")

    __table_args__ = (
        Index("idx_gabinete_producto", "producto_id"),
        Index("idx_gabinete_dimensiones", "ancho", "alto", "profundidad"),
    )
