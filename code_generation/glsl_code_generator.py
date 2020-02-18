from itertools import chain
from os import path

from . import code_generator_util


class GLSLCodeManager:
    """
    Generates GLSL related code
    Keeps GLSL parameters consistent between files
    """

    def __init__(self, gui):
        self._props = gui.get_props()
        self._node_name = gui.get_node_name()
        self._is_texture_node = gui.get_node_type() == 'Texture'
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._uses_texture_mapping = gui.uses_texture_mapping()
        self._node_type = gui.get_node_type()
        self._dropdowns = list(filter(lambda p: p['data-type'] == 'Enum', self._props))
        self._sockets = gui.get_node_sockets()
        self._source_path = gui.get_source_path()

    def _dropdowns_count(self):
        return len(self._dropdowns)

    def _get_dropdowns(self):
        return self._dropdowns

    def _generate_shader_func_names(self):
        func_name = '"node_{name}_{options}"'.format(
            name=code_generator_util.string_lower_underscored(self._node_name),
            options='{options}'
        )

        if self._dropdowns_count() == 0:
            return ['']
        elif self._dropdowns_count() == 1:
            return [func_name.format(
                name=self._node_name,
                options=code_generator_util.string_lower_underscored(option['name'])
            ) for option in self._get_dropdowns()[0]['options']]
        elif self._dropdowns_count() == 2:
            return [
                [func_name.format(
                    options='{option1}_{option2}'.format(option1=option1['name'], option2=option2['name'])) for option2
                    in self._get_dropdowns()[1]['options']] for option1 in self._get_dropdowns()[0]['options']
            ]
        else:
            return ['/* glsl func name */']

    def _generate_names_array(self):
        if self._dropdowns_count() == 1:
            return 'static const char *names[] = {{' \
                   '"",' \
                   '{funcs},' \
                   '}};\n\n'.format(
                funcs=','.join(self._generate_shader_func_names())
            )
        elif self._dropdowns_count() == 2:
            return 'static const char *names[][{options_count}] = {{' \
                   '{names}' \
                   '}};\n\n'.format(
                options_count=len(self._get_dropdowns()[0]['options']),
                names=''.join('[{enum}] = {{'
                              '"",'
                              '{names},'
                              '}},'.format(enum='SHD_{NODE_NAME}_{OPTION}'.format(
                    NODE_NAME=code_generator_util.string_upper_underscored(self._node_name),
                    OPTION=code_generator_util.string_upper_underscored(option['name'])
                ),
                    names=','.join(names)) for names, option in
                              zip(self._generate_shader_func_names(), self._get_dropdowns()[0]['options']))
            )
        else:
            return ''

    def _generate_assertions(self):
        assertions = []
        custom_i = 1
        for prop in self._get_dropdowns():
            if code_generator_util.uses_dna(self._props, self._node_type):
                assertions.append('BLI_assert({struct}->{prop} >= 0 && {struct}->{prop} < {option_count});'.format(
                    struct='tex' if self._is_texture_node else 'attr',
                    prop=code_generator_util.string_lower_underscored(prop['name']),
                    option_count=len(prop['options']) + 1))
            else:
                assertions.append('BLI_assert(node->custom{i} >= 0 && node->custom{i} < {option_count});'.format(
                    i=custom_i, option_count=len(prop['options']) + 1
                ))
                custom_i += 1

        if len(assertions) > 0:
            assertions.append('\n\n')

        return ''.join(assertions)

    def _generate_retrieve_props(self):
        retrieved_props = []
        if code_generator_util.uses_dna(self._props, self._node_type):
            struct = 'tex' if self._is_texture_node else 'attr'
            retrieved_props.append('Node{Suff}{Name} *{struct} = (Node{Suff}{Name} *)node->storage;'.format(
                Suff=self._type_suffix_abbreviated.capitalize(),
                Name=code_generator_util.string_capitalized_no_space(self._node_name),
                struct=struct
            ))
            for prop in self._props:
                prop_name = code_generator_util.string_lower_underscored(prop['name'])
                if prop['data-type'] == 'Boolean':
                    retrieved_props.append('float {name} = ({struct}->{name}) ? 1.0f : 0.0f;'.format(
                        name=prop_name,
                        struct=struct))
                elif prop['data-type'] != 'String' and prop['data-type'] != 'Enum':
                    retrieved_props.append('float {name} = {struct}->{name};'.format(
                        name=prop_name,
                        struct=struct))
        else:
            struct = 'node'
            s_custom_i = 1
            f_custom_i = 3
            boolean_bit = 0
            for prop in self._props:
                prop_name = code_generator_util.string_lower_underscored(prop['name'])
                if prop['data-type'] == 'Boolean':
                    # Need to get individual bits if multiple bools
                    if len([prop for prop in self._props if prop['data-type'] == 'Boolean']) > 1:
                        retrieved_props.append(
                            'float {name} = ({struct}->custom{i}) ? 1.0f : 0.0f;'.format(name=prop_name,
                                                                                         struct=struct,
                                                                                         i=s_custom_i))
                    else:
                        retrieved_props.append(
                            'float {name} = ({struct}->custom{i} >> {boolean_bit} & 1) ? 1.0f : 0.0f;'.format(
                                name=prop_name,
                                struct=struct,
                                i=s_custom_i,
                                boolean_bit=boolean_bit))
                        boolean_bit += 1
                elif prop['data-type'] == 'Float':
                    retrieved_props.append('float {name} = node->custom{i};'.format(name=prop_name,
                                                                                    struct=struct,
                                                                                    i=f_custom_i))
                    f_custom_i += 1
                elif prop['data-type'] == 'Int':
                    retrieved_props.append('float {name} = node->custom{i};'.format(name=prop_name,
                                                                                    struct=struct,
                                                                                    i=s_custom_i))
                    s_custom_i += 1

        if len(retrieved_props) > 0:
            retrieved_props.append('\n\n')
        return '{props}{assertions}'.format(props=''.join(retrieved_props), assertions=self._generate_assertions())

    def _generate_get_function_name(self):
        if self._dropdowns_count() == 0:
            return '"node_{name}"'.format(
                name=code_generator_util.string_lower_underscored(self._node_name)
            )
        elif self._dropdowns_count() == 1:
            if code_generator_util.uses_dna(self._props, self._node_type):
                return 'names[{struct}->{name}]'.format(
                    struct='tex' if self._is_texture_node else 'attr',
                    name=code_generator_util.string_lower_underscored(self._get_dropdowns()[0]['name'])
                )
            else:
                return 'names[node->custom1]'
        elif self._dropdowns_count() == 2:
            if code_generator_util.uses_dna(self._props, self._node_type):
                return 'names[{struct}->{drop1}][{struct}->{drop2}]'.format(
                    struct='tex' if self._is_texture_node else 'attr',
                    drop1=code_generator_util.string_lower_underscored(self._get_dropdowns()[0]['name']),
                    drop2=code_generator_util.string_lower_underscored(self._get_dropdowns()[1]['name'])
                )
            else:
                return 'names[node->custom1][node->custom2]'
        else:
            return '/* glsl func name */'

    def _generate_additional_params(self):
        """
        Additional parameters passed to the glsl shader
        Most commonly properties
        """
        return ['GPU_constant(&{prop})'.format(
            prop=code_generator_util.string_lower_underscored(prop['name'])) for prop in
            list(filter(lambda p: p['data-type'] != 'Enum' and p['data-type'] != 'String', self._props))]

    def _generate_return_statement(self):
        """Generates the return statement of the gpu function"""
        additional_params = self._generate_additional_params()
        return 'return GPU_stack_link(mat, node, {func_name}, in, out{other_params});'.format(
            func_name=self._generate_get_function_name(),
            other_params=', {params}'.format(params=', '.join(additional_params)) if len(additional_params) > 0 else ''
        )

    def generate_gpu_func(self):
        """gpu func in node_shader_*.c"""
        gpu_text = 'static int gpu_shader_{suff}{name}(GPUMaterial *mat,' \
                   ' bNode *node, ' \
                   'bNodeExecData *UNUSED(execdata), ' \
                   'GPUNodeStack *in, ' \
                   'GPUNodeStack *out)' \
                   '{{' \
                   '{texture_mapping}' \
                   '{func_names}' \
                   '{dna}' \
                   '{return_statement}' \
                   '}};\n\n'.format(
            suff='{suff}_'.format(suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
            name=code_generator_util.string_lower_underscored(self._node_name),
            texture_mapping='node_shader_gpu_default_tex_coord(mat, '
                            'node, &in[0].link);'
                            'node_shader_gpu_tex_mapping(mat, node, in, out);'
                            '\n\n' if self._uses_texture_mapping else '',
            func_names=self._generate_names_array(),
            dna=self._generate_retrieve_props(),
            return_statement=self._generate_return_statement(),
            other_params=''.join(self._generate_additional_params()))
        return gpu_text

    def _generate_glsl_shader(self):
        if self._dropdowns_count() > 2:
            return '// glsl functions'
        type_map = {'Vector': 'vec3', 'Float': 'float', 'Int': 'float', 'Boolean': 'float',
                    'RGBA': 'vec4', 'Shader': 'Closure'}
        params = ','.join('{out}{type} {name}'.format(
            type=type_map[param['data-type']],
            out='out ' if 'type' in param and param['type'] == 'Output' else '',
            # Must check if 'type' is a key since props don't have 'type' key
            name=code_generator_util.string_lower_underscored(param['name']))
                          for param in
                          [prop for prop in self._props if prop['data-type'] not in ['Enum', 'String']] +
                          [socket for socket in self._sockets if socket['data-type'] != 'String'])
        if self._dropdowns_count() == 0:
            return 'void node_{name}({params}){{}}'.format(
                name=code_generator_util.string_lower_underscored(self._node_name),
                params=params
            )
        else:
            func_names = self._generate_shader_func_names()

            return '\n\n'.join('void {func_name}({params})'
                               '{{'
                               '}}'.format(
                func_name=func_name.replace('"', ''),
                params=params
            ) for func_name in (func_names if self._dropdowns_count() == 1 else chain.from_iterable(func_names)))

    def add_glsl_shader(self):
        file_path = path.join(self._source_path, "source", "blender", "gpu", "shaders", "material",
                              "gpu_shader_material_{suff}{name}.glsl".format(
                                  suff='{suff}_'.format(
                                      suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                  name=code_generator_util.string_lower_underscored(self._node_name)
                              ))
        with open(file_path, 'w') as f:
            f.write('{0}\n'.format(self._generate_glsl_shader()))
        code_generator_util.apply_clang_formatting(file_path, self._source_path)
