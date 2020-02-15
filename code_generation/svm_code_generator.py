from os import path

from . import code_generator_util


class SVMCompilationManager:
    """
    Generates code related to SVM
    Keeps svm parameters consistent between files
    """

    def __init__(self, gui):
        self._props = gui.get_props()
        self._sockets = gui.get_node_sockets()
        self._node_name = gui.get_node_name()
        self._is_texture_node = gui.is_texture_node()
        self._uses_texture_mapping = gui.uses_texture_mapping()
        self._source_path = gui.get_source_path()
        self._node_group_level = gui.get_node_group_level()

    def _generate_param_names(self):
        """How the props/sockets are passed to the compiler"""
        names = []
        for prop in self._props:
            if prop['data-type'] == 'Float':
                names.append(
                    '__float_as_int({name})'.format(name=code_generator_util.string_lower_underscored(prop['name'])))
            elif prop['data-type'] != 'String':
                names.append(code_generator_util.string_lower_underscored(prop['name']))
        for socket in self._sockets:
            names.append('{name}_stack_offset'.format(name=socket['name']))
        return names

    def _generate_svm_params(self):
        """Generates svm node parameters"""
        param_names = self._generate_param_names()
        uchar4 = 'compiler.encode_uchar4({params})'
        if len(param_names) < 4:
            return ', '.join(param_names)
        elif len(param_names) == 4:
            return ', '.join([', '.join(param_names[:2]), uchar4.format(params=', '.join(param_names[2:]))])
        elif len(param_names) == 5:
            return ', '.join([uchar4.format(params=', '.join(param_names[:2])),
                              uchar4.format(params=', '.join(param_names[2:4])),
                              param_names[-1]])
        elif len(param_names) == 6:
            return ', '.join([uchar4.format(params=', '.join(param_names[:3])),
                              uchar4.format(params=', '.join(param_names[3:]))])
        elif len(param_names) == 7:
            return ', '.join([uchar4.format(params=', '.join(param_names[:3])),
                              uchar4.format(params=', '.join(param_names[3:6])),
                              param_names[-1]])
        elif len(param_names) == 8:
            return ', '.join([uchar4.format(params=', '.join(param_names[:4])),
                              uchar4.format(params=', '.join(param_names[4:7])),
                              param_names[-1]])
        elif len(param_names) == 9:
            return ', '.join([uchar4.format(params=', '.join(param_names[:4])),
                              uchar4.format(params=', '.join(param_names[4:8])),
                              param_names[-1]])
        elif len(param_names) >= 10 and len(param_names) <= 12:
            return ', '.join(uchar4.format(
                params=', '.join(
                    param_names[i:(i + 4) if i + 4 < len(param_names) else 2 * (i + 4) - len(param_names)]))
                             for i in range(0, len(param_names), 4))
        elif len(param_names) > 12:
            raise Exception("Only 12 Props + Sockets Supported")
        else:
            raise Exception("Invalid number of prop + sockets {0}".format(len(param_names)))

    def _generate_get_sockets(self):
        """Generate retrieving """
        return ''.join('Shader{Type} *{name}_{type} = {type}put("{Name}");'.format(
            Type=socket['type'].capitalize(),
            name=code_generator_util.string_lower_underscored(socket['name']),
            type=socket['type'][:-3].lower(),
            Name=code_generator_util.string_capitalized_spaced(socket['name'])) for socket in self._sockets)

    def _generate_stack_offsets(self):

        def is_first_vector(socket, sockets):
            return socket == list(filter(lambda s: s['data-type'] == 'Vector' and s['type'] == 'Input', sockets))[0]

        socket_type_map = {"Input": 'in', "Output": 'out'}

        stack_offsets = []
        for socket in self._sockets:
            if socket['data-type'] == 'Vector' and self._is_texture_node and is_first_vector(socket, self._sockets):
                stack_offsets.append('int {name}_stack_offset = tex_mapping.compile_begin(compiler, {name}_in);'.format(
                    name=code_generator_util.string_lower_underscored(socket['name'])))
            elif socket['data-type'] == 'Float' and socket['type'] == 'Input':
                stack_offsets.append('int {name}_stack_offset = compiler.stack_assign_if_linked({name}_in);'.format(
                    name=code_generator_util.string_lower_underscored(socket['name'])))
            else:
                stack_offsets.append('int {name}_stack_offset = compiler.stack_assign({name}_{type});'.format(
                    name=code_generator_util.string_lower_underscored(socket['name']),
                    type=socket_type_map[socket['type']]))
        return ''.join(stack_offsets)

    def _generate_float_optimizations(self):
        """Generate code for passing floats directly to shader for optimization"""
        inputs = ['__float_as_int({socket})'.format(socket=code_generator_util.string_lower_underscored(socket['name']))
                  for socket in self._sockets if socket['data-type'] == 'Float' and socket['type'] == 'Input']

        return ''.join('compiler.add_node({params});'.format(
            params=', '.join(inputs[i:(i + 4) if i + 4 < len(inputs) else 2 * (i + 4) - len(inputs)])) for i in
                       range(0, len(inputs), 4))

    def _generate_add_node(self):
        return 'compiler.add_node(NODE_{TEX}{NAME}, ' \
               '{params});{optimizations}'.format(
            TEX='TEX_' if self._is_texture_node else '',
            NAME=code_generator_util.string_upper_underscored(self._node_name),
            params=self._generate_svm_params(),
            optimizations=self._generate_float_optimizations())

    def generate_svm_compile_func(self):
        """SVM compile function for nodes.cpp"""
        if self._uses_texture_mapping:
            first_input_vector = \
                list(filter(lambda s: s['data-type'] == 'Vector' and s['type'] == 'Input', self._sockets))[0]

        return 'void {Name}{Tex}Node::compile(SVMCompiler &compiler)' \
               '{{' \
               '{body}' \
               '{texture_mapping}' \
               '}}\n\n'.format(Name=code_generator_util.string_capitalized_no_space(self._node_name),
                               Tex='Texture' if self._is_texture_node else '',
                               body='\n\n'.join(
                                   [self._generate_get_sockets(), self._generate_stack_offsets(),
                                    self._generate_add_node()]),
                               texture_mapping='\n\ntex_mapping.compile_end(compiler, {name}_in, {name}_stack_offset);'.format(
                                   name=code_generator_util.string_lower_underscored(first_input_vector['name'])
                               ) if self._uses_texture_mapping else '')

    def _passed_params_count(self):
        """Returns the no. of props/sockets passed to the shader"""
        return len(list(filter(lambda p: p['data-type'] != 'String', self._props + self._sockets)))

    def _unpack_names(self):
        def unpack_name(item):
            name = code_generator_util.string_lower_underscored(item['name'])
            if item['data-type'] in ['Boolean', 'Int', 'Enum']:
                return name
            elif item['data-type'] != 'String':
                return '{name}_stack_offset'.format(name=name)

        return [unpack_name(item) for item in self._props + self._sockets if item['data-type'] != 'String']

    def _generate_offset_definitions(self):
        names = self._unpack_names()

        offset_def = 'uint {names};'

        if len(names) < 4:
            return ''
        if len(names) == 4:
            return offset_def.format(names=', '.join(names[2:]))
        elif len(names) == 5:
            return offset_def.format(names=', '.join(names[:4]))
        elif len(names) == 6:
            return ''.join([offset_def.format(names=', '.join(names[:3])),
                            offset_def.format(names=', '.join(names[3:]))])
        elif len(names) == 7:
            return ''.join([offset_def.format(names=', '.join(names[:3])),
                            offset_def.format(names=', '.join(names[3:6]))])
        elif len(names) == 8 or len(names) == 9:
            return ''.join([offset_def.format(names=', '.join(names[:4])),
                            offset_def.format(names=', '.join(names[4:8]))])
        elif len(names) >= 10 and len(names) <= 12:
            return ''.join([offset_def.format(
                names=', '.join(names[i:(i + 4) if i + 4 < len(names) else 2 * (i + 4) - len(names)]))
                for i in range(0, len(names), 4)])
        elif len(names) > 12:
            raise Exception("Only 12 Props + Sockets Supported")
        else:
            raise Exception("Invalid number of prop + sockets {0}".format(len(names)))

    def _generate_unpack(self):
        names = self._unpack_names()
        unpack_uchar = 'svm_unpack_uchar{count}(stack_offsets{offset_count}, {params});'

        if len(names) < 4:
            return ''
        elif len(names) == 4:
            return unpack_uchar.format(
                count=2,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[2:])
            )
        elif len(names) == 5:
            return ''.join([unpack_uchar.format(
                count=2,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[:2])
            ), unpack_uchar.format(
                count=2,
                offset_count=2,
                params=', '.join('&{name}'.format(name=name) for name in names[2:4])
            )])
        elif len(names) == 6:
            return ''.join([unpack_uchar.format(
                count=3,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[:3])
            ), unpack_uchar.format(
                count=3,
                offset_count=2,
                params=', '.join('&{name}'.format(name=name) for name in names[3:])
            )])
        elif len(names) == 7:
            return ''.join([unpack_uchar.format(
                count=3,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[:3])
            ), unpack_uchar.format(
                count=3,
                offset_count=2,
                params=', '.join('&{name}'.format(name=name) for name in names[3:6])
            )
            ])
        elif len(names) == 8:
            return ''.join([unpack_uchar.format(
                count=4,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[:4])
            ), unpack_uchar.format(
                count=3,
                offset_count=2,
                params=', '.join('&{name}'.format(name=name) for name in names[4:7])
            )
            ])
        elif len(names) == 9:
            return ''.join([unpack_uchar.format(
                count=4,
                offset_count=1,
                params=', '.join('&{name}'.format(name=name) for name in names[:4])
            ), unpack_uchar.format(
                count=4,
                offset_count=2,
                params=', '.join('&{name}'.format(name=name) for name in names[4:8])
            )
            ])
        elif len(names) >= 10 and len(names) <= 12:
            return ''.join([unpack_uchar.format(
                count=4 if i + 4 <= len(names) else i + 4 - len(names),
                offset_count=i // 4 + 1,
                params=', '.join('&{name}'.format(
                    name=name) for name in names[i:(i + 4) if i + 4 < len(names) else 2 * (i + 4) - len(names)]))
                for i in range(0, len(names), 4)
            ])
        elif len(names) > 12:
            raise Exception("Only 12 Props + Sockets Supported")
        else:
            raise Exception("Invalid number of prop + sockets {0}".format(len(names)))

    def _generate_load_params(self):
        load = ['uint4 defaults{i} = read_node(kg, offset);'.format(i=i // 4 + 1) for i in range(0, len(
            [socket for socket in self._sockets if socket['type'] == 'Input' and socket['data-type'] == 'Float']), 4)]
        if len(load) > 0:
            load.append('\n\n')

        float_i = 0
        type_map = {'Float': 'float', 'Vector': 'float3', 'RGBA': 'float3', 'Int': 'int', 'Shader': 'float3'}
        for socket in self._sockets:
            if socket['type'] == 'Input':
                load.append(
                    '{type} {name} = stack_load_{type}{default}(stack, {name}_stack_offset{default_address});'.format(
                        type=type_map[socket['data-type']],
                        name=code_generator_util.string_lower_underscored(socket['name']),
                        default='_default' if socket['data-type'] == 'Float' else '',
                        default_address=', {node}.{address}'.format(
                            node='defaults{i}'.format(i=float_i // 4 + 1),
                            address=['x', 'y', 'z', 'w'][float_i % 4]) if socket['data-type'] == 'Float' else ''
                    ))
                if socket['data-type'] == 'Float':
                    float_i += 1
        return ''.join(load)

    def _generate_shader_params(self):
        """Parameters in shader"""
        num_params = self._passed_params_count()
        items = self._props + self._sockets
        if num_params < 4:
            params = ', '.join('uint {name}'.format(
                name=code_generator_util.string_lower_underscored(item['name'])) for item in items)
        elif num_params == 4:
            params = ', '.join('uint {name}'.format(
                name=code_generator_util.string_lower_underscored(item['name'])) for item in items[:2]
                               ) + ', uint stack_offsets'
        elif num_params == 5:
            params = 'uint stack_offsets1, uint stack_offsets2, uint ' + code_generator_util.string_lower_underscored(
                items[-1]['name'])
        elif num_params == 6:
            params = 'uint stack_offsets1, uint stack_offsets2'
        elif num_params == 7 or num_params == 8 or num_params == 9:
            params = 'uint stack_offsets1, uint stack_offsets2, uint ' + code_generator_util.string_lower_underscored(
                items[-1]['name'])
        elif num_params >= 10 and num_params <= 12:
            params = 'uint stack_offsets1, uint stack_offsets2, uint stack_offsets3'
        elif num_params > 12:
            raise Exception("Only 12 Props + Sockets Supported")
        else:
            raise Exception("Invalid number of prop + sockets {0}".format(num_params))

        return '{params}{offset}'.format(
            params=params,
            offset=', int *offset' if any(socket['data-type'] == 'Float' for socket in self._sockets) else '')

    def _generate_shader_file_name(self):
        return "svm_{name}".format(
            name=code_generator_util.string_lower_underscored(self._node_name)
        )

    def _generate_svm_shader(self):
        """Loading passed values in svm_*.h"""
        return 'CCL_NAMESPACE_BEGIN\n\n' \
               'ccl_device void svm_node_{tex}{name}(KernelGlobals *kg,' \
               'ShaderData *sd,' \
               'float *stack,' \
               '{params}' \
               ')' \
               '{{' \
               '{offset_defs}\n\n' \
               '{unpack_params}\n\n' \
               '{load_params}' \
               '}}\n\n' \
               'CCL_NAMESPACE_END\n\n'.format(tex='tex_' if self._is_texture_node else '',
                                              name=code_generator_util.string_lower_underscored(self._node_name),
                                              params=self._generate_shader_params(),
                                              offset_defs=self._generate_offset_definitions(),
                                              unpack_params=self._generate_unpack(),
                                              load_params=self._generate_load_params())

    def add_svm_shader(self):
        """svm_*.h"""
        file_path = path.join(self._source_path, "intern", "cycles", "kernel", "svm", "{shader_file_name}".format(
            shader_file_name=self._generate_shader_file_name()))
        with open(file_path, 'w') as f:
            code_generator_util.write_license(f)
            f.write(self._generate_svm_shader())
        code_generator_util.apply_clang_formatting(file_path, self._source_path)

    def _generate_svm_shader_include(self):
        """Include statement for svm.h"""
        return '#include "kernel/svm/{shader_file_name}.h"\n'.format(
            shader_file_name=self._generate_shader_file_name())

    def _has_multiple_nodes(self):
        """Returns whether the shader requires multiple nodes for passing parameters"""
        param_count = 0
        for param in self._props + self._sockets:
            if param['data-type'] == 'Float':
                # Float optimizations are added in a separate node
                return True
            elif param['data-type'] != 'String':
                param_count += 1
        # 3 uchar4's = 3*4 = 12 max params for one node
        return param_count > 12

    def _generate_svm_shader_passed_params(self):
        """Params passed when the shader is called"""
        num_params = self._passed_params_count()
        if num_params in [2, 6]:
            return 'node.y, node.z'
        elif num_params > 2:
            return 'node.y, node.z, node.w'
        elif num_params == 1:
            return 'node.y'
        elif num_params == 0:
            return ''
        else:
            raise Exception("Invalid number of params {0}".format(num_params))

    def _generate_svm_shader_case(self):
        """Case to pass parameters to shader in svm.h"""
        return 'case NODE_{TEX}{NAME}:' \
               'svm_node_{tex}{name}(kg, sd, stack, {params}{offset});' \
               'break;\n'.format(
            TEX='TEX_' if self._is_texture_node else '',
            NAME=code_generator_util.string_upper_underscored(self._node_name),
            tex='tex_' if self._is_texture_node else '',
            name=code_generator_util.string_lower_underscored(self._node_name),
            params=self._generate_svm_shader_passed_params(),
            offset=', &offset' if self._has_multiple_nodes() else ''
        )

    def add_register_svm(self):
        """Include and register svm shader in svm.h"""
        file_path = path.join(self._source_path, "intern", "cycles", "kernel", "svm", "svm.h")
        with open(file_path, 'r+') as f:
            include_statement = self._generate_svm_shader_include()

            shader_case = self._generate_svm_shader_case()

            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == '#ifdef __SHADER_RAYTRACE__\n':
                    lines.insert(i - 1, include_statement)
                    break
            else:
                raise Exception("No match found")

            for i, line in enumerate(lines):
                if line == '    switch (node.x) {\n':
                    j = i
                    while lines[j] != '#if NODES_GROUP(NODE_GROUP_LEVEL_{group})\n'.format(
                            group=self._node_group_level):
                        j += 1

                    if self._is_texture_node:
                        while lines[j] != '#  ifdef __TEXTURES__\n':
                            j += 1
                    lines.insert(j + 1, shader_case)
                    break
            else:
                raise Exception("No match found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def _generate_enum_typedefs(self):
        """Generate enum typedefs"""
        return '\n\n'.join(['typedef enum Node{Name}{Prop} {{{options}}} Node{Name}{Prop};'.format(
            Name=code_generator_util.string_capitalized_no_space(self._node_name),
            Prop=code_generator_util.string_capitalized_no_space(prop['name']),
            options=','.join(['NODE_{NAME}_{OPTION} = {i}'.format(
                NAME=code_generator_util.string_upper_underscored(self._node_name),
                OPTION=code_generator_util.string_upper_underscored(option['name']),
                i=i + 1) for i, option in enumerate(prop['options'])]))
            for prop in self._props if prop['data-type'] == 'Enum'])

    def add_svm_types(self):
        """Register node types in svm_types.h"""
        file_path = path.join(self._source_path, "intern", "cycles", "kernel", "svm", "svm_types.h")
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == '} ShaderNodeType;\n':
                    lines.insert(i, 'NODE_{TEX}{NAME},'.format(
                        TEX='TEX_' if self._is_texture_node else '',
                        NAME=code_generator_util.string_upper_underscored(self._node_name)
                    ))
                    lines.insert(i+2, '\n')
                    lines.insert(i + 3, self._generate_enum_typedefs())
                    break
            else:
                raise Exception("Match not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._source_path)
