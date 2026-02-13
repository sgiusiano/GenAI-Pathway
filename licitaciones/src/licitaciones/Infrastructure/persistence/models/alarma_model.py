from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AlarmaModel(Base):
    __tablename__ = "alarmas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    tipo_alarma_id = Column(Integer, ForeignKey("tipos_alarma.id"))
    tipo_senal = Column(String(100))
    activa = Column(Boolean, default=True)

    producto = relationship("ProductoModel", back_populates="alarmas")
    tipo_alarma = relationship("TipoAlarmaModel", back_populates="alarmas")

    __table_args__ = (
        Index("idx_alarmas_producto", "producto_id"),
        Index("idx_alarmas_tipo", "tipo_alarma_id"),
    )
