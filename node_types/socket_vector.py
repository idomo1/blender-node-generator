from node_types.socket_type import SocketType

class VectorSocket(SocketType):
    @property
    def type_name(self):
        return "Vector"

    @property
    def property_name(self):
        return "float3"

    @property
    def osl_name(self):
        return "point"
    
    @property
    def osl_default(self):
        return "point(0.0, 0.0, 0.0)"
    
    @property
    def svm_name(self):
        return "float3"
    
    @property
    def glsl_name(self):
        return "vec3"
    
    @property
    def definition_name(self):
        return "POINT"

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
