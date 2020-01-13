import shutil
from os import path, pardir, SEEK_END, SEEK_SET
import subprocess
import re
from collections import defaultdict


class CodeGeneratorUtil:
    """Utility operations for common code generation"""

    @staticmethod
    def write_license(fd):
        """Appends Blender license info to the file specified by the given file descriptor"""
        with open(path.join(path.dirname(__file__), pardir, "templates", "license.txt"), 'r') as license_f:
            shutil.copyfileobj(license_f, fd)

    @staticmethod
    def apply_clang_formatting(file_path):
        """
        Applies clang formatting to the given file. Requires clang installation http://releases.llvm.org/download.html
        """
        subprocess.call(['clang-format', file_path, '-i'])

    @staticmethod
    def uses_dna(props, node_type):
        """Whether the node requires an DNA struct
            DNA struct is required if props can't fit in shorts custom1/2 and floats custom3/4"""
        if node_type == "Texture":
            return True

        float_count = 0
        enum_count = 0
        bool_count = 0
        int_count = 0
        for prop in props:
            if prop['type'] == "Float":
                float_count += 1
            elif prop['type'] == "Enum":
                enum_count += 1
            elif prop['type'] == "Boolean":
                bool_count += 1
            elif prop['type'] == "Int":
                int_count += 1
            elif prop['type'] == "String":
                return True
        if enum_count > 2 or float_count > 2 or bool_count > 16 or int_count > 2:
            return True
        if enum_count + int_count > 2 or (enum_count + int_count == 2 and bool_count > 0):
            return True

        return False

    @staticmethod
    def dna_padding_size(props):
        """Returns the padding size the dna struct requires
            Requires a padding member if the bytes size of the properties is not a multiple of 8"""
        byte_total = 0
        for prop in props:
            if prop["type"] == "String":
                byte_total += 2 * prop['size']
            else:
                byte_total += 4
        return (8 - byte_total % 8) if byte_total % 8 != 0 else 0

    @staticmethod
    def string_lower_underscored(string):
        return string.replace(" ", "_").lower()

    @staticmethod
    def string_upper_underscored(string):
        return string.replace(" ", "_").upper()

    @staticmethod
    def string_capitalized_underscored(string):
        return "_".join(map(lambda s: s.capitalize(), string.split()))

    @staticmethod
    def string_capitalized_no_space(string):
        return "".join(map(lambda s: s.capitalize(), string.split(" ")))

    @staticmethod
    def string_capitalized_spaced(string):
        return " ".join(map(lambda s: s.capitalize(), string.split(" ")))


class CodeGenerator:
    """Generates code required for a new node"""

    def __init__(self, gui):
        self._gui = gui

    def _add_node_type_id(self):
        """BKE_node.h"""
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenderkernel", "BKE_node.h"),
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
            line = "#define SH_NODE_{0}{1} {2}\n".format("TEX_" if self._gui.get_node_type() == "Texture" else "",
                                                         name_underscored.upper(), str(last + 1))
            file_text = file_text[:last_i - 1] + line + file_text[last_i - 1:]

            f.seek(0)
            f.write(file_text)
            f.truncate()

    def _add_dna_node_type(self):
        """
        DNA_node_types.h
        """
        if CodeGeneratorUtil.uses_dna(self._gui.get_props(), self._gui.get_node_type()):
            dna_path = path.join(self._gui.get_source_path(), "source", "blender", "makesdna", "DNA_node_types.h")
            with open(dna_path, 'r+') as f:
                props = defaultdict(list)
                for prop in self._gui.get_props():
                    if prop['type'] == 'Enum' or prop['type'] == 'Boolean' or prop['type'] == 'Int':
                        props['int'].append(prop['name'])
                    elif prop['type'] == 'String':
                        props['char'].append("{name}[{size}]".format(name=prop['name'], size=prop['size']))
                    elif prop['type'] == 'Float':
                        props['float'].append(prop['name'])
                    else:
                        raise Exception("Invalid Property Type")

                props_definitions = "; ".join(
                    '{key} {names}'.format(key=key, names=", ".join(names)) for key, names in props.items()) + ";"

                struct = 'typedef struct NodeTex{name} {{NodeTexBase base; {props}{pad}}} NodeTex{name};\n\n'.format(
                    name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                    props=props_definitions,
                    pad=' char _pad[{size}];'.format(size=CodeGeneratorUtil.dna_padding_size(self._gui.get_props())) \
                        if CodeGeneratorUtil.dna_padding_size(self._gui.get_props()) != 0 else '')
                text = f.read()
                match = re.search('} NodeTex'[::-1], text[::-1])  # Reversed to find last occurrence
                if match:
                    i = len(text) - match.end()
                    for _ in range(i, len(text)):
                        if text[i] == '\n':
                            break
                        i += 1
                    else:
                        print("No newline found")
                    text = text[:i + 2] + struct + text[i + 2:]

                    f.seek(0)
                    f.write(text)
                    f.truncate()
                else:
                    print("No matches found")
            CodeGeneratorUtil.apply_clang_formatting(dna_path)

            # TODO - Add enums

    def _add_rna_properties(self):
        """rna_nodetree.c"""
        if self._gui.node_has_properties():
            file_path = path.join(self._gui.get_source_path(), "source", "blender", "makesrna", "intern",
                                  "rna_nodetree.c")
            with open(file_path, 'r+') as f:
                props = []
                s_custom_i = 1
                f_custom_i = 3
                uses_dna = CodeGeneratorUtil.uses_dna(self._gui.get_props(), self._gui.get_node_type())
                for prop in self._gui.get_props():
                    if not uses_dna:
                        if prop['type'] == "Enum" or prop['type'] == "Int":
                            custom_i = s_custom_i
                            s_custom_i += 1
                        elif prop['type'] == "Boolean":
                            custom_i = s_custom_i
                        elif prop['type'] == "Float":
                            custom_i = f_custom_i
                            f_custom_i += 1
                    if prop['type'] == "Enum":
                        enum_name = 'rna_enum_node_{tex}{name}_items'. \
                            format(tex='tex_' if self._gui.get_node_type() == "Texture" else '',
                                   name=CodeGeneratorUtil.string_lower_underscored(prop['name']))

                    props.append('prop = RNA_def_property(srna, "{name}", PROP_{TYPE}, PROP_{SUBTYPE});'
                                 'RNA_def_property_{type}_sdna(prop, NULL, "{sdna}"{enum});'
                                 '{enum_items}'
                                 '{prop_range}'
                                 'RNA_def_property_ui_text(prop, "{Name}", "{desc}");'
                                 'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");'.
                        format(
                        name=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                        TYPE=CodeGeneratorUtil.string_upper_underscored(prop['type']),
                        SUBTYPE=CodeGeneratorUtil.string_upper_underscored(prop['sub-type']),
                        type=CodeGeneratorUtil.string_lower_underscored(prop['type']),
                        sdna=CodeGeneratorUtil.string_lower_underscored(
                            prop['name'] if uses_dna else "custom{index}".format(index=custom_i)),
                        enum=', SHD_{NAME}_{PROP}'.format(
                            NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                            PROP=CodeGeneratorUtil.string_upper_underscored(prop['name']))
                        if prop['type'] == "Boolean" else '',
                        enum_items='RNA_def_property_enum_items(prop, {enum_name});'.format(enum_name=enum_name) if
                        prop['type'] == "Enum" else '',
                        prop_range='RNA_def_property_range(prop, {min}, {max});'.format(min=prop['min'],
                                                                                        max=prop['max']) if prop[
                                                                                                                'type'] == "Int" or
                                                                                                            prop[
                                                                                                                'type'] == "Float" else '',
                        Name=CodeGeneratorUtil.string_capitalized_spaced(prop['name']),
                        desc=""))

                func = 'static void def_sh_{tex}{name}(StructRNA *srna)\n' \
                       '{{\n' \
                       'PropertyRNA *prop;\n\n' \
                       '{sdna}' \
                       '{props}\n' \
                       '}}\n\n'.format(tex="tex_" if self._gui.get_node_type() == "Texture" else '',
                                       name=self._gui.get_node_name().replace(" ", "_").lower(),
                                       sdna='RNA_def_struct_sdna_from(srna, "Node{Tex}{Name}", "storage");\ndef_sh_tex(srna);\n\n'. \
                                       format(Name=CodeGeneratorUtil.string_capitalized_no_space(
                                           self._gui.get_node_name()),
                                           Tex="Tex" if self._gui.get_node_type() == "Texture" else "")
                                       if self._gui.get_node_type() == "Texture" else '',
                                       props="\n\n".join(props))
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line == '/* -- Compositor Nodes ------------------------------------------------------ */\n':
                        break
                else:
                    raise Exception("Reached end of file without match")
                lines.insert(i, func)

                f.seek(0, SEEK_SET)
                f.writelines(lines)
                f.truncate()
            CodeGeneratorUtil.apply_clang_formatting(file_path)

    def _add_node_definition(self):
        """NOD_static_types.h"""
        with open("/".join((self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")),
                  "r") as f:
            lines = f.readlines()

            node_definition = 'DefNode(ShaderNode,     ' + \
                              'SH_NODE_' + "_".join(("TEX" if self._gui.get_node_type() == "Texture" else "",
                                                     CodeGeneratorUtil.string_upper_underscored(
                                                         self._gui.get_node_name()))) + \
                              ',' + ('def_sh_' + CodeGeneratorUtil.string_lower_underscored(
                self._gui.get_node_name()) if self._gui.node_has_properties() else '0') + \
                              ', ' + (
                                  'Tex' if self._gui.get_node_type() == "Texture" else '') + CodeGeneratorUtil.string_capitalized_no_space(
                self._gui.get_node_name()) + \
                              ', ' + CodeGeneratorUtil.string_capitalized_spaced(
                self._gui.get_node_name()) + ',  ""   ' + ")"
            print(node_definition)

    def _add_node_drawing(self):
        """drawnode.c"""
        drawnode_path = path.join(self._gui.get_source_path(), "source", "blender", "editors", "space_node",
                                  "drawnode.c")
        with open(drawnode_path, "r+") as f:
            if self._gui.node_has_properties():
                draw_props = ''
                if self._gui.node_has_properties():
                    prop_lines = []
                    for prop in self._gui.get_props():
                        name = "NULL"
                        if prop['type'] == "Enum":
                            name = '""'
                        elif prop['type'] == "String":
                            name = 'IFACE_("{name}")'.format(
                                name=CodeGeneratorUtil.string_capitalized_spaced(prop['name']))
                        prop_lines.append(
                            'uiItemR(layout, ptr, "{propname}", 0, {name}, ICON_NONE);'.format(propname=prop['name'],
                                                                                               name=name))

                    draw_props = ''.join(prop_lines)
                func = 'static void node_shader_buts_{name}(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)' \
                       '{{{props}}}\n\n'.format(
                    name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                    props=draw_props)
                lines = f.readlines()
                line_i = lines.index("static void node_shader_set_butfunc(bNodeType *ntype)\n") - 1

                lines.insert(line_i, func)

                case = [
                    "case SH_NODE_{tex}{name}:\n".format(tex="TEX_" if self._gui.get_node_type() == "Texture" else "",
                                                         name=CodeGeneratorUtil.string_upper_underscored(
                                                             self._gui.get_node_name())),
                    "ntype->draw_buttons = node_shader_buts_{tex}{name};\n".format(
                        tex="tex_" if self._gui.get_node_type() == "Texture" else "",
                        name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name())),
                    "break;\n"]

                for i in range(line_i, len(lines)):
                    if "break" in lines[i] and '}' in lines[i + 1]:
                        line_i = i + 1
                        break
                else:
                    print("Not Found")
                    return

                for line in reversed(case):
                    lines.insert(line_i, line)

                f.seek(0)
                f.writelines(lines)
                f.truncate()
        CodeGeneratorUtil.apply_clang_formatting(drawnode_path)

    def _add_shader_node_file(self):
        """node_shader_*.c"""
        pass

    def _add_node_register(self):
        """NOD_shader.h"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "NOD_shader.h")
        with open(file_path, 'r+') as f:

            func = 'void register_node_type_sh_{tex}{name}(void);\n'. \
                format(tex="tex_" if self._gui.get_node_type() == "Texture" else '',
                       name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()))

            f.seek(0, SEEK_END)
            f.seek(f.tell() - 500, SEEK_SET)
            line = f.readline()
            while line != '\n':
                if line == '':
                    raise Exception("Reached end of file")
                line = f.readline()
            f.seek(f.tell() - 2, SEEK_SET)
            f.write(func)
            f.write('\n'
                    'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
                    '\n'
                    '#endif\n'
                    '\n')

    def _add_cycles_class(self):
        """nodes.h"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.h")
        with open(file_path, 'r+') as f:
            props = defaultdict(list)
            types_convert = {"Boolean": "bool", "Int": "int", "Float": "float", "Enum": "int", "Vector": "float3",
                             "RGBA": "float3", "String": "ustring"}
            for socket in list(filter(lambda s: s['type'] == 'Input', self._gui.get_node_sockets())):
                props[types_convert[socket['data_type']]].append(socket['name'])

            for prop in self._gui.get_props():
                if prop['type'] != "String":
                    props[types_convert[prop['type']]].append(prop['name'])
                else:
                    props['char'].append('{name}[{size}]'.format(name=prop['name'], size=prop['size']))

            props_string = "".join(
                '{type} {names};'.format(type=type, names=", ".join(names)) for type, names in props.items())

            node = "class {name}{tex}Node : public {type}Node {{" \
                   "public:" \
                   "SHADER_NODE_CLASS({name}Node)" \
                   "{node_group}" \
                   "{props}" \
                   "}};".format(name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                                tex="Texture" if self._gui.get_node_type() == "Texture" else "",
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
        CodeGeneratorUtil.apply_clang_formatting(file_path)

    def _add_cycles_class_instance(self):
        """blender_shader.cpp"""
        pass

    def _add_cycles_node(self):
        """nodes.cpp"""
        pass

    def _add_to_node_menu(self):
        """nodeitems_builtins.py"""
        nodeitems_path = path.join(self._gui.get_source_path(), "release", "scripts", "startup",
                                   "nodeitems_builtins.py")
        with open(nodeitems_path, 'r+') as f:
            lines = f.readlines()
            cat_line_i = 0
            for i, line in enumerate(lines):
                if re.search('SH_NEW_' + (
                        'OP_' if self._gui.get_node_group() == 'Color' else '') + self._gui.get_node_group().upper(),
                             line):
                    cat_line_i = i
                    break
            else:
                print("Node Type Not Found")

            for i in range(cat_line_i, len(lines)):
                if re.search(']\)', lines[i]):
                    lines.insert(i, '        NodeItem("ShaderNode{0}{1}"{2})\n'.format(
                        "Tex" if self._gui.get_node_type() == "Texture" else "",
                        CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                        (', poll={0}'.format(self._gui.get_poll()) if self._gui.get_poll() is not None else '')))
                    lines[i - 1] = lines[i - 1][:len(lines[i - 1]) - 1] + ',\n'
                    break
            else:
                print("End not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def _add_osl_shader(self):
        """"""
        node_name_underscored = CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name())
        osl_path = path.join(self._gui.get_source_path(), "intern", "cycles", "kernel", "shaders",
                             "node_" + node_name_underscored + ".osl")
        with open(osl_path, "w+") as osl_f:
            CodeGeneratorUtil.write_license(osl_f)
            osl_f.write('#include "stdosl.h"\n\n')

            props = self._gui.get_props()
            sockets = self._gui.get_node_sockets()

            type_conversion = {"Boolean": "int", "String": "string", "Int": "int", "Float": "float", "Enum": "string"}

            function = "shader node_{name}{tex}({mapping}{props}{in_sockets}{out_sockets}){{}}".format(
                name=node_name_underscored,
                tex='_texture' if self._gui.get_node_type() == 'Texture' else '',
                mapping='int use_mapping = 0,matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),' if self._gui.get_node_type() == 'Texture' else '',
                props=''.join('{type} {name} = {default},'.format(type=type_conversion[prop['type']],
                                                                  name=CodeGeneratorUtil.string_lower_underscored(
                                                                      prop['name']),
                                                                  default=prop['default']) for prop in props),
                in_sockets=''.join(['{type} {name} = {default},'.format(type=type_conversion[socket['data_type']],
                                                                        name=socket['name'],
                                                                        default=socket['default'])
                                    for socket in sockets if socket['type'] == 'Input']),
                out_sockets=','.join(
                    ['output {type} {name} = {default}'.format(type=type_conversion[socket['data_type']],
                                                               name=socket['name'],
                                                               default=socket['default'])
                     for socket in sockets if socket['type'] == 'Output']))

            osl_f.write(function)
        CodeGeneratorUtil.apply_clang_formatting(osl_path)

    def _add_svm_shader(self):
        """"""
        pass

    def _add_glsl_shader(self):
        """"""
        pass

    def generate_node(self):
        self._add_osl_shader()
        self._add_to_node_menu()
        self._add_node_type_id()
        self._add_dna_node_type()
        self._add_node_drawing()
        self._add_cycles_class()
        self._add_node_register()
        self._add_rna_properties()
