from os import path
from node_types.prop_enum import EnumProp

from node_types.socket_vector import VectorSocket

from node_types.socket_color import ColorSocket

import code_generation.code_generator_util as code_generator_util


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
        osl_path = path.join(self._source_path, "intern", "cycles", "kernel", "osl", "shaders",
                             "node_{name}{suffix}.osl".format(
                                 name=node_name_underscored,
                                 suffix='_{suffix}'.format(
                                     suffix=self._type_suffix) if self._type_suffix else ''
                             ))
        with open(osl_path, "w") as osl_f:
            code_generator_util.write_license(osl_f)

            osl_f.write('#include "stdcycles.h"\n\n')

            function = "shader node_{name}{suffix}({mapping}{props}{in_sockets}{out_sockets}){{}}\n".format(
                name=node_name_underscored,
                suffix='_{suffix}'.format(suffix=self._type_suffix) if self._type_suffix else '',
                mapping='int use_mapping = 0,matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                if self._uses_texture_mapping else '',
                props=''.join('{type} {name} = {default},'.format(
                    type=prop['data-type'].osl_name,
                    name=code_generator_util.string_lower_underscored(prop['name']),
                    default='"{default}"'.format(default=prop['default']) if isinstance(prop['data-type'], EnumProp) else prop['default'])
                              for prop in self._props),
                in_sockets=''.join(['{type} {name} = {default},'.format(
                    type=socket['data-type'].osl_name,
                    name=code_generator_util.string_capitalized_no_space(socket['name']),
                    default=socket['default'].replace('f', '') if not isinstance(socket['data-type'], (VectorSocket, ColorSocket)) else
                    'point({0})'.format(socket['default'].replace(',', ', ').replace('f', '')))
                    for socket in self._node_sockets if socket['type'] == 'Input']),
                out_sockets=','.join(
                    ['output {type} {name} = {default}'.format(
                        type=socket['data-type'].osl_name,
                        name=code_generator_util.string_capitalized_no_space(socket['name']),
                        default=socket['data-type'].osl_default)
                        for socket in self._node_sockets if socket['type'] == 'Output']))

            osl_f.write(function)
        code_generator_util.apply_clang_formatting(osl_path, self._source_path)
