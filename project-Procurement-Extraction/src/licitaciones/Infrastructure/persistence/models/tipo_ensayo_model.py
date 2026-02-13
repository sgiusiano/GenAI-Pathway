from sqlalchemy import Column, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TipoEnsayoModel(Base):
    __tablename__ = "tipos_ensayo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    orden = Column(Integer)

    ensayos = relationship("EnsayoModel", back_populates="tipo_ensayo")

    __table_args__ = (
        Index("idx_tipos_ensayo_codigo", "codigo"),
        Index("idx_tipos_ensayo_orden", "orden"),
    )
