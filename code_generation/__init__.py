from os import path, SEEK_END, SEEK_SET
import re
from collections import defaultdict

from . import code_generator_util
from .svm_writer import SVMWriter
from .glsl_writer import GLSLWriter
from .cmake_writer import CMakeWriter
from .node_definition_writer import NodeDefinitionWriter
from .osl_writer import OSLWriter
from .dna_writer import DNAWriter
from .node_register_writer import NodeRegisterWriter
from .rna_writer import RNAWriter
from .node_drawing_writer import NodeDrawingWriter


class CodeGenerator:
    """Generates code required for a new node"""

    def __init__(self, gui):
        self._gui = gui

    def _add_node_type_id(self):
        """BKE_node.h"""
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenkernel", "BKE_node.h"),
                  "r+") as f:
            file_text = f.read()
            last_i = -1
            last_id = re.search('[7-9][0-9][0-9]\n\n', file_text)
            if last_id is not None:
                last_i = last_id.end()
            else:
                print("Node ID not found")
            last = int(file_text[last_i - 5:last_i - 2])
            name_underscored = "_".join(self._gui.get_node_name().split(" "))
            line = "#define SH_NODE_{0}{1} {2}\n".format("{SUFF}_".format(
                SUFF=self._gui.type_suffix_abbreviated().upper()) if self._gui.type_suffix_abbreviated() else '',
                                                         name_underscored.upper(), str(last + 1))
            file_text = file_text[:last_i - 1] + line + file_text[last_i - 1:]

            f.seek(0)
            f.write(file_text)
            f.truncate()

    def _add_node_definition(self):
        """NOD_static_types.h"""
        def_node_line_length = 138
        def_node_parameter_offsets = [0, 16, 44, 68, 90, 108, 129]
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")
        with open(file_path, "r+") as f:
            params = 'ShaderNode,' \
                     'SH_NODE_{SUFF}{NAME},' \
                     '{rna},' \
                     '"{SUFF}{NAME}",' \
                     '{struct},' \
                     '"{Name}{Suffix}",' \
                     '""'.format(
                SUFF='{SUFF}_'.format(
                    SUFF=self._gui.type_suffix_abbreviated().upper()) if self._gui.type_suffix_abbreviated() else '',
                NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                rna='def_sh_{suff}{name}'.format(
                    suff='{suff}_'.format(suff=self._gui.type_suffix_abbreviated()) if self._gui.type_suffix() else '',
                    name=code_generator_util.string_lower_underscored(
                        self._gui.get_node_name())) if self._gui.node_has_properties() else 0,
                struct='{Suff}{Name}'.format(Suff=self._gui.type_suffix_abbreviated().capitalize(),
                                             Name=code_generator_util.string_capitalized_no_space(
                                                 self._gui.get_node_name())),
                Name=code_generator_util.string_capitalized_spaced(self._gui.get_node_name()),
                Suffix=' {Suffix}'.format(
                    Suffix='Texture' if self._gui.is_texture_node() else 'BSDF') if self._gui.type_suffix() else '')

            node_definition = 'DefNode({params})\n'.format(
                params=code_generator_util.fill_white_space(
                    params.split(','), def_node_line_length, def_node_parameter_offsets))

            # Find last shader node definition, write new node def under that
            text = f.read()
            matches = re.search(r'edoNredahS\(edoNfeD', text[::-1])
            if not matches:
                raise Exception("Match not found")
            match_i = len(text) - matches.end()
            for i in range(match_i, len(text)):
                if text[i] == '\n':
                    break
            else:
                raise Exception("No newline found")

            text = text[:i + 1] + node_definition + text[i + 1:]
            f.seek(0)
            f.write(text)
            f.truncate()

    def _add_cycles_class(self):
        """nodes.h"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.h")
        with open(file_path, 'r+') as f:
            props = defaultdict(list)
            types_convert = {"Boolean": "bool", "Int": "int", "Float": "float", "Enum": "int", "Vector": "float3",
                             "RGBA": "float3", "String": "ustring"}
            for socket in list(filter(lambda s: s['type'] == 'Input', self._gui.get_node_sockets())):
                props[types_convert[socket['data-type']]].append(
                    code_generator_util.string_lower_underscored(socket['name']))

            for prop in self._gui.get_props():
                props[types_convert[prop['data-type']]].append(
                    code_generator_util.string_lower_underscored(prop['name']))

            props_string = "".join(
                '{type} {names};'.format(type=type,
                                         names=", ".join(names)) for
                type, names in props.items())

            node = "class {name}{Suffix}Node : public {type}Node {{" \
                   "public:" \
                   "SHADER_NODE_CLASS({name}{Suffix}Node)\n" \
                   "{node_group}" \
                   "{props}" \
                   "}};".format(name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                                Suffix=self._gui.type_suffix().capitalize(),
                                type=self._gui.get_node_type(),
                                node_group="virtual int get_group(){{return NODE_GROUP_LEVEL_{level};}}".
                                format(
                                    level=self._gui.get_node_group_level()) if self._gui.get_node_group_level() is not 0 else "",
                                props=props_string)
            f.seek(0, SEEK_END)
            f.seek(f.tell() - 100, SEEK_SET)
            line = f.readline()
            while line != '\n':
                if line == '':
                    raise Exception("Reached end of file")
                line = f.readline()
            f.seek(f.tell(), SEEK_SET)
            f.write(node)
            f.write("""

                    CCL_NAMESPACE_END

                    #endif /* __NODES_H__ */
                    """)
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_cycles_class_instance(self):
        """blender_shader.cpp"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "blender", "blender_shader.cpp")
        with open(file_path, 'r+') as f:
            props = self._gui.get_props()
            text = 'else if (b_node.is_a(&RNA_ShaderNode{Suff}{Name})) {{' \
                   'BL::ShaderNode{Suff}{Name} b_{name}_node(b_node);' \
                   '{Name}{Suffix}Node *{name} = new {Name}{Suffix}Node();' \
                   '{props}' \
                   '{texture_mapping}' \
                   'node = {name};' \
                   '}}\n'.format(
                Suff=self._gui.type_suffix_abbreviated().capitalize(),
                Name=code_generator_util.string_capitalized_no_space(
                    self._gui.get_node_name()),
                name=code_generator_util.string_lower_underscored(
                    self._gui.get_node_name()),
                Suffix=self._gui.type_suffix().capitalize(),
                props=''.join(
                    ['{name}->{prop} = b_{name}_node.{prop}();'.format(
                        name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                        prop=code_generator_util.string_lower_underscored(prop['name'])) for prop in props]),
                texture_mapping='BL::TexMapping b_texture_mapping(b_{name}_node.texture_mapping());'
                                'get_tex_mapping(&{name}->tex_mapping, b_texture_mapping);'.format(
                    name=code_generator_util.string_lower_underscored(
                        self._gui.get_node_name())) if self._gui.uses_texture_mapping() else '') \
                if len(props) > 0 or self._gui.uses_texture_mapping() else \
                'else if (b_node.is_a(&RNA_ShaderNode{Suff}{Name})) {{' \
                'node = new {Name}{Suffix}Node();}}\n'.format(
                    Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                    Suff=self._gui.type_suffix_abbreviated().capitalize(),
                    Suffix=self._gui.type_suffix().capitalize())

            file_text = f.read()
            # Find start of function
            function_i = re.search(r'static ShaderNode \*add_node\(Scene \*scene,', file_text)

            # Find end of function
            if not function_i:
                raise Exception("Match not found")

            i = function_i.span()[1]
            while file_text[i] != '{':
                i += 1
            bracket_stack = 1
            while bracket_stack > 0:
                i += 1
                if file_text[i] == '{':
                    bracket_stack += 1
                elif file_text[i] == '}':
                    bracket_stack -= 1

            # Go back to last else if
            seen_brackets = 0
            while seen_brackets < 2:
                i -= 1
                if file_text[i] == '}':
                    seen_brackets += 1

            # Insert text into file
            file_text = file_text[:i + 2] + text + file_text[i + 2:]

            f.seek(0)
            f.write(file_text)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_cycles_node(self):
        """nodes.cpp"""

        def format_default(item):
            if item['data-type'] == 'Enum':
                for i, option in enumerate(item['options']):
                    if option['name'] == item['default']:
                        return i + 1
                else:
                    raise Exception("Default not in options")
            elif item['data-type'] == 'Boolean':
                return 'true' if item['default'] else 'false'
            elif item['data-type'] == 'Float':
                return '{0}f'.format(item['default'])
            elif item['data-type'] == 'Int':
                return item['default']
            elif item['data-type'] == 'String':
                return 'ustring()'
            elif item['data-type'] == 'Vector' or item['data-type'] == 'RGBA':
                return 'make_float3({default})'.format(
                    default=code_generator_util.fill_socket_default(item['default'], 3))

        def is_first_vector_socket(socket):
            if socket['data-type'] != 'Vector':
                return False
            return socket == [sock for sock in sockets if sock['data-type'] == 'Vector'][0]

        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.cpp")
        with open(file_path, 'r+') as f:
            props = self._gui.get_props()
            sockets = self._gui.get_node_sockets()

            svm_node_manager = SVMWriter(self._gui)

            socket_defs = []
            for prop in props:
                if prop['data-type'] == 'Enum':
                    socket_defs.append('static NodeEnum {name}_enum;'.format(
                        name=code_generator_util.string_lower_underscored(prop['name'])))
                    socket_defs.extend(['{prop}_enum.insert("{OPTION}", {i});'.format(
                        prop=prop['name'],
                        OPTION=code_generator_util.string_upper_underscored(option['name']),
                        i=i + 1) for i, option in enumerate(prop['options'])])
                    socket_defs.append('SOCKET_ENUM({prop}, "{Prop}", {prop}_enum, {default});\n\n'.format(
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        Prop=code_generator_util.string_capitalized_spaced(prop['name']),
                        default=format_default(prop)))
                else:
                    socket_defs.append('SOCKET_{TYPE}({prop}, "{Prop}", {default});'.format(
                        TYPE=prop['data-type'].upper(),
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        Prop=code_generator_util.string_capitalized_spaced(prop['name']),
                        default=format_default(prop)))
            socket_defs.append('\n\n')

            data_type_map = {'Int': 'INT', 'Float': 'FLOAT', 'Enum': 'ENUM', 'Vector': 'POINT', 'RGBA': 'COLOR',
                             'Shader': 'CLOSURE', 'String': 'STRING'}

            for socket in sockets:
                socket_defs.append('SOCKET_{TYPE}_{DATA_TYPE}({name}, "{Name}"{default}{texture_mapping});'.format(
                    TYPE=socket['type'][:-3].upper(),
                    DATA_TYPE=data_type_map[socket['data-type']],
                    name=code_generator_util.string_lower_underscored(socket['name']),
                    Name=code_generator_util.string_capitalized_spaced(socket['name']),
                    default=(', ' + format_default(socket)) if socket['type'] == 'Input' and socket[
                        'data-type'] != 'Shader' else '',
                    texture_mapping=', SocketType::LINK_TEXTURE_GENERATED' if self._gui.uses_texture_mapping() and
                                                                              socket['data-type'] == 'Vector' and
                                                                              is_first_vector_socket(socket) else ''))

            node = '/* {NodeName}{space}{Suffix} */\n\n' \
                   'NODE_DEFINE({Name}{Suffix}Node)' \
                   '{{' \
                   'NodeType *type = NodeType::add("{name}{suffix}", create, NodeType::SHADER);\n\n' \
                   '{texture_mapping}' \
                   '{sockets}\n\n' \
                   'return type;' \
                   '}}\n\n' \
                   '{Name}{Suffix}Node::{Name}{Suffix}Node() : {Type}Node(node_type)' \
                   '{{' \
                   '}}\n\n' \
                   '{svm_func}' \
                   'void {Name}{Suffix}Node::compile(OSLCompiler &compiler)' \
                   '{{' \
                   '{tex_mapping_comp_osl}' \
                   '{osl_params}' \
                   'compiler.add(this, "node_{name}{suffix}");' \
                   '}}\n\n'.format(
                NodeName=code_generator_util.string_capitalized_spaced(self._gui.get_node_name()),
                space=' ' if self._gui.type_suffix_abbreviated() is not '' else '',
                Suffix=self._gui.type_suffix().capitalize(),
                Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                suffix='_{suffix}'.format(suffix=self._gui.type_suffix()) if self._gui.type_suffix() else '',
                texture_mapping='TEXTURE_MAPPING_DEFINE({Name}{Texture}Node);\n\n'.format(
                    Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                    Texture='Texture' if self._gui.is_texture_node() else ''
                ) if self._gui.uses_texture_mapping() else '',
                sockets=''.join(socket_defs),
                Type=self._gui.get_node_type(),
                svm_func=svm_node_manager.generate_svm_compile_func(),
                tex_mapping_comp_osl='tex_mapping.compile(compiler);\n\n' if self._gui.uses_texture_mapping() else '',
                osl_params=''.join('compiler.parameter(this, "{prop}");'.format(prop=prop['name']) for prop in props if
                                   prop['data-type'] != 'String')
            )

            f.seek(0, SEEK_END)
            f.seek(f.tell() - 30, SEEK_SET)
            text = f.read()
            match = re.search('\n\n', text)

            if not match:
                raise Exception("Match not found")

            f.seek(f.tell() - 30 + match.end() + 3)
            f.write(node)

            f.write('CCL_NAMESPACE_END\n\n')
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_to_node_menu(self):
        """nodeitems_builtins.py"""
        nodeitems_path = path.join(self._gui.get_source_path(), "release", "scripts", "startup",
                                   "nodeitems_builtins.py")
        with open(nodeitems_path, 'r+') as f:
            lines = f.readlines()
            cat_line_i = 0
            for i, line in enumerate(lines):
                if re.search('SH_NEW_' + self._gui.get_node_group().upper(), line):
                    cat_line_i = i
                    break
            else:
                print("Node Type Not Found")

            for i in range(cat_line_i, len(lines)):
                if re.search(']\)', lines[i]):
                    lines.insert(i, '        NodeItem("ShaderNode{0}{1}")\n'.format(
                        self._gui.type_suffix_abbreviated().capitalize(),
                        code_generator_util.string_capitalized_no_space(self._gui.get_node_name())))
                    if lines[i - 1][-2] != ',':
                        lines[i - 1] = lines[i - 1][:len(lines[i - 1]) - 1] + ',\n'
                    break
            else:
                print("End not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def generate_node(self):
        self._add_to_node_menu()
        self._add_node_type_id()
        self._add_cycles_class()
        self._add_cycles_class_instance()
        self._add_node_definition()
        self._add_cycles_node()

        svm_manager = svm_writer.SVMWriter(self._gui)
        svm_manager.add_svm_shader()
        svm_manager.add_register_svm()
        svm_manager.add_svm_types()

        glsl_manager = GLSLWriter(self._gui)
        glsl_manager.add_glsl_shader()

        cmake_manager = CMakeWriter(self._gui)
        cmake_manager.add_to_cmake()

        node_definition_writer = NodeDefinitionWriter(self._gui)
        node_definition_writer.write_node_definition_file()

        osl_writer = OSLWriter(self._gui)
        osl_writer.write_osl_shader()

        dna_writer = DNAWriter(self._gui)
        dna_writer.write_dna_node_type()

        register_writer = NodeRegisterWriter(self._gui)
        register_writer.write_call_node_register()
        register_writer.write_node_register()

        rna_writer = RNAWriter(self._gui)
        rna_writer.write_rna_properties()

        drawing_writer = NodeDrawingWriter(self._gui)
        drawing_writer.write_node_drawing()
