from abc import ABC, abstractmethod, abstractproperty


class SocketType(ABC):

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
    def osl_default(self):
        pass

    @abstractproperty
    def svm_name(self):
        pass

    @abstractproperty
    def glsl_name(self):
        pass

    @abstractproperty
    def definition_name(self):
        pass

    @abstractmethod
    def has_min(self):
        pass

    @abstractproperty
    def default_min(self):
        pass

    @abstractmethod
    def has_max(self):
        pass

    @abstractproperty
    def default_max(self):
        pass

    @abstractmethod
    def has_default(self):
        pass

    @abstractproperty
    def default_default(self):
        pass
