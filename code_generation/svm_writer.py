from os import path
from socket import SocketType
from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp
from node_types.prop_int import IntProp

from node_types.socket_vector import VectorSocket

from node_types.socket_float import FloatSocket

import code_generation.code_generator_util as code_generator_util


class SVMWriter:
    """
    Writes code related to SVM
    Keeps svm parameters consistent between files
    """

    def __init__(self, gui):
        self._props = gui.get_props()
        self._sockets = gui.get_node_sockets()
        self._node_name = gui.get_node_name()
        self._is_texture_node = gui.is_texture_node()
        self._type_suffix = gui.type_suffix()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._uses_texture_mapping = gui.uses_texture_mapping()
        self._source_path = gui.get_source_path()

    def _generate_param_names(self):
        """How the props/sockets are passed to the compiler"""
        names = []
        for prop in self._props:
            names.append(code_generator_util.string_lower_underscored(
                code_generator_util.string_lower_underscored(prop['name'])))
        for socket in self._sockets:
            names.append(
                '{name}_stack_offset'.format(name=code_generator_util.string_lower_underscored(socket['name'])))
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

    def _generate_get_sockets(self):
        """Generate retrieving """
        return ''.join('Shader{Type} *{name}_{type} = {type}put("{Name}");'.format(
            Type=socket['type'].capitalize(),
            name=code_generator_util.string_lower_underscored(socket['name']),
            type=socket['type'][:-3].lower(),
            Name=code_generator_util.string_capitalized_spaced(socket['name'])) for socket in self._sockets)

    def _generate_stack_offsets(self):

        def is_first_vector(socket, sockets):
            return socket == list(filter(lambda s: isinstance(s['data-type'], VectorSocket) and s['type'] == 'Input', sockets))[0]

        socket_type_map = {"Input": 'in', "Output": 'out'}

        stack_offsets = []
        for socket in self._sockets:
            if isinstance(socket['data-type'], VectorSocket) and self._is_texture_node and socket['type'] == 'Input' and is_first_vector(socket, self._sockets):
                stack_offsets.append('int {name}_stack_offset = tex_mapping.compile_begin(compiler, {name}_in);'.format(
                    name=code_generator_util.string_lower_underscored(socket['name'])))
            elif isinstance(socket['data-type'], FloatSocket) and socket['type'] == 'Input':
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
                  for socket in self._sockets if isinstance(socket['data-type'], FloatSocket) and socket['type'] == 'Input']

        return ''.join('compiler.add_node({params});'.format(
            params=', '.join(inputs[i:(i + 4) if i + 4 < len(inputs) else 2 * (i + 4) - len(inputs)])) for i in
                       range(0, len(inputs), 4))

    def _generate_add_node(self):
        # TODO For nodes with less than 3 params, add any float optimizations to the same node
        return 'compiler.add_node(NODE_{SUFF}{NAME}, ' \
               '{params});{optimizations}'.format(
            SUFF='{SUFF}_'.format(SUFF=self._type_suffix_abbreviated.upper()) if self._type_suffix_abbreviated else '',
            NAME=code_generator_util.string_upper_underscored(self._node_name),
            params=self._generate_svm_params(),
            optimizations=self._generate_float_optimizations()) if len(self._props) + len(self._sockets) < 13 else ''

    def generate_svm_compile_func(self):
        """SVM compile function for nodes.cpp"""
        if self._uses_texture_mapping:
            first_input_vector = \
                list(filter(lambda s: isinstance(s['data-type'], VectorSocket) and s['type'] == 'Input', self._sockets))[0]

        return 'void {Name}{Suffix}Node::compile(SVMCompiler &compiler)' \
               '{{' \
               '{body}' \
               '{texture_mapping}' \
               '}}\n\n'.format(Name=code_generator_util.string_capitalized_no_space(self._node_name),
                               Suffix=self._type_suffix.capitalize(),
                               body='\n\n'.join(
                                   [self._generate_get_sockets(), self._generate_stack_offsets(),
                                    self._generate_add_node()]),
                               texture_mapping='\n\ntex_mapping.compile_end(compiler, {name}_in, {name}_stack_offset);'.format(
                                   name=code_generator_util.string_lower_underscored(first_input_vector['name'])
                               ) if self._uses_texture_mapping else '')

    def _passed_params_count(self):
        """Returns the no. of props/sockets passed to the shader"""
        return len(self._props) + len(self._sockets)

    def _unpack_names(self):
        def unpack_name(item):
            name = code_generator_util.string_lower_underscored(item['name'])
            if isinstance(item['data-type'], (BoolProp, IntProp, EnumProp)):
                return name
            else:
                return '{name}_stack_offset'.format(name=name)

        return [unpack_name(item) for item in self._props + self._sockets]

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

    def _generate_unpack(self):
        names = self._unpack_names()
        unpack_uchar = 'svm_unpack_node_uchar{count}(stack_offsets{offset_count}, {params});'

        if len(names) < 4:
            return ''
        elif len(names) == 4:
            return unpack_uchar.format(
                count=2,
                offset_count='',
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

    def _generate_load_params(self):
        load = ['uint4 defaults{i} = read_node(kg, &offset);'.format(i=i // 4 + 1) for i in range(0, len(
            [socket for socket in self._sockets if socket['type'] == 'Input' and isinstance(socket['data-type'], FloatSocket)]), 4)]
        if len(load) > 0:
            load.append('\n\n')

        float_i = 0
        type_map = {'Float': 'float', 'Vector': 'float3', 'Color': 'float3', 'Int': 'int', 'Shader': 'float3'}
        for socket in self._sockets:
            if socket['type'] == 'Input':
                load.append(
                    '{type} {name} = stack_load_{type}{default}(stack, {name}_stack_offset{default_address});'.format(
                        type=socket['data-type'].svm_name,
                        name=code_generator_util.string_lower_underscored(socket['name']),
                        default='_default' if isinstance(socket['data-type'], FloatSocket) else '',
                        default_address=', {node}.{address}'.format(
                            node='defaults{i}'.format(i=float_i // 4 + 1),
                            address=['x', 'y', 'z', 'w'][float_i % 4]) if isinstance(socket['data-type'], FloatSocket) else ''
                    ))
                if isinstance(socket['data-type'], FloatSocket):
                    float_i += 1
        return ''.join(load)

    def _is_socket(self, item):
        """Returns if the item is a sockets"""
        return 'type' in item

    def _generate_shader_params(self):
        """Parameters in shader"""
        num_params = self._passed_params_count()
        items = [item for item in self._props + self._sockets]
        if num_params < 4:
            params = ', '.join('uint {name}{suffix}'.format(
                name=code_generator_util.string_lower_underscored(item['name']),
                suffix='_stack_offset' if self._is_socket(item) else '') for item in items)
        elif num_params == 4:
            params = ', '.join('uint {name}{suffix}'.format(
                name=code_generator_util.string_lower_underscored(item['name']),
                suffix='_stack_offset' if self._is_socket(item) else '') for item in items[:2]
                               ) + ', uint stack_offsets'
        elif num_params == 5:
            params = 'uint stack_offsets1, uint stack_offsets2, uint {name}{suffix}'.format(
                name=code_generator_util.string_lower_underscored(items[-1]['name']),
                suffix='_stack_offset' if self._is_socket(items[-1]) else '')
        elif num_params == 6:
            params = 'uint stack_offsets1, uint stack_offsets2'
        elif num_params == 7 or num_params == 8 or num_params == 9:
            params = 'uint stack_offsets1, uint stack_offsets2, uint {name}{suffix}'.format(
                name=code_generator_util.string_lower_underscored(items[-1]['name']),
                suffix='_stack_offset' if self._is_socket(items[-1]) else '')
        elif num_params >= 10 and num_params <= 12:
            params = 'uint stack_offsets1, uint stack_offsets2, uint stack_offsets3'

        return '{params}{offset}'.format(
            params=params,
            offset=', int offset' if any(isinstance(socket['data-type'], FloatSocket) for socket in self._sockets) else '')

    def _generate_shader_file_name(self):
        return "{name}".format(
            name=code_generator_util.string_lower_underscored(self._node_name)
        )

    def _generate_svm_shader(self):
        """Loading passed values in svm_*.h"""
        params = self._generate_shader_params()
        return '\n#pragma once\n\n' \
               'CCL_NAMESPACE_BEGIN\n\n' \
               'ccl_device {return_type} svm_node_{suff}{name}(const KernelGlobals kg,' \
               'ccl_private ShaderData *sd,' \
               'ccl_private float *stack' \
               '{params}' \
               ')' \
               '{{' \
               '{offset_defs}\n\n' \
               '{unpack_params}\n\n' \
               '{load_params}' \
               '{return_statement}' \
               '}}\n\n' \
               'CCL_NAMESPACE_END\n\n'.format(return_type='int' if self._has_multiple_nodes() else 'void',
                   suff='{suff}_'.format(suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                              name=code_generator_util.string_lower_underscored(self._node_name),
                                              params=',{params}'.format(params=params) if params else '',
                                              offset_defs=self._generate_offset_definitions(),
                                              unpack_params=self._generate_unpack(),
                                              load_params=self._generate_load_params(),
                                              return_statement='return offset;' if self._has_multiple_nodes() else '')

    def add_svm_shader(self):
        """svm_*.h"""
        file_path = path.join(self._source_path, "intern", "cycles", "kernel", "svm", "{shader_file_name}.h".format(
            shader_file_name=self._generate_shader_file_name()))
        with open(file_path, 'w') as f:
            code_generator_util.write_license(f)
            if len(self._props) + len(self._sockets) < 13:
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
            if param['data-type'] == 'Float' or isinstance(param['data-type'], FloatSocket):
                # Float optimizations are added in a separate node
                return True
            else:
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

    def _generate_svm_shader_case(self):
        """Case to pass parameters to shader in svm.h"""
        params=self._generate_svm_shader_passed_params()
        return 'case NODE_{SUFF}{NAME}:' \
               '{set_offset}svm_node_{suff}{name}(kg, sd, stack{params}{offset});' \
               'break;\n'.format(
            SUFF='{SUFF}_'.format(SUFF=self._type_suffix_abbreviated.upper()) if self._type_suffix_abbreviated else '',
            NAME=code_generator_util.string_upper_underscored(self._node_name),
            set_offset='offset = ' if self._has_multiple_nodes() else '',
            suff='{suff}_'.format(suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
            name=code_generator_util.string_lower_underscored(self._node_name),
            params=', {params}'.format(params=params) if params else '',
            offset=', offset' if self._has_multiple_nodes() else ''
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
                    lines.insert(i + 1, shader_case)
                    break
            else:
                raise Exception("No match found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._source_path)

    def _generate_enum_typedefs(self):
        """Generate enum typedefs"""
        return ''.join(['typedef enum Node{Name}{Prop} {{{options}}} Node{Name}{Prop};\n\n'.format(
            Name=code_generator_util.string_capitalized_no_space(self._node_name),
            Prop=code_generator_util.string_capitalized_no_space(prop['name']),
            options=','.join(['NODE_{NAME}_{OPTION} = {i}'.format(
                NAME=code_generator_util.string_upper_underscored(self._node_name),
                OPTION=code_generator_util.string_upper_underscored(option['name']),
                i=i + 1) for i, option in enumerate(prop['options'])]))
            for prop in self._props if isinstance(prop['data-type'], EnumProp)])

    def add_svm_types(self):
        """Register node types in types.h"""
        file_path = path.join(self._source_path, "intern", "cycles", "kernel", "svm", "types.h")
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == '} ShaderNodeType;\n':
                    lines.insert(i, 'NODE_{SUFF}{NAME},'.format(
                        SUFF='{SUFF}_'.format(
                            SUFF=self._type_suffix_abbreviated.upper()) if self._type_suffix_abbreviated else '',
                        NAME=code_generator_util.string_upper_underscored(self._node_name)
                    ))
                    lines.insert(i + 2, '\n')
                    lines.insert(i + 3, self._generate_enum_typedefs())
                    break
            else:
                raise Exception("Match not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._source_path)
