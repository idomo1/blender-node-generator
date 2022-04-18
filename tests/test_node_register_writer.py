# import unittest
# from unittest.mock import Mock, patch, mock_open

# from code_generation.node_register_writer import NodeRegisterWriter


# class TestNodeRegisterWriter(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls._mock_gui = Mock()

#     def _create_default_class(self, props=None, sockets=None, node_type='Shader', node_group='Shader'):
#         self._mock_gui.get_node_type.return_value = node_type
#         self._mock_gui.get_source_path.return_value = 'C:/some/path'
#         self._mock_gui.get_node_name.return_value = "Node Name"
#         self._mock_gui.get_props.return_value = [
#             {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
#              "options": [{"name": "prop1", "desc": "Short description"},
#                          {"name": "prop2", "desc": "Short description"}],
#              "default": 'prop1'},
#             {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
#              "options": [{"name": "prop3", "desc": "Short description"},
#                          {"name": "prop4", "desc": "Short description"}],
#              "default": 'prop3'},
#             {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
#             {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
#             {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
#             {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
#             {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64,
#              "default": '""'}] if props is None else props
#         self._mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
#                                                          'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                          'min': "-1.0", 'max': "1.0", 'default': "0.5"},
#                                                         {'type': "Output", 'name': "socket2", 'data-type': "Float",
#                                                          'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                          'min': "-1.0", 'max': "1.0",
#                                                          }] if sockets is None else sockets
#         if node_type == 'Texture':
#             suffix = 'tex'
#         elif node_type == 'Bsdf':
#             suffix = 'bsdf'
#         else:
#             suffix = ''
#         self._mock_gui.type_suffix_abbreviated.return_value = suffix
#         self._mock_gui.get_node_group.return_value = node_group
#         return NodeRegisterWriter(self._mock_gui)

#     def test_write_node_register_correct_formatting(self):
#         with patch('builtins.open', mock_open(read_data='void register_node_type_sh_tex_ies(void);\n'
#                                                         'void register_node_type_sh_tex_white_noise(void);\n'
#                                                         'void register_node_type_sh_tex_truchet(void);\n'
#                                                         '\n'
#                                                         'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
#                                                         '\n'
#                                                         '#endif\n'
#                                                         '\n')) as mf:
#             code_gen = self._create_default_class()
#             code_gen.write_node_register()

#             self.assertTrue(mf.mock_calls[-3][1][0] == 'void register_node_type_sh_node_name(void);\n')

#     def test_write_texture_node_register_correct_formatting(self):
#         with patch('builtins.open', mock_open(read_data='void register_node_type_sh_tex_ies(void);\n'
#                                                         'void register_node_type_sh_tex_white_noise(void);\n'
#                                                         'void register_node_type_sh_tex_truchet(void);\n'
#                                                         '\n'
#                                                         'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
#                                                         '\n'
#                                                         '#endif\n'
#                                                         '\n')) as mf:
#             code_gen = self._create_default_class(node_type='Texture')
#             code_gen.write_node_register()

#             self.assertTrue(mf.mock_calls[-3][1][0] == 'void register_node_type_sh_tex_node_name(void);\n')

#     def test_write_bsdf_node_register_correct_formatting(self):
#         with patch('builtins.open', mock_open(read_data='void register_node_type_sh_tex_ies(void);\n'
#                                                         'void register_node_type_sh_tex_white_noise(void);\n'
#                                                         'void register_node_type_sh_tex_truchet(void);\n'
#                                                         '\n'
#                                                         'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
#                                                         '\n'
#                                                         '#endif\n'
#                                                         '\n')) as mf:
#             code_gen = self._create_default_class(node_type='Bsdf')
#             code_gen.write_node_register()

#             self.assertTrue(mf.mock_calls[-3][1][0] == 'void register_node_type_sh_bsdf_node_name(void);\n')

#     def test_generate_node_register_correct_formatting(self):
#         code_gen = self._create_default_class()
#         text = code_gen.generate_node_shader_register()

#         self.assertTrue(text == 'void register_node_type_sh_node_name(void)'
#                                 '{'
#                                 'static bNodeType ntype;\n\n'
#                                 'sh_node_type_base(&ntype, SH_NODE_NODE_NAME, "Node Name", NODE_CLASS_SHADER, 0);'
#                                 'node_type_socket_templates(&ntype, sh_node_node_name_in, sh_node_node_name_out);'
#                                 'node_type_init(&ntype, node_shader_init_node_name);'
#                                 'node_type_storage(&ntype, "NodeNodeName", node_free_standard_storage, node_copy_standard_storage);'
#                                 'node_type_gpu(&ntype, gpu_shader_node_name);'
#                                 'node_type_update(&ntype, node_shader_update_node_name);'
#                                 '\n\n'
#                                 'nodeRegisterType(&ntype);'
#                                 '}\n')

#     def test_generate_node_register_texture_node_correct_formatting(self):
#         code_gen = self._create_default_class(node_type='Texture', node_group='Texture')
#         text = code_gen.generate_node_shader_register()

#         self.assertTrue(text == 'void register_node_type_sh_tex_node_name(void)'
#                                 '{'
#                                 'static bNodeType ntype;\n\n'
#                                 'sh_node_type_base(&ntype, SH_NODE_TEX_NODE_NAME, "Node Name", NODE_CLASS_TEXTURE, 0);'
#                                 'node_type_socket_templates(&ntype, sh_node_tex_node_name_in, sh_node_tex_node_name_out);'
#                                 'node_type_init(&ntype, node_shader_init_tex_node_name);'
#                                 'node_type_storage(&ntype, "NodeTexNodeName", node_free_standard_storage, node_copy_standard_storage);'
#                                 'node_type_gpu(&ntype, gpu_shader_tex_node_name);'
#                                 'node_type_update(&ntype, node_shader_update_tex_node_name);'
#                                 '\n\n'
#                                 'nodeRegisterType(&ntype);'
#                                 '}\n')

#     def test_generate_node_register_bsdf_node_correct_formatting(self):
#         code_gen = self._create_default_class(node_type='Bsdf')
#         text = code_gen.generate_node_shader_register()

#         self.assertTrue(text == 'void register_node_type_sh_bsdf_node_name(void)'
#                                 '{'
#                                 'static bNodeType ntype;\n\n'
#                                 'sh_node_type_base(&ntype, SH_NODE_BSDF_NODE_NAME, "Node Name", NODE_CLASS_SHADER, 0);'
#                                 'node_type_socket_templates(&ntype, sh_node_bsdf_node_name_in, sh_node_bsdf_node_name_out);'
#                                 'node_type_init(&ntype, node_shader_init_bsdf_node_name);'
#                                 'node_type_storage(&ntype, "NodeBsdfNodeName", node_free_standard_storage, node_copy_standard_storage);'
#                                 'node_type_gpu(&ntype, gpu_shader_bsdf_node_name);'
#                                 'node_type_update(&ntype, node_shader_update_bsdf_node_name);'
#                                 '\n\n'
#                                 'nodeRegisterType(&ntype);'
#                                 '}\n')

#     def test_generate_node_register_no_update_correct_formatting(self):
#         code_gen = self._create_default_class()
#         text = code_gen.generate_node_shader_register()

#         self.assertTrue(text == 'void register_node_type_sh_node_name(void)'
#                                 '{'
#                                 'static bNodeType ntype;\n\n'
#                                 'sh_node_type_base(&ntype, SH_NODE_NODE_NAME, "Node Name", NODE_CLASS_SHADER, 0);'
#                                 'node_type_socket_templates(&ntype, sh_node_node_name_in, sh_node_node_name_out);'
#                                 'node_type_init(&ntype, node_shader_init_node_name);'
#                                 'node_type_storage(&ntype, "NodeNodeName", node_free_standard_storage, node_copy_standard_storage);'
#                                 'node_type_gpu(&ntype, gpu_shader_node_name);'
#                                 '\n\n'
#                                 'nodeRegisterType(&ntype);'
#                                 '}\n')

#     def test_generate_node_register_no_dna_correct_formatting(self):
#         props = [
#             {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
#              "options": [{"name": "prop1", "desc": "Short description"},
#                          {"name": "prop2", "desc": "Short description"}],
#              "default": 'prop1'},
#             {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
#              "options": [{"name": "prop3", "desc": "Short description"},
#                          {"name": "prop4", "desc": "Short description"}],
#              "default": 'prop3'}]
#         code_gen = self._create_default_class(props=props)
#         text = code_gen.generate_node_shader_register()

#         self.assertTrue(text == 'void register_node_type_sh_node_name(void)'
#                                 '{'
#                                 'static bNodeType ntype;\n\n'
#                                 'sh_node_type_base(&ntype, SH_NODE_NODE_NAME, "Node Name", NODE_CLASS_SHADER, 0);'
#                                 'node_type_socket_templates(&ntype, sh_node_node_name_in, sh_node_node_name_out);'
#                                 'node_type_init(&ntype, node_shader_init_node_name);'
#                                 'node_type_storage(&ntype, "", NULL, NULL);'
#                                 'node_type_gpu(&ntype, gpu_shader_node_name);'
#                                 'node_type_update(&ntype, node_shader_update_node_name);'
#                                 '\n\n'
#                                 'nodeRegisterType(&ntype);'
#                                 '}\n')


# if __name__ == '__main__':
#     unittest.main()
