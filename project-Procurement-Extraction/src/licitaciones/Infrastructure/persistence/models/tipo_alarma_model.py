from sqlalchemy import Column, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TipoAlarmaModel(Base):
    __tablename__ = "tipos_alarma"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)

    alarmas = relationship("AlarmaModel", back_populates="tipo_alarma")

    __table_args__ = (Index("idx_tipos_alarma_codigo", "codigo"),)
