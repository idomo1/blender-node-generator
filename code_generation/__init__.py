import shutil
from os import path
from os import pardir
import subprocess


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
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenderkernel", "BKE_node.h"), "r") as f:
            last = 707
            name_underscored = "_".join(self._gui.get_node_name().split(" "))
            line = "#define SH_NODE_" + ("TEX_" if self._gui.get_node_type() == "Texture" else "") + name_underscored.upper() + " " + str(last+1)
            print(line)

    def _add_dna_node_type(self):
        """
        DNA_node_types.h
        For texture nodes
        """
        pass

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
        pass

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
