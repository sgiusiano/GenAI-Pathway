from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class EspecificacionesModel(Base):
    __tablename__ = "especificaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), unique=True)
    normas_fabricacion = Column(Text)
    apto_pb_ac = Column(Boolean, default=True)
    apto_ni_cd = Column(Boolean, default=True)
    temperatura_maxima = Column(Numeric(5, 2))
    temperatura_minima = Column(Numeric(5, 2))
    altura_snm = Column(Integer)
    humedad_relativa_max = Column(Numeric(5, 2))
    tipo_instalacion = Column(String(50))
    tipo_servicio = Column(String(50))
    ventilacion = Column(String(50))
    tipo_rectificador = Column(Text)
    nivel_ruido = Column(String(10))
    rendimiento_minimo = Column(Numeric(5, 2))
    proteccion_sobretension = Column(Text)
    proteccion_cortocircuito = Column(Text)
    proteccion_sobrecarga = Column(Text)
    ripple_con_baterias = Column(String(10))
    ripple_sin_baterias = Column(String(10))
    tension_flote_min = Column(Numeric(6, 2))
    tension_flote_max = Column(Numeric(6, 2))
    tension_fondo_min = Column(Numeric(6, 2))
    tension_fondo_max = Column(Numeric(6, 2))
    modo_manual_automatico = Column(Boolean)
    modo_carga_excepcional = Column(Boolean)
    regulador_diodos_carga = Column(String(50))
    rango_salida_nicd = Column(String(50))
    rango_salida_pbca = Column(String(50))
    deteccion_polo_tierra = Column(Boolean)

    producto = relationship("ProductoModel", back_populates="especificaciones")

    __table_args__ = (Index("idx_especificaciones_producto", "producto_id"),)
