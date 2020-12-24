from os import path, SEEK_END, SEEK_SET

from . import code_generator_util


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
        self._socket_availability_changes = gui.socket_availability_changes()
        self._node_type = gui.get_node_type()

    def generate_node_shader_register(self):
        register_text = 'void register_node_type_sh_{suff}{name}(void)' \
                        '{{' \
                        'static bNodeType ntype;\n\n' \
                        'sh_node_type_base(&ntype, SH_NODE_{SUFF}{NAME}, "{Name}", NODE_CLASS_{CLASS}, 0);' \
                        'node_type_socket_templates(&ntype, {sockets_in}, {sockets_out});' \
                        '{init}' \
                        '{storage}' \
                        'node_type_gpu(&ntype, gpu_shader_{suff}{name});' \
                        '{update}\n\n' \
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
                                           sock['type'] == 'Input' and sock['data-type'] != 'String']) > 0 else 'NULL',
                                      sockets_out='sh_node_{suff}{name}_out'.format(
                                          suff='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._node_name)) if len(
                                          [sock for sock in self._node_sockets if
                                           sock['type'] == 'Output' and sock['data-type'] != 'String']) > 0 else 'NULL',
                                      init='node_type_init(&ntype, node_shader_init_{tex}{name});'.format(
                                          tex='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._node_name)) if self._node_has_properties else '',
                                      storage='node_type_storage(&ntype, "Node{Suff}{Name}", node_free_standard_storage, node_copy_standard_storage);'.format(
                                          Suff=self._type_suffix_abbreviated.capitalize(),
                                          Name=code_generator_util.string_capitalized_no_space(
                                              self._node_name)
                                      )
                                      if code_generator_util.uses_dna(
                                          self._props,
                                          self._node_type) else 'node_type_storage(&ntype, "", NULL, NULL);',
                                      Suff=self._type_suffix_abbreviated.capitalize(),
                                      update='node_type_update(&ntype, node_shader_update_{suff}{name});'.format(
                                          suff='{suff}_'.format(
                                              suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                          name=code_generator_util.string_lower_underscored(self._node_name))
                                      if self._socket_availability_changes else '')
        return register_text

    def write_node_register(self):
        """NOD_shader.h"""
        file_path = path.join(self._source_path, "source", "blender", "nodes", "NOD_shader.h")
        with open(file_path, 'r+') as f:

            func = 'void register_node_type_sh_{suff}{name}(void);\n'. \
                format(suff="{suff}_".format(
                suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                       name=code_generator_util.string_lower_underscored(self._node_name))

            f.seek(0, SEEK_END)
            f.seek(f.tell() - 500, SEEK_SET)
            line = f.readline()
            while line != '\n':
                if line == '':
                    raise Exception("Reached end of file")
                line = f.readline()
            f.seek(f.tell() - 2, SEEK_SET)
            f.write(func)
            f.write('\n' \
                    'void register_node_type_sh_custom_group(bNodeType *ntype);\n' \
                    '\n' \
                    '#ifdef __cplusplus\n' \
                    '}\n' \
                    '#endif\n' \
                    '\n')

    def write_call_node_register(self):
        """node.c"""
        file_path = path.join(self._source_path, "source", "blender", "blenkernel", "intern", "node.c")
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == 'static void registerShaderNodes(void)\n':
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
