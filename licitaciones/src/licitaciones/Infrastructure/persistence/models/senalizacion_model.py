from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SenalizacionModel(Base):
    __tablename__ = "senalizaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    tipo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    tipo_display = Column(String(50))

    producto = relationship("ProductoModel", back_populates="senalizaciones")

    __table_args__ = (
        Index("idx_senalizaciones_producto", "producto_id"),
        Index("idx_senalizaciones_tipo", "tipo"),
    )
