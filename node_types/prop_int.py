from node_types.prop_type import PropType

class IntProp(PropType):
    @property
    def type_name(self):
        return "Int"

    @property
    def property_name(self):
        return "int"

    @property
    def osl_name(self):
        return "int"

    @property
    def glsl_name(self):
        return "float"