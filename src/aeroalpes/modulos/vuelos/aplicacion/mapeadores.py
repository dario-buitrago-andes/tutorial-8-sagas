from datetime import datetime

from aeroalpes.modulos.vuelos.dominio.entidades import Reserva, Aeropuerto
from aeroalpes.modulos.vuelos.dominio.objetos_valor import Itinerario, Odo, Segmento, Leg
from aeroalpes.seedwork.aplicacion.dto import Mapeador as AppMap
from aeroalpes.seedwork.dominio.repositorios import Mapeador as RepMap
from .dto import ReservaDTO, ItinerarioDTO, OdoDTO, SegmentoDTO, LegDTO


class MapeadorReservaDTOJson(AppMap):
    def _procesar_itinerario(self, itinerario: dict) -> ItinerarioDTO:
        odos_dto: list[OdoDTO] = list()
        for odo in itinerario.get('odos', list()):

            segmentos_dto: list[SegmentoDTO] = list()
            for segmento in odo.get('segmentos', list()):
                legs_dto: list[LegDTO] = list()
                for leg in segmento.get('legs', list()):
                    leg_dto: LegDTO = LegDTO(leg.get('fecha_salida'), leg.get('fecha_llegada'), leg.get('origen'), leg.get('destino')) 
                    legs_dto.append(leg_dto)  
                
                segmentos_dto.append(SegmentoDTO(legs_dto))
            
            odos_dto.append(Odo(segmentos_dto))

        return ItinerarioDTO(odos_dto)
    
    def externo_a_dto(self, externo: dict) -> ReservaDTO:
        reserva_dto = ReservaDTO()

        itinerarios: list[ItinerarioDTO] = list()
        for itin in externo.get('itinerarios', list()):
            reserva_dto.itinerarios.append(self._procesar_itinerario(itin))

        return reserva_dto

    def dto_a_externo(self, dto: ReservaDTO) -> dict:
        return dto.__dict__

class MapeadorReserva(RepMap):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def _procesar_itinerario(self, itinerario_dto: ItinerarioDTO) -> Itinerario:
        odos = list()

        for odo_dto in itinerario_dto.odos:
            segmentos = list()
            for seg_dto in odo_dto.segmentos:
                
                legs = list()

                for leg_dto in seg_dto.legs:
                    destino = Aeropuerto(codigo=leg_dto.destino.get('codigo'), nombre=leg_dto.destino.get('nombre'))
                    origen = Aeropuerto(codigo=leg_dto.origen.get('codigo'), nombre=leg_dto.origen.get('nombre'))
                    fecha_salida = datetime.strptime(leg_dto.fecha_salida, self._FORMATO_FECHA)
                    fecha_llegada = datetime.strptime(leg_dto.fecha_llegada, self._FORMATO_FECHA)

                    leg: Leg = Leg(fecha_salida, fecha_llegada, origen, destino)

                    legs.append(leg)

                segmentos.append(Segmento(legs))
            
            odos.append(Odo(segmentos))

        return Itinerario(odos)

    def obtener_tipo(self) -> type:
        return Reserva.__class__

    def locacion_a_dict(self, locacion):
        if not locacion:
            return dict(codigo=None, nombre=None, fecha_actualizacion=None, fecha_creacion=None)
        
        return dict(
                    codigo=locacion.codigo
                ,   nombre=locacion.nombre
                ,   fecha_actualizacion=locacion.fecha_actualizacion.strftime(self._FORMATO_FECHA)
                ,   fecha_creacion=locacion.fecha_creacion.strftime(self._FORMATO_FECHA)
        )
        

    def entidad_a_dto(self, entidad: Reserva) -> ReservaDTO:
        
        fecha_creacion = entidad.fecha_creacion.strftime(self._FORMATO_FECHA)
        fecha_actualizacion = entidad.fecha_actualizacion.strftime(self._FORMATO_FECHA)
        _id = str(entidad.id)
        itinerarios = list()

        for itin in entidad.itinerarios:
            odos = list()
            for odo in itin.odos:
                segmentos = list()
                for seg in odo.segmentos:
                    legs = list()
                    for leg in seg.legs:
                        fecha_salida = leg.fecha_salida.strftime(self._FORMATO_FECHA)
                        fecha_llegada = leg.fecha_llegada.strftime(self._FORMATO_FECHA)
                        origen = self.locacion_a_dict(leg.origen)
                        destino = self.locacion_a_dict(leg.destino)
                        leg = LegDTO(fecha_salida=fecha_salida, fecha_llegada=fecha_llegada, origen=origen, destino=destino)
                        
                        legs.append(leg)

                    segmentos.append(SegmentoDTO(legs))
                odos.append(OdoDTO(segmentos))
            itinerarios.append(ItinerarioDTO(odos))
        
        return ReservaDTO(fecha_creacion, fecha_actualizacion, _id, itinerarios)

    def dto_a_entidad(self, dto: ReservaDTO) -> Reserva:
        reserva = Reserva()
        reserva.itinerarios = list()

        itinerarios_dto: list[ItinerarioDTO] = dto.itinerarios

        for itin in itinerarios_dto:
            reserva.itinerarios.append(self._procesar_itinerario(itin))
        
        return reserva



