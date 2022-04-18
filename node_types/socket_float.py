from node_types.socket_type import SocketType

class FloatSocket(SocketType):
    @property
    def type_name(self):
        return "Float"

    @property
    def property_name(self):
        return "float"

    @property
    def osl_name(self):
        return "float"
    
    @property
    def osl_default(self):
        return "0.0"
    
    @property
    def svm_name(self):
        return "float"
    
    @property
    def glsl_name(self):
        return "float"
    
    @property
    def definition_name(self):
        return "FLOAT"

    def has_min(self):
        return True

    @property
    def default_min(self):
        return "0.0f"

    def has_max(self):
        return True

    @property
    def default_max(self):
        return "1.0f"

    def has_default(self):
        return True

    @property
    def default_default(self):
        return "0.0f"
