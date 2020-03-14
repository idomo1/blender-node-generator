from os import path

from . import code_generator_util
from . import GLSLWriter
from .node_register_writer import NodeRegisterWriter


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
        self._socket_availability_changes = gui.socket_availability_changes()
        self._socket_availability_maps = gui.get_socket_availability_maps()
        self._source_path = gui.get_source_path()

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
        out = []
        for sock in sockets:
            socket_text = '{{SOCK_{TYPE}, {input_count}, N_("{Name}"), {default}, {min}, {max}{subtype}{flag}}},'.format(
                TYPE=sock['data-type'].upper(), Name=code_generator_util.string_capitalized_spaced(sock['name']),
                input_count=1 if sock['type'] == 'Input' else 0,
                default=code_generator_util.fill_socket_default(sock['default'])
                if 'default' in sock else '0.0f, 0.0f, 0.0f, 0.0f',
                min=sock['min'] + 'f' if 'min' in sock else '0.0f',
                max=sock['max'] + 'f' if 'max' in sock else '1.0f',
                subtype=(', ' + sock['sub-type']) if sock['sub-type'] != 'PROP_NONE' or sock[
                    'flag'] != "None" else '',
                flag=(', ' + sock['flag']) if sock['flag'] != 'None' else '')
            if sock['type'] == "Input":
                sockets_in.append(socket_text)
            else:
                sockets_out.append(socket_text)
        if len(sockets_in) > 0:
            in_sockets_text = 'static bNodeSocketTemplate sh_node_{tex}{name}_in[] = {{{sockets}{{-1, 0, ""}},}};\n\n'.format(
                tex="{suff}_".format(
                    suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                name=code_generator_util.string_lower_underscored(self._node_name),
                sockets="".join(sockets_in))
            out.append(in_sockets_text)

        if len(sockets_out) > 0:
            out_sockets_text = 'static bNodeSocketTemplate sh_node_{tex}{name}_out[] = {{{sockets}{{-1, 0, ""}},}};\n\n'.format(
                tex="{suff}_".format(
                    suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                name=code_generator_util.string_lower_underscored(self._node_name),
                sockets="".join(sockets_out))
            out.append(out_sockets_text)
        return ''.join(out)

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
                if prop['data-type'] == 'Enum':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default='SHD_{NAME}_{PROP}'.format(
                            NAME=code_generator_util.string_upper_underscored(
                                self._node_name),
                            PROP=code_generator_util.string_upper_underscored(
                                prop['default']))))
                elif prop['data-type'] == 'Boolean' or prop['data-type'] == 'Int':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default=prop['default']))
                elif prop['data-type'] == 'Float':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default='{default}f'.format(default=prop['default'])))
            prop_init = ''.join(defaults)
        else:  # Use custom
            defaults = []
            s_custom_i = 1
            f_custom_i = 3
            boolean_bit = 0
            for prop in self._props:
                if prop['data-type'] == 'Enum':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i,
                                                                          default='SHD_{NAME}_{PROP}'.format(
                                                                              NAME=code_generator_util.string_upper_underscored(
                                                                                  self._node_name),
                                                                              PROP=code_generator_util.string_upper_underscored(
                                                                                  prop['default']))))
                    s_custom_i += 1
                elif prop['data-type'] == 'Int':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    s_custom_i += 1
                elif prop['data-type'] == 'Boolean':
                    # Need to set bits if multiple bools
                    if len([prop for prop in self._props if prop['data-type'] == 'Boolean']) == 1:
                        defaults.append(
                            'node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    else:
                        # Set nth bit
                        defaults.append('node->custom{i} |= {default} << {boolean_bit};'.format(
                            i=s_custom_i,
                            default=int(prop['default']),
                            boolean_bit=boolean_bit))
                        boolean_bit += 1
                elif prop['data-type'] == 'Float':
                    defaults.append('node->custom{i} = {default}f;'.format(i=f_custom_i, default=prop['default']))
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
            get_storage='Node{Suff}{Name} *{struct} = MEM_callocN(sizeof(Node{Suff}{Name}), "Node{Suff}{Name}");'.format(
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

    def _generate_node_shader_socket_availability(self):
        if not self._socket_availability_changes:
            return ''

        if len(self._props) == 0:
            return ''

        struct = 'tex' if self._is_texture_node else 'attr'

        in_sockets = []
        out_sockets = []
        socket_availability = []
        for map in self._socket_availability_maps:
            if any(not available for prop, available in map['prop-avail']):
                type = map['socket-type']
                socket_get = 'bNodeSocket *{type}{Name}Sock = nodeFindSocket(node, SOCK_{TYPE}, "{Name_Spaced}");'.format(
                    type=type,
                    Name=code_generator_util.string_capitalized_no_space(map['socket-name']),
                    TYPE=map['socket-type'].upper(),
                    Name_Spaced=code_generator_util.string_capitalized_spaced(map['socket-name']))
                if map['socket-type'] == 'in':
                    in_sockets.append(socket_get)
                else:
                    out_sockets.append(socket_get)

                constraints = []
                avail_count = sum(avail for prop, avail in map['prop-avail'])
                invert_avail = avail_count / len(map['prop-avail']) < 0.5
                if code_generator_util.uses_dna(self._props, self._node_type):
                    for prop, avail in map['prop-avail']:
                        prop_name, value = prop.split('=')
                        is_enum = not (value == 'False' or value == 'True')
                        if not invert_avail and not avail:
                            constraints.append('{struct}->{prop} != {value}'.format(
                                struct=struct,
                                prop=code_generator_util.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=code_generator_util.string_upper_underscored(self._node_name),
                                    OPTION=code_generator_util.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                        elif invert_avail and avail:
                            constraints.append('{struct}->{prop} == {value}'.format(
                                struct=struct,
                                prop=code_generator_util.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=code_generator_util.string_upper_underscored(self._node_name),
                                    OPTION=code_generator_util.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                else:
                    bool_count = len(list(filter(lambda p: p['data-type'] == 'Boolean', self._props)))
                    s_custom_i = 1
                    boolean_bit = 0
                    last_prop = None
                    last_prop_is_enum = None
                    for prop, avail in map['prop-avail']:
                        prop_name, value = prop.split('=')
                        is_enum = not (value == 'False' or value == 'True')

                        if last_prop is None:
                            last_prop = prop_name
                            last_prop_is_enum = is_enum

                        if prop_name != last_prop:
                            if not last_prop_is_enum:
                                boolean_bit += 1
                            else:
                                s_custom_i += 1
                        last_prop = prop_name
                        last_prop_is_enum = is_enum

                        if not invert_avail and not avail:
                            if not is_enum and bool_count > 1:
                                constraints.append('(node->custom{i} >> {bit}) & 1 != {value}'.format(
                                    i=s_custom_i,
                                    bit=boolean_bit,
                                    value=int(avail)
                                ))
                            else:
                                constraints.append('node->custom{i} != {value}'.format(
                                    i=s_custom_i,
                                    prop=code_generator_util.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=code_generator_util.string_upper_underscored(self._node_name),
                                        OPTION=code_generator_util.string_upper_underscored(value))
                                    if is_enum else int(value == 'True')))
                        elif invert_avail and avail:
                            if not is_enum and bool_count > 1:
                                constraints.append('(node->custom{i} >> {bit}) & 1 == {value}'.format(
                                    i=s_custom_i,
                                    bit=boolean_bit,
                                    value=int(avail)
                                ))
                            else:
                                constraints.append('node->custom{i} == {value}'.format(
                                    i=s_custom_i,
                                    prop=code_generator_util.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=code_generator_util.string_upper_underscored(self._node_name),
                                        OPTION=code_generator_util.string_upper_underscored(value))
                                    if is_enum else int(value == 'True')))
                socket_availability.append('nodeSetSocketAvailability({socket}, {constraints});'.format(
                    socket='{type}{Name}Sock'.format(
                        type=type,
                        Name=code_generator_util.string_capitalized_no_space(map['socket-name'])),
                    constraints=' || '.join(constraints) if invert_avail else ' && '.join(constraints)))

        if len(in_sockets) > 0:
            in_sockets.append('\n\n')
        if len(out_sockets) > 0:
            out_sockets.append('\n\n')
        get_struct = 'Node{Suff}{Name} *{struct} = (Node{Suff}{Name} *)node->storage;\n\n'.format(
            Suff=self._type_suffix_abbreviated.capitalize(),
            Name=code_generator_util.string_capitalized_no_space(self._node_name),
            struct='tex' if self._is_texture_node else 'attr')

        socket_availability_func = 'static void node_shader_update_{suff}{name}(bNodeTree *UNUSED(ntree), bNode *node)' \
                                   '{{' \
                                   '{in_sockets}' \
                                   '{out_sockets}' \
                                   '{struct}' \
                                   '{availability}' \
                                   '}}\n\n'.format(
            suff='{suff}_'.format(
                suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
            name=code_generator_util.string_lower_underscored(self._node_name),
            in_sockets=''.join(in_sockets),
            out_sockets=''.join(out_sockets),
            struct=get_struct if code_generator_util.uses_dna(self._props, self._node_type) else '',
            availability=''.join(socket_availability))
        return socket_availability_func

    def write_node_definition_file(self):
        """node_shader_*.c"""
        file_path = path.join(self._source_path, "source", "blender", "nodes", "shader", "nodes",
                              "node_shader_{suff}{name}.c".format(
                                  suff="{suff}_".format(
                                      suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                  name=code_generator_util.string_lower_underscored(
                                      self._node_name)))
        with open(file_path, "w") as f:
            code_generator_util.write_license(f)

            file_lines = ['', '#include "../node_shader_util.h"\n\n', '/**************** {NAME} ****************/\n\n'.
                format(NAME=code_generator_util.string_upper_underscored(self._node_name))]

            file_lines.append(self._generate_node_shader_sockets())

            file_lines.append(self._generate_node_shader_init())

            file_lines.append(self._glsl_writer.generate_gpu_func())

            file_lines.append(self._generate_node_shader_socket_availability())

            file_lines.append(self._node_register_writer.generate_node_shader_register())

            f.writelines(file_lines)

        code_generator_util.apply_clang_formatting(file_path, self._source_path)
