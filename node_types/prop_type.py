
from abc import ABC, abstractproperty


class PropType(ABC):

    @abstractproperty
    def type_name(self):
        pass

    @abstractproperty
    def property_name(self):
        pass

    @abstractproperty
    def osl_name(self):
        pass

    @abstractproperty
    def glsl_name(self):
        pass

    