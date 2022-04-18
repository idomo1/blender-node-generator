from node_types.socket_type import SocketType

class ColorSocket(SocketType):

    @property
    def type_name(self):
        return "Color"

    @property
    def property_name(self):
        return "float3"

    @property
    def osl_name(self):
        return "point"
    
    @property
    def osl_default(self):
        return "0.0"
    
    @property
    def svm_name(self):
        return "float3"
    
    @property
    def glsl_name(self):
        return "vec4"
    
    @property
    def definition_name(self):
        return "COLOR"

    def has_min(self):
        return False

    @property
    def default_min(self):
        return "0.0f"

    def has_max(self):
        return False

    @property
    def default_max(self):
        return "1.0f"

    def has_default(self):
        return True

    @property
    def default_default(self):
        return "0.0f"
