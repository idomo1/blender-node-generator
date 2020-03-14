from os import path

from . import code_generator_util


class OSLWriter:
    """Writes OSL related code"""
    def __init__(self, gui):
        self._source_path = gui.get_source_path()
        self._node_name = gui.get_node_name()
        self._type_suffix = gui.type_suffix()
        self._node_sockets = gui.get_node_sockets()
        self._props = gui.get_props()
        self._uses_texture_mapping = gui.uses_texture_mapping()

    def write_osl_shader(self):
        """"""
        node_name_underscored = code_generator_util.string_lower_underscored(self._node_name)
        osl_path = path.join(self._source_path, "intern", "cycles", "kernel", "shaders",
                             "node_{name}{suffix}.osl".format(
                                 name=node_name_underscored,
                                 suffix='_{suffix}'.format(
                                     suffix=self._type_suffix) if self._type_suffix else ''
                             ))
        with open(osl_path, "w") as osl_f:
            code_generator_util.write_license(osl_f)

            # Must include stdcycles for closure type definition
            if any(sock['data-type'] == 'Shader' for sock in self._node_sockets):
                osl_f.write('#include "stdcycles.h"\n\n')
            else:
                osl_f.write('#include "stdosl.h"\n\n')

            type_conversion = {"Boolean": "int", "String": "string", "Int": "int", "Float": "float", "Enum": "string",
                               "Vector": "point", "RGBA": "point", 'Shader': 'closure color'}

            out_socket_default = {"RGBA": "0.0", "Shader": "0", "Vector": "point(0.0, 0.0, 0.0)", "Float": "0.0"}

            function = "shader node_{name}{suffix}({mapping}{props}{in_sockets}{out_sockets}){{}}\n".format(
                name=node_name_underscored,
                suffix='_{suffix}'.format(suffix=self._type_suffix) if self._type_suffix else '',
                mapping='int use_mapping = 0,matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                if self._uses_texture_mapping else '',
                props=''.join('{type} {name} = {default},'.format(
                    type=type_conversion[prop['data-type']],
                    name=code_generator_util.string_lower_underscored(prop['name']),
                    default='"{default}"'.format(default=prop['default']) if prop['data-type'] == 'Enum' else prop[
                        'default'])
                              for prop in self._props if prop['data-type'] != 'String'),
                in_sockets=''.join(['{type} {name} = {default},'.format(
                    type=type_conversion[socket['data-type']],
                    name=code_generator_util.string_capitalized_no_space(socket['name']),
                    default=socket['default'] if socket['data-type'] not in ['Vector', 'RGBA', 'Shader'] else
                    'point({0})'.format(socket['default'].replace(',', ', ')))
                    for socket in self._node_sockets if socket['type'] == 'Input' and socket['data-type'] != 'String']),
                out_sockets=','.join(
                    ['output {type} {name} = {default}'.format(
                        type=type_conversion[socket['data-type']],
                        name=code_generator_util.string_capitalized_no_space(socket['name']),
                        default=out_socket_default[socket['data-type']])
                        for socket in self._node_sockets if socket['type'] == 'Output']))

            osl_f.write(function)
        code_generator_util.apply_clang_formatting(osl_path, self._source_path)
