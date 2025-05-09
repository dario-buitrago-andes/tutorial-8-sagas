""" Fábricas para la creación de objetos del dominio de vuelos

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de vuelos

"""

from dataclasses import dataclass

from aeroalpes.seedwork.dominio.entidades import Entidad
from aeroalpes.seedwork.dominio.eventos import EventoDominio
from aeroalpes.seedwork.dominio.fabricas import Fabrica
from aeroalpes.seedwork.dominio.repositorios import Mapeador
from .entidades import Reserva
from .excepciones import TipoObjetoNoExisteEnDominioVuelosExcepcion
from .reglas import MinimoUnItinerario, RutaValida


@dataclass
class _FabricaReserva(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad) or isinstance(obj, EventoDominio):
            return mapeador.entidad_a_dto(obj)
        else:
            reserva: Reserva = mapeador.dto_a_entidad(obj)

            self.validar_regla(MinimoUnItinerario(reserva.itinerarios))
            [self.validar_regla(RutaValida(ruta)) for itin in reserva.itinerarios for odo in itin.odos for segmento in odo.segmentos for ruta in segmento.legs]
            
            return reserva

@dataclass
class FabricaVuelos(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if mapeador.obtener_tipo() == Reserva.__class__:
            fabrica_reserva = _FabricaReserva()
            return fabrica_reserva.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioVuelosExcepcion()

