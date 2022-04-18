from node_types.prop_type import PropType

class EnumProp(PropType):
    @property
    def type_name(self):
        return "Enum"

    @property
    def property_name(self):
        return "int"

    @property
    def osl_name(self):
        return "string"
    
    @property
    def glsl_name(self):
        return None
