from node_types.prop_type import PropType

class BoolProp(PropType):
    @property
    def type_name(self):
        return "Boolean"

    @property
    def property_name(self):
        return "bool"

    @property
    def osl_name(self):
        return "int"
    
    @property
    def glsl_name(self):
        return "float"
