from sqlalchemy import Column, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GarantiaModel(Base):
    __tablename__ = "garantia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    meses = Column(Integer, default=24)
    condiciones = Column(Text)

    producto = relationship("ProductoModel", back_populates="garantia")

    __table_args__ = (Index("idx_garantia_producto", "producto_id"),)
