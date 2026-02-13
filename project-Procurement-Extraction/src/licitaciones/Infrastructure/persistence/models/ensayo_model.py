from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class EnsayoModel(Base):
    __tablename__ = "ensayos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    tipo_ensayo_id = Column(Integer, ForeignKey("tipos_ensayo.id"))
    realizado = Column(Boolean, default=True)
    observaciones = Column(Text)

    producto = relationship("ProductoModel", back_populates="ensayos")
    tipo_ensayo = relationship("TipoEnsayoModel", back_populates="ensayos")

    __table_args__ = (
        Index("idx_ensayos_producto", "producto_id"),
        Index("idx_ensayos_tipo", "tipo_ensayo_id"),
    )
