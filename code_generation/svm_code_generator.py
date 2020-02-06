from . import code_generator_util


class SVMCompilationManager:
    """
    Generates code related to SVM
    Keeps svm parameters consistent between files
    """

    def __init__(self, props, sockets, node_name, is_texture_node=False, uses_texture_mapping=False):
        self._props = props
        self._sockets = sockets
        self._node_name = node_name
        self._is_texture_node = is_texture_node
        self._uses_texture_mapping = uses_texture_mapping

    def _generate_param_names(self):
        """How the props/sockets are passed to the compiler"""
        names = []
        for prop in self._props:
            if prop['type'] == 'Float':
                names.append(
                    '__float_as_int({name})'.format(name=code_generator_util.string_lower_underscored(prop['name'])))
            elif prop['type'] != 'String':
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
            return ', '.join([param_names[:2], uchar4.format(params=', '.join(param_names[2:]))])
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
