from os import path
import re

import code_generation.code_generator_util as code_generator_util


class NodeRegisterWriter:
    """Writes references to node register function"""
    def __init__(self, gui):
        self._source_path = gui.get_source_path()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._node_name = gui.get_node_name()
        self._node_group = gui.get_node_group()
        self._node_sockets = gui.get_node_sockets()
        self._node_has_properties = gui.node_has_properties()
        self._props = gui.get_props()

    def generate_node_shader_register(self):
        register_text = 'void register_node_type_sh_{suff}{name}(void)' \
                        '{{' \
                        'namespace file_ns = blender::nodes::node_shader_{suff}{name}_cc;\n\n' \
                        'static bNodeType ntype;\n\n' \
                        'sh_node_type_base(&ntype, SH_NODE_{SUFF}{NAME}, "{Name}", NODE_CLASS_{CLASS});' \
                        'ntype.declare = file_ns::node_declare;' \
                        '{init}' \
                        '{storage}' \
                        'node_type_gpu(&ntype, file_ns::gpu_shader_{suff}{name});' \
                        '\n\n' \
                        'nodeRegisterType(&ntype);' \
                        '}}\n'.format(suff='{suff}_'.format(
            suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                      name=code_generator_util.string_lower_underscored(self._node_name),
                                      SUFF='{SUFF}_'.format(
                                          SUFF=self._type_suffix_abbreviated.upper()) if self._type_suffix_abbreviated else '',
                                      NAME=code_generator_util.string_upper_underscored(self._node_name),
                                      Name=code_generator_util.string_capitalized_spaced(self._node_name),
                                      CLASS=self._node_group.upper(),
                                      sockets_in='sh_node_{suff}{name}_in'.format(
                                          suff='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._node_name)) if len(
                                          [sock for sock in self._node_sockets if
                                           sock['type'] == 'Input']) > 0 else 'NULL',
                                      sockets_out='sh_node_{suff}{name}_out'.format(
                                          suff='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._node_name)) if len(
                                          [sock for sock in self._node_sockets if
                                           sock['type'] == 'Output']) > 0 else 'NULL',
                                      init='node_type_init(&ntype, file_ns::node_shader_init_{tex}{name});'.format(
                                          tex='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._node_name)) if self._node_has_properties else '',
                                      storage='node_type_storage(&ntype, "Node{Suff}{Name}", node_free_standard_storage, node_copy_standard_storage);'.format(
                                          Suff=self._type_suffix_abbreviated.capitalize(),
                                          Name=code_generator_util.string_capitalized_no_space(
                                              self._node_name)
                                      ),
                                      Suff=self._type_suffix_abbreviated.capitalize())
        return register_text

    def write_node_register(self):
        """NOD_shader.h"""
        file_path = path.join(self._source_path, "source", "blender", "nodes", "NOD_shader.h")
        with open(file_path, 'r+') as f:

            func = 'void register_node_type_sh_{suff}{name}(void);\n'. \
                format(suff="{suff}_".format(
                suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                       name=code_generator_util.string_lower_underscored(self._node_name))

            # Find insertion point. Parse file in reverse to put new line near the bottom.
            contents = f.readlines()
            for i, line in enumerate(reversed(contents)):
                if re.search(r'^void register_node_type_sh.*void\);$', line) != None:
                    break
            
            # Insert new register call.
            contents.insert(len(contents) - i, func)
            # Clear file contents.
            f.truncate(0)
            # Write new content.
            f.seek(0)
            f.writelines(contents)

    def write_call_node_register(self):
        """node.c"""
        file_path = path.join(self._source_path, "source", "blender", "blenkernel", "intern", "node.cc")
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == 'static void registerShaderNodes()\n':
                    while lines[i] != '}\n':
                        i += 1
                    lines.insert(i, 'register_node_type_sh_{suff}{name}();'.format(
                        suff='{suff}_'.format(suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                        name=code_generator_util.string_lower_underscored(self._node_name)
                    ))
                    break
            else:
                raise Exception("Match not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._source_path)
