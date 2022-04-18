from os import path
from sys import flags
from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp
from node_types.prop_int import IntProp

from node_types.socket_vector import VectorSocket

from node_types.socket_color import ColorSocket

import code_generation.code_generator_util as code_generator_util
from code_generation.glsl_writer import GLSLWriter
from code_generation.node_register_writer import NodeRegisterWriter


class NodeDefinitionWriter:
    """Writes node_shader_*.c"""
    def __init__(self, gui):
        self._node_register_writer = NodeRegisterWriter(gui)
        self._glsl_writer = GLSLWriter(gui)
        self._node_sockets = gui.get_node_sockets()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._node_name = gui.get_node_name()
        self._node_has_properties = gui.node_has_properties()
        self._props = gui.get_props()
        self._node_type = gui.get_node_type()
        self._is_texture_node = gui.is_texture_node()
        self._uses_texture_mapping = gui.uses_texture_mapping()
        self._source_path = gui.get_source_path()
    
    def _generate_node_namespace(self):
        return 'namespace blender::nodes::node_shader_{suff}{name}_cc {{\n\n'.format(
            suff="{suff}_".format(suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                  name=code_generator_util.string_lower_underscored(
                                      self._node_name)
        )

    def _generate_node_shader_sockets(self):
        """
        Generates node socket definition function code
        :return: socket definition code as text, or empty string if no sockets
        """
        sockets = self._node_sockets
        if len(sockets) == 0:
            return ''
        sockets_in = []
        sockets_out = []
        out = ['static void node_declare(NodeDeclarationBuilder &b)\n{\n']
        for sock in sockets:
            socket_text = 'b.add_{type}<decl::{Type}>(N_("{Name}")){options};\n'.format(
                type=sock['type'].lower(),
                Type=sock['data-type'].type_name.capitalize(),
                Name=code_generator_util.string_capitalized_spaced(sock['name']),
                options='{min}{max}{default}{flags}'.format(
                    min='.min({})'.format(sock['min']) if 'min' in sock else '',
                    max='.max({})'.format(sock['max']) if 'max' in sock else '',
                    default='.default_value({})'.format(
                        '{{}}'.format(sock['default']) if isinstance(sock['data-type'], (VectorSocket, ColorSocket)) else sock['default']
                        ) if 'default' in sock else '',
                    flags=self._generate_flags(sock)
                    )
            )

            if sock['type'] == "Input":
                sockets_in.append(socket_text)
            else:
                sockets_out.append(socket_text)
        
        for in_socket_text in sockets_in:
            out.append(in_socket_text)
        for out_socket_text in sockets_out:
            out.append(out_socket_text)

        out.append('}\n\n')
        return ''.join(out)
    
    def _generate_flags(self, socket):
        return ''.join('.{0}()'.format(flag) for flag in socket['flags'])

    def _generate_node_shader_init(self):
        """
        Generates node init function code
        :return: init function code as text
        """

        if not self._node_has_properties:
            return ''

        prop_init = ''
        uses_dna = code_generator_util.uses_dna(self._props, self._node_type)
        if uses_dna:
            struct = 'tex' if self._is_texture_node else 'attr'
            defaults = []
            for prop in self._props:
                if isinstance(prop['data-type'], EnumProp):
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default='SHD_{NAME}_{PROP}'.format(
                            NAME=code_generator_util.string_upper_underscored(
                                self._node_name),
                            PROP=code_generator_util.string_upper_underscored(
                                prop['default']))))
                elif isinstance(prop['data-type'], (BoolProp, IntProp)):
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default=prop['default']))

            prop_init = ''.join(defaults)
        else:  # Use custom
            defaults = []
            s_custom_i = 1
            boolean_bit = 0
            for prop in self._props:
                if isinstance(prop['data-type'], EnumProp):
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i,
                                                                          default='SHD_{NAME}_{PROP}'.format(
                                                                              NAME=code_generator_util.string_upper_underscored(
                                                                                  self._node_name),
                                                                              PROP=code_generator_util.string_upper_underscored(
                                                                                  prop['default']))))
                    s_custom_i += 1
                elif isinstance(prop['data-type'], IntProp):
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    s_custom_i += 1
                elif isinstance(prop['data-type'], BoolProp):
                    # Need to set bits if multiple bools
                    if len([prop for prop in self._props if isinstance(prop['data-type'], BoolProp)]) == 1:
                        defaults.append(
                            'node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    else:
                        # Set nth bit
                        defaults.append('node->custom{i} |= {default} << {boolean_bit};'.format(
                            i=s_custom_i,
                            default=int(prop['default']),
                            boolean_bit=boolean_bit))
                        boolean_bit += 1

            prop_init = ''.join(defaults)

        init_func = 'static void node_shader_init_{suff}{name}(bNodeTree *UNUSED(ntree), bNode *node){{' \
                    '{get_storage}' \
                    '{texture_mapping}' \
                    '{prop_init}\n\n' \
                    '{set_storage}' \
                    '}}\n\n'.format(
            suff='{suff}_'.format(
                suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
            name=code_generator_util.string_lower_underscored(self._node_name),
            get_storage='Node{Suff}{Name} *{struct} = MEM_cnew<Node{Suff}{Name}>(__func__);'.format(
                Suff=self._type_suffix_abbreviated.capitalize(),
                Name=code_generator_util.string_capitalized_no_space(self._node_name),
                struct=struct) if uses_dna else '',
            Name=code_generator_util.string_capitalized_no_space(
                self._node_name),
            texture_mapping='BKE_texture_mapping_default(&tex->base.tex_mapping, TEXMAP_TYPE_POINT);'
                            'BKE_texture_colormapping_default(&tex->base.color_mapping);'
            if self._uses_texture_mapping else '',
            prop_init=prop_init,
            set_storage='node->storage = {struct};'.format(struct=struct) if uses_dna else '')
        return init_func

    def write_node_definition_file(self):
        """node_shader_*.cc"""
        file_path = path.join(self._source_path, "source", "blender", "nodes", "shader", "nodes",
                              "node_shader_{suff}{name}.cc".format(
                                  suff="{suff}_".format(
                                      suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                  name=code_generator_util.string_lower_underscored(
                                      self._node_name)))
        with open(file_path, "w") as f:
            code_generator_util.write_license(f)

            file_lines = ['', '#include "node_shader_util.hh"\n\n', '\n\n'.
                format(NAME=code_generator_util.string_upper_underscored(self._node_name))]

            file_lines.append(self._generate_node_namespace())

            file_lines.append(self._generate_node_shader_sockets())

            file_lines.append(self._generate_node_shader_init())

            file_lines.append(self._glsl_writer.generate_gpu_func())

            file_lines.append('\n}\n')

            file_lines.append(self._node_register_writer.generate_node_shader_register())

            f.writelines(file_lines)

        code_generator_util.apply_clang_formatting(file_path, self._source_path)
