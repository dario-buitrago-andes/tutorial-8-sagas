from abc import ABC, abstractmethod
from functools import singledispatch


class Proyeccion(ABC):
    @abstractmethod
    def ejecutar(self):
        ...

class ProyeccionHandler(ABC):
    @abstractmethod
    def handle(self, proyeccion: Proyeccion):
        ...

@singledispatch
def ejecutar_proyeccion(proyeccion):
    raise NotImplementedError(f'No existe implementación para la proyección de tipo {type(proyeccion).__name__}')