import shutil
from os import path
from os import pardir
import subprocess
import re


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


class CodeGenerator:
    """Generates code required for a new node"""
    def __init__(self, gui):
        self._gui = gui

    def _add_node_type_id(self):
        """BKE_node.h"""
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenderkernel", "BKE_node.h"), "r+") as f:
            file_text = f.read()
            last_i = -1
            last_id = re.search('[7-9][0-9][0-9]\n\n', file_text)
            if last_id is not None:
                last_i = last_id.end()
            else:
                print("Node ID not found")
            last = int(file_text[last_i-5:last_i-2])
            name_underscored = "_".join(self._gui.get_node_name().split(" "))
            line = "#define SH_NODE_{0}{1} {2}\n".format("TEX_" if self._gui.get_node_type() == "Texture" else "", name_underscored.upper(), str(last+1))
            file_text = file_text[:last_i-1] + line + file_text[last_i-1:]

            f.seek(0)
            f.write(file_text)
            f.truncate()

    def _add_dna_node_type(self):
        """
        DNA_node_types.h
        For texture nodes
        """
        if self._gui.get_node_type() == "Texture":
            dna_path = path.join(self._gui.get_source_path(), "source", "blender", "makesdna", "DNA_node_types.h")
            print(self._gui.get_node_dropdown_property2_name() is None)
            with open(dna_path, 'r+') as f:
                struct = 'typedef struct NodeTex{name} {{NodeTexBase base; {props}{pad}}} NodeTex{name};\n\n'.format(
                    name="".join(map(lambda s: s.capitalize(), self._gui.get_node_name().split(" "))),
                    props='{prop1} {prop2} {bools}'
                        .format(prop1='int {0};'.format(self._gui.get_node_dropdown_property1_name()) if self._gui.get_node_dropdown_property1_name() is not None else '',
                                prop2='int {0};'.format(self._gui.get_node_dropdown_property2_name()) if self._gui.get_node_dropdown_property2_name() is not None else '',
                                bools=" ".join(['int ' + check['name'] + ";" for check in self._gui.get_node_check_boxes()])),
                    pad=' char _pad[4];' if (self._gui.get_node_check_box_count() +
                                            (self._gui.get_node_dropdown_property1_name() is not None) +
                                            (self._gui.get_node_dropdown_property2_name() is not None)) % 2 == 1 else '')
                text = f.read()
                match = re.search('} NodeTex'[::-1], text[::-1])    # Reversed to find last occurrence
                if match:
                    i = len(text) - match.end()
                    for _ in range(i, len(text)):
                        if text[i] == '\n':
                            break
                        i += 1
                    else:
                        print("No newline found")
                    text = text[:i+2] + struct + text[i+2:]

                    f.seek(0)
                    f.write(text)
                    f.truncate()
                else:
                    print("No matches found")
            CodeGeneratorUtil.apply_clang_formatting(dna_path)

    def _add_rna_properties(self):
        """rna_nodetree.c"""
        pass

    def _add_node_definition(self):
        """NOD_static_types.h"""
        with open("/".join((self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")), "r") as f:
            lines = f.readlines()

            node_name_underscored = self._gui.get_node_name().replace(" ", "_")

            node_definition = 'DefNode(ShaderNode,     ' + \
                              'SH_NODE_' + "_".join(("TEX" if self._gui.get_node_type() == "Texture" else "", node_name_underscored.upper())) + \
                              ',' + ('def_sh_' + node_name_underscored.lower() if self._gui.node_has_properties() else '0') + \
                              ', ' + ('Tex' if self._gui.get_node_type() == "Texture" else '') + self._gui.get_node_name().replace(" ", "") + \
                              ', ' + " ".join(map(lambda word: word.capitalize(), self._gui.get_node_name().split(" "))) + ',  ""   ' + ")"
            print(node_definition)

    def _add_node_drawing(self):
        """drawnode.c"""
        if self._gui.node_has_properties() or self._gui.node_has_check_box():
            pass

    def _add_shader_node_file(self):
        """node_shader_*.c"""
        pass

    def _add_node_register(self):
        """NOD_shader.h"""
        pass

    def _add_cycles_class(self):
        """nodes.h"""
        pass

    def _add_cycles_class_instance(self):
        """blender_shader.cpp"""
        pass

    def _add_cycles_node(self):
        """nodes.cpp"""
        pass

    def _add_to_node_menu(self):
        """nodeitems_builtins.py"""
        nodeitems_path = path.join(self._gui.get_source_path(), "release", "scripts", "startup", "nodeitems_builtins.py")
        with open(nodeitems_path, 'r+') as f:
            lines = f.readlines()
            cat_line_i = 0
            for i, line in enumerate(lines):
                if re.search('SH_NEW_' + ('OP_' if self._gui.get_node_type() == 'Color' else '') + self._gui.get_node_type().upper(), line):
                    cat_line_i = i
                    break
            else:
                print("Node Type Not Found")

            for i in range(cat_line_i, len(lines)):
                if re.search(']\)', lines[i]):
                    lines.insert(i, '        NodeItem("ShaderNode{0}{1}"{2})\n'.format("Tex" if self._gui.get_node_type() == "Texture" else "",
                                                                              "".join(map(lambda s: s.capitalize(), self._gui.get_node_name().split(" "))),
                                                                              (', poll={0}'.format(self._gui.get_poll()) if self._gui.get_poll() is not None else '')))
                    lines[i-1] = lines[i-1][:len(lines[i-1])-1] + ',\n'
                    break
            else:
                print("End not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def _add_osl_shader(self):
        """"""
        node_name_underscored = self._gui.get_node_name().replace(" ", "_").lower()
        osl_path = path.join(self._gui.get_source_path(), "intern", "cycles", "kernel", "shaders", "node_" + node_name_underscored + ".osl")
        with open(osl_path, "w+") as osl_f:
            CodeGeneratorUtil.write_license(osl_f)
            osl_f.write('#include "stdosl.h"\n\n')

            properties1 = self._gui.get_node_dropdown1_properties()
            properties2 = self._gui.get_node_dropdown2_properties()
            dropdown1_name = self._gui.get_node_dropdown_property1_name()
            dropdown2_name = self._gui.get_node_dropdown_property2_name()
            check_boxes = self._gui.get_node_check_boxes()
            sockets = self._gui.get_node_sockets()

            function = "shader node_{0}{1}({2}{3}{4}{5}{6}{7}{8}".format(node_name_underscored,
                '_texture' if self._gui.get_node_type() == 'Texture' else '',
                'int use_mapping = 0, matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), ' if self._gui.get_node_type() == 'Texture' else '',
                'string {name} = "{default}", '.format(name=dropdown1_name, default=properties1[0]) if properties1 is not None else "",
                'string {name} = "{default}", '.format(name=dropdown2_name, default=properties2[0]) if properties2 is not None else "",
                ''.join(['int {name} = {default}, '.format(name=box['name'], default=str(int(box['default']))) for box in check_boxes]),
                ''.join(['{type} {name} = {default}, '.format(type=socket['data_type'], name=socket['name'], default=socket['default']) for socket in sockets if socket['type'] == 'Input']),
                ', '.join(['output {type} {name} = {default}'.format(type=socket['data_type'], name=socket['name'], default=socket['default']) for socket in sockets if socket['type'] == 'Output']),
                '){}')

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
