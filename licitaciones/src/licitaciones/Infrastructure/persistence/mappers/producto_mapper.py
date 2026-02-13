from licitaciones.domain.entities.accesorios import Accesorios
from licitaciones.domain.entities.alarma import Alarma
from licitaciones.domain.entities.alimentacion import Alimentacion
from licitaciones.domain.entities.aparato_medida import AparatosMedida
from licitaciones.domain.entities.ensayo import Ensayo
from licitaciones.domain.entities.especificaciones import Especificaciones
from licitaciones.domain.entities.gabinete import Gabinete
from licitaciones.domain.entities.garantia import Garantia
from licitaciones.domain.entities.producto import Producto
from licitaciones.domain.entities.salida import Salida
from licitaciones.domain.entities.senalizacion import Senalizacion
from licitaciones.domain.entities.tipo_alarma import TipoAlarma
from licitaciones.domain.entities.tipo_ensayo import TipoEnsayo
from licitaciones.domain.valueObjects.value_objects import Codigo, Dimensiones, RangoTension
from licitaciones.infrastructure.persistence.models.accesorio_model import AccesoriosModel
from licitaciones.infrastructure.persistence.models.alarma_model import AlarmaModel
from licitaciones.infrastructure.persistence.models.alimentacion_model import AlimentacionModel
from licitaciones.infrastructure.persistence.models.aparatos_medida_model import (
    AparatosMedidaModel,
)
from licitaciones.infrastructure.persistence.models.ensayo_model import EnsayoModel
from licitaciones.infrastructure.persistence.models.especificaciones_model import (
    EspecificacionesModel,
)
from licitaciones.infrastructure.persistence.models.gabinete_model import GabineteModel
from licitaciones.infrastructure.persistence.models.garantia_model import GarantiaModel
from licitaciones.infrastructure.persistence.models.producto_model import ProductoModel
from licitaciones.infrastructure.persistence.models.salida_model import SalidaModel
from licitaciones.infrastructure.persistence.models.senalizacion_model import SenalizacionModel


class ProductoMapper:
    """Mapper entre entidad Producto y ProductoModel"""

    def to_entity(self, model: ProductoModel) -> Producto | None:
        """Convierte un modelo SQLAlchemy a entidad de dominio"""
        if not model:
            return None

        return Producto(
            id=model.id,
            codigo=Codigo(model.codigo),
            marca=model.marca,
            modelo=model.modelo,
            tension_nominal=model.tension_nominal,
            corriente_nominal=model.corriente_nominal,
            regulador_diodos=model.regulador_diodos,
            origen=model.origen,
            tipo=model.tipo,
            created_at=model.created_at,
            updated_at=model.updated_at,
            accesorios=self._map_accesorios(model.accesorios) if model.accesorios else None,
            alarmas=[self._map_alarma(a) for a in model.alarmas] if model.alarmas else [],
            alimentacion=self._map_alimentacion(model.alimentacion) if model.alimentacion else None,
            aparatos_medida=self._map_aparatos_medida(model.aparatos_medida)
            if model.aparatos_medida
            else None,
            ensayos=[self._map_ensayo(e) for e in model.ensayos] if model.ensayos else [],
            especificaciones=self._map_especificaciones(model.especificaciones)
            if model.especificaciones
            else None,
            gabinete=self._map_gabinete(model.gabinete) if model.gabinete else None,
            garantia=self._map_garantia(model.garantia) if model.garantia else None,
            salida=self._map_salida(model.salida) if model.salida else None,
            senalizaciones=[self._map_senalizacion(s) for s in model.senalizaciones]
            if model.senalizaciones
            else [],
        )

    def to_model(self, entity: Producto) -> ProductoModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy"""
        model = ProductoModel(
            codigo=str(entity.codigo),
            marca=entity.marca,
            modelo=entity.modelo,
            tension_nominal=entity.tension_nominal,
            corriente_nominal=entity.corriente_nominal,
            regulador_diodos=entity.regulador_diodos,
            origen=entity.origen,
            tipo=entity.tipo,
        )

        # Mapear relaciones
        if entity.accesorios:
            model.accesorios = self._accesorios_to_model(entity.accesorios)

        if entity.alarmas:
            model.alarmas = [self._alarma_to_model(a) for a in entity.alarmas]

        if entity.alimentacion:
            model.alimentacion = self._alimentacion_to_model(entity.alimentacion)

        if entity.aparatos_medida:
            model.aparatos_medida = self._aparatos_medida_to_model(entity.aparatos_medida)

        if entity.ensayos:
            model.ensayos = [self._ensayo_to_model(e) for e in entity.ensayos]

        if entity.especificaciones:
            model.especificaciones = self._especificaciones_to_model(entity.especificaciones)

        if entity.gabinete:
            model.gabinete = self._gabinete_to_model(entity.gabinete)

        if entity.garantia:
            model.garantia = self._garantia_to_model(entity.garantia)

        if entity.salida:
            model.salida = self._salida_to_model(entity.salida)

        if entity.senalizaciones:
            model.senalizaciones = [self._senalizacion_to_model(s) for s in entity.senalizaciones]

        return model

    def update_model(self, model: ProductoModel, entity: Producto) -> ProductoModel:
        """Actualiza un modelo existente con datos de la entidad"""
        model.codigo = str(entity.codigo)
        model.marca = entity.marca
        model.modelo = entity.modelo
        model.tension_nominal = entity.tension_nominal
        model.corriente_nominal = entity.corriente_nominal
        model.regulador_diodos = entity.regulador_diodos
        model.origen = entity.origen
        model.tipo = entity.tipo

        # Actualizar relaciones (simplificado - en producción manejar actualizaciones complejas)
        return model

    # Métodos auxiliares para mapear relaciones
    def _map_accesorios(self, model: AccesoriosModel) -> Accesorios:
        return Accesorios(
            id=model.id,
            producto_id=model.producto_id,
            panel_control=model.panel_control,
            resistencias_calefactoras=model.resistencias_calefactoras,
            tension_resistencias=model.tension_resistencias,
            potencia_resistencias=model.potencia_resistencias,
            cables_incluidos=model.cables_incluidos,
            tension_aislacion_cables=model.tension_aislacion_cables,
            material_cables=model.material_cables,
            baja_emision_halogenos=model.baja_emision_halogenos,
            bornes_reserva=model.bornes_reserva,
            placas_identificacion=model.placas_identificacion,
            chapa_caracteristicas=model.chapa_caracteristicas,
        )

    def _accesorios_to_model(self, entity: Accesorios) -> AccesoriosModel:
        return AccesoriosModel(
            panel_control=entity.panel_control,
            resistencias_calefactoras=entity.resistencias_calefactoras,
            tension_resistencias=entity.tension_resistencias,
            potencia_resistencias=entity.potencia_resistencias,
            cables_incluidos=entity.cables_incluidos,
            tension_aislacion_cables=entity.tension_aislacion_cables,
            material_cables=entity.material_cables,
            baja_emision_halogenos=entity.baja_emision_halogenos,
            bornes_reserva=entity.bornes_reserva,
            placas_identificacion=entity.placas_identificacion,
            chapa_caracteristicas=entity.chapa_caracteristicas,
        )

    def _map_alarma(self, model: AlarmaModel) -> Alarma:
        tipo_alarma = None
        if model.tipo_alarma:
            tipo_alarma = TipoAlarma(
                id=model.tipo_alarma.id,
                codigo=model.tipo_alarma.codigo,
                descripcion=model.tipo_alarma.descripcion,
            )

        return Alarma(
            id=model.id,
            producto_id=model.producto_id,
            tipo_alarma_id=model.tipo_alarma_id,
            tipo_senal=model.tipo_senal,
            activa=model.activa,
            tipo_alarma=tipo_alarma,
        )

    def _alarma_to_model(self, entity: Alarma) -> AlarmaModel:
        return AlarmaModel(
            tipo_alarma_id=entity.tipo_alarma_id, tipo_senal=entity.tipo_senal, activa=entity.activa
        )

    def _map_alimentacion(self, model: AlimentacionModel) -> Alimentacion:
        rango_tension = None
        if model.rango_tension:
            try:
                rango_tension = RangoTension.from_string(model.rango_tension)
            except ValueError:
                pass

        return Alimentacion(
            id=model.id,
            producto_id=model.producto_id,
            tipo=model.tipo,
            tension=model.tension,
            rango_tension=rango_tension,
            frecuencia=model.frecuencia,
            rango_frecuencia=model.rango_frecuencia,
            conexion_neutro=model.conexion_neutro,
            conductor_pe_independiente=model.conductor_pe_independiente,
            corriente_cortocircuito=model.corriente_cortocircuito,
            tipo_interruptor_acometida=model.tipo_interruptor_acometida,
            potencia_transformador=model.potencia_transformador,
            corriente_conexion_transformador=model.corriente_conexion_transformador,
        )

    def _alimentacion_to_model(self, entity: Alimentacion) -> AlimentacionModel:
        return AlimentacionModel(
            tipo=entity.tipo,
            tension=entity.tension,
            rango_tension=str(entity.rango_tension) if entity.rango_tension else None,
            frecuencia=entity.frecuencia,
            rango_frecuencia=entity.rango_frecuencia,
            conexion_neutro=entity.conexion_neutro,
            conductor_pe_independiente=entity.conductor_pe_independiente,
            corriente_cortocircuito=entity.corriente_cortocircuito,
            tipo_interruptor_acometida=entity.tipo_interruptor_acometida,
            potencia_transformador=entity.potencia_transformador,
            corriente_conexion_transformador=entity.corriente_conexion_transformador,
        )

    def _map_aparatos_medida(self, model: AparatosMedidaModel) -> AparatosMedida:
        return AparatosMedida(
            id=model.id,
            producto_id=model.producto_id,
            unidad_digital_centralizada=model.unidad_digital_centralizada,
            protocolo_comunicacion=model.protocolo_comunicacion,
            puerto_comunicacion=model.puerto_comunicacion,
            medicion=model.medicion,
        )

    def _aparatos_medida_to_model(self, entity: AparatosMedida) -> AparatosMedidaModel:
        return AparatosMedidaModel(
            unidad_digital_centralizada=entity.unidad_digital_centralizada,
            protocolo_comunicacion=entity.protocolo_comunicacion,
            puerto_comunicacion=entity.puerto_comunicacion,
            medicion=entity.medicion,
        )

    def _map_ensayo(self, model: EnsayoModel) -> Ensayo:
        tipo_ensayo = None
        if model.tipo_ensayo:
            tipo_ensayo = TipoEnsayo(
                id=model.tipo_ensayo.id,
                codigo=model.tipo_ensayo.codigo,
                descripcion=model.tipo_ensayo.descripcion,
                orden=model.tipo_ensayo.orden,
            )

        return Ensayo(
            id=model.id,
            producto_id=model.producto_id,
            tipo_ensayo_id=model.tipo_ensayo_id,
            realizado=model.realizado,
            observaciones=model.observaciones,
            tipo_ensayo=tipo_ensayo,
        )

    def _ensayo_to_model(self, entity: Ensayo) -> EnsayoModel:
        return EnsayoModel(
            tipo_ensayo_id=entity.tipo_ensayo_id,
            realizado=entity.realizado,
            observaciones=entity.observaciones,
        )

    def _map_especificaciones(self, model: EspecificacionesModel) -> Especificaciones:
        return Especificaciones(
            id=model.id,
            producto_id=model.producto_id,
            normas_fabricacion=model.normas_fabricacion,
            apto_pb_ac=model.apto_pb_ac,
            apto_ni_cd=model.apto_ni_cd,
            temperatura_maxima=float(model.temperatura_maxima)
            if model.temperatura_maxima
            else None,
            temperatura_minima=float(model.temperatura_minima)
            if model.temperatura_minima
            else None,
            altura_snm=model.altura_snm,
            humedad_relativa_max=float(model.humedad_relativa_max)
            if model.humedad_relativa_max
            else None,
            tipo_instalacion=model.tipo_instalacion,
            tipo_servicio=model.tipo_servicio,
            ventilacion=model.ventilacion,
            tipo_rectificador=model.tipo_rectificador,
            nivel_ruido=model.nivel_ruido,
            rendimiento_minimo=float(model.rendimiento_minimo)
            if model.rendimiento_minimo
            else None,
            proteccion_sobretension=model.proteccion_sobretension,
            proteccion_cortocircuito=model.proteccion_cortocircuito,
            proteccion_sobrecarga=model.proteccion_sobrecarga,
            ripple_con_baterias=model.ripple_con_baterias,
            ripple_sin_baterias=model.ripple_sin_baterias,
            tension_flote_min=float(model.tension_flote_min) if model.tension_flote_min else None,
            tension_flote_max=float(model.tension_flote_max) if model.tension_flote_max else None,
            tension_fondo_min=float(model.tension_fondo_min) if model.tension_fondo_min else None,
            tension_fondo_max=float(model.tension_fondo_max) if model.tension_fondo_max else None,
            modo_manual_automatico=model.modo_manual_automatico,
            modo_carga_excepcional=model.modo_carga_excepcional,
            regulador_diodos_carga=model.regulador_diodos_carga,
            rango_salida_nicd=model.rango_salida_nicd,
            rango_salida_pbca=model.rango_salida_pbca,
            deteccion_polo_tierra=model.deteccion_polo_tierra,
        )

    def _especificaciones_to_model(self, entity: Especificaciones) -> EspecificacionesModel:
        return EspecificacionesModel(
            normas_fabricacion=entity.normas_fabricacion,
            apto_pb_ac=entity.apto_pb_ac,
            apto_ni_cd=entity.apto_ni_cd,
            temperatura_maxima=entity.temperatura_maxima,
            temperatura_minima=entity.temperatura_minima,
            altura_snm=entity.altura_snm,
            humedad_relativa_max=entity.humedad_relativa_max,
            tipo_instalacion=entity.tipo_instalacion,
            tipo_servicio=entity.tipo_servicio,
            ventilacion=entity.ventilacion,
            tipo_rectificador=entity.tipo_rectificador,
            nivel_ruido=entity.nivel_ruido,
            rendimiento_minimo=entity.rendimiento_minimo,
            proteccion_sobretension=entity.proteccion_sobretension,
            proteccion_cortocircuito=entity.proteccion_cortocircuito,
            proteccion_sobrecarga=entity.proteccion_sobrecarga,
            ripple_con_baterias=entity.ripple_con_baterias,
            ripple_sin_baterias=entity.ripple_sin_baterias,
            tension_flote_min=entity.tension_flote_min,
            tension_flote_max=entity.tension_flote_max,
            tension_fondo_min=entity.tension_fondo_min,
            tension_fondo_max=entity.tension_fondo_max,
            modo_manual_automatico=entity.modo_manual_automatico,
            modo_carga_excepcional=entity.modo_carga_excepcional,
            regulador_diodos_carga=entity.regulador_diodos_carga,
            rango_salida_nicd=entity.rango_salida_nicd,
            rango_salida_pbca=entity.rango_salida_pbca,
            deteccion_polo_tierra=entity.deteccion_polo_tierra,
        )

    def _map_gabinete(self, model: GabineteModel) -> Gabinete:
        dimensiones = None
        if model.ancho or model.alto or model.profundidad:
            dimensiones = Dimensiones(
                ancho=model.ancho, alto=model.alto, profundidad=model.profundidad
            )

        return Gabinete(
            id=model.id,
            producto_id=model.producto_id,
            material=model.material,
            acceso=model.acceso,
            grado_proteccion=model.grado_proteccion,
            espesor_chapa=float(model.espesor_chapa) if model.espesor_chapa else None,
            tipo_pintura=model.tipo_pintura,
            color=model.color,
            espesor_pintura=float(model.espesor_pintura) if model.espesor_pintura else None,
            dimensiones=dimensiones,
            peso=model.peso,
        )

    def _gabinete_to_model(self, entity: Gabinete) -> GabineteModel:
        return GabineteModel(
            material=entity.material,
            acceso=entity.acceso,
            grado_proteccion=entity.grado_proteccion,
            espesor_chapa=entity.espesor_chapa,
            tipo_pintura=entity.tipo_pintura,
            color=entity.color,
            espesor_pintura=entity.espesor_pintura,
            ancho=entity.dimensiones.ancho if entity.dimensiones else None,
            alto=entity.dimensiones.alto if entity.dimensiones else None,
            profundidad=entity.dimensiones.profundidad if entity.dimensiones else None,
            peso=entity.peso,
        )

    def _map_garantia(self, model: GarantiaModel) -> Garantia:
        return Garantia(
            id=model.id,
            producto_id=model.producto_id,
            meses=model.meses,
            condiciones=model.condiciones,
        )

    def _garantia_to_model(self, entity: Garantia) -> GarantiaModel:
        return GarantiaModel(meses=entity.meses, condiciones=entity.condiciones)

    def _map_salida(self, model: SalidaModel) -> Salida:
        return Salida(
            id=model.id,
            producto_id=model.producto_id,
            tension_nominal=model.tension_nominal,
            corriente_nominal=model.corriente_nominal,
            maxima_corriente_consumos=model.maxima_corriente_consumos,
            tipo_interruptor_consumo=model.tipo_interruptor_consumo,
            tipo_interruptor_baterias=model.tipo_interruptor_baterias,
            sistema_rectificacion=model.sistema_rectificacion,
        )

    def _salida_to_model(self, entity: Salida) -> SalidaModel:
        return SalidaModel(
            tension_nominal=entity.tension_nominal,
            corriente_nominal=entity.corriente_nominal,
            maxima_corriente_consumos=entity.maxima_corriente_consumos,
            tipo_interruptor_consumo=entity.tipo_interruptor_consumo,
            tipo_interruptor_baterias=entity.tipo_interruptor_baterias,
            sistema_rectificacion=entity.sistema_rectificacion,
        )

    def _map_senalizacion(self, model: SenalizacionModel) -> Senalizacion:
        return Senalizacion(
            id=model.id,
            producto_id=model.producto_id,
            tipo=model.tipo,
            descripcion=model.descripcion,
            tipo_display=model.tipo_display,
        )

    def _senalizacion_to_model(self, entity: Senalizacion) -> SenalizacionModel:
        return SenalizacionModel(
            tipo=entity.tipo, descripcion=entity.descripcion, tipo_display=entity.tipo_display
        )
