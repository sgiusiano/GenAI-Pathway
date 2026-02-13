from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AccesoriosModel(Base):
    __tablename__ = "accesorios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    panel_control = Column(Text)
    resistencias_calefactoras = Column(Text)
    tension_resistencias = Column(Integer)
    potencia_resistencias = Column(String(100))
    cables_incluidos = Column(Text)
    tension_aislacion_cables = Column(String(20))
    material_cables = Column(String(50))
    baja_emision_halogenos = Column(Boolean)
    bornes_reserva = Column(Boolean)
    placas_identificacion = Column(Boolean)
    chapa_caracteristicas = Column(Boolean)

    producto = relationship("ProductoModel", back_populates="accesorios")

    __table_args__ = (Index("idx_accesorios_producto", "producto_id"),)
