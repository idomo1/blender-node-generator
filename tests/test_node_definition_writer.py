# import unittest
# from unittest import mock
# from unittest.mock import patch, mock_open

# from code_generation.node_definition_writer import NodeDefinitionWriter
# from node_types.prop_bool import BoolProp
# from node_types.prop_enum import EnumProp
# from node_types.prop_int import IntProp
# from node_types.socket_float import FloatSocket
# from node_types.socket_vector import VectorSocket


# class TestWritesNodeDefinition(unittest.TestCase):
#     @classmethod
#     def setUp(cls):
#         cls._mock_gui = mock.Mock()

#     def _create_default_class(self, props=None, sockets=None, node_type='Shader', uses_texture_mapping=False,
#                               socket_availability=None, node_group='Shader'):
#         self._mock_gui.get_node_name.return_value = "Node Name"
#         self._mock_gui.get_node_type.return_value = "Shader"
#         self._mock_gui.get_props.return_value = [
#             {"name": "dropdown1", 'data-type': EnumProp(), "sub-type": "PROP_NONE",
#              "options": [{"name": "prop1", "desc": "Short description"},
#                          {"name": "prop2", "desc": "Short description"}],
#              "default": 'prop1'},
#             {"name": "dropdown2", 'data-type': EnumProp(), "sub-type": "PROP_NONE",
#              "options": [{"name": "prop3", "desc": "Short description"},
#                          {"name": "prop4", "desc": "Short description"}],
#              "default": 'prop3'},
#             {"name": "int1", 'data-type': IntProp(), "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
#             {"name": "box1", 'data-type': BoolProp(), "sub-type": "PROP_NONE", "default": 0},
#             {"name": "box2", 'data-type': BoolProp(), "sub-type": "PROP_NONE", "default": 1}] if props is None else props
#         self._mock_gui.is_texture_node.return_value = node_type == 'Texture'
#         self._mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data-type': FloatSocket(),
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0", 'default': "0.5"},
#                                                        {'type': "Output", 'name': "socket2", 'data-type': FloatSocket(),
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0",
#                                                         }] if sockets is None else sockets
#         self._mock_gui.uses_texture_mapping.return_value = uses_texture_mapping
#         if node_type == 'Texture':
#             suff = 'tex'
#             suffix = 'texture'
#         elif node_type == 'Bsdf':
#             suff = 'bsdf'
#             suffix = suff
#         else:
#             suff = ''
#             suffix = suff
#         self._mock_gui.type_suffix_abbreviated.return_value = suff
#         self._mock_gui.type_suffix.return_value = suffix
#         self._mock_gui.get_node_group.return_value = node_group
#         return NodeDefinitionWriter(self._mock_gui)

#     def test_generate_socket_definitions_vector_correct_formatting(self):
#         sockets = [{'type': "Input", 'name': "socket1", 'data-type': VectorSocket(),
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0", 'default': "0.1,0.2,0.3"},
#                                                        {'type': "Output", 'name': "socket2", 'data-type': VectorSocket(),
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0"}]
#         writer = self._create_default_class(sockets=sockets)
#         defs = writer._generate_node_shader_sockets()
#         self.assertTrue(defs ==
#                         'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#                         '{SOCK_VECTOR, N_("Socket1"), 0.1f, 0.2f, 0.3f, 0.0f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n'
#                         'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#                         '{SOCK_VECTOR, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n')

#     def test_generate_node_init_correct_formatting(self):
#         code_gen = self._create_default_class()
#         text = code_gen._generate_node_shader_init()

#         self.assertTrue(text ==
#                         'static void node_shader_init_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#                         '{'
#                         'NodeNodeName *attr = MEM_cnew<NodeNodeName>(__func__);'
#                         'attr->dropdown1 = SHD_NODE_NAME_PROP1;'
#                         'attr->dropdown2 = SHD_NODE_NAME_PROP3;'
#                         'attr->int1 = 0;'
#                         'attr->box1 = 0;'
#                         'attr->box2 = 1;'
#                         'attr->float1 = 0.0f;\n\n'
#                         'node->storage = attr;'
#                         '}\n\n')

#     def test_generate_node_init_texture_node_with_vector_correct_formatting(self):
#         sockets = [{'type': "Input", 'name': "socket1", 'data-type': FloatSocket(),
#                                                         'sub-type': 'PROP_NONE', 'flag': [],
#                                                         'min': "-1.0", 'max': "1.0", 'default': "0.5"},
#                    {'type': "Output", 'name': "socket2", 'data-type': "Float",
#                                                         'sub-type': 'PROP_NONE', 'flag': [],
#                                                         'min': "-1.0", 'max': "1.0",
#                                                         'default': "0.5"}]
#         sockets.insert(0, {'type': "Input", 'name': "vec1", 'data-type': VectorSocket(),
#                                                                'sub-type': 'PROP_NONE', 'flag': [],
#                                                                'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0",
#                                                                'default': "0.5,0.5,0.5"})

#         code_gen = self._create_default_class(sockets=sockets, node_type='Texture', uses_texture_mapping=True)
#         text = code_gen._generate_node_shader_init()

#         self.assertTrue(text == 'static void node_shader_init_tex_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#                                 '{'
#                                 'NodeTexNodeName *tex = MEM_cnew<NodeNodeName>(__func__);'
#                                 'BKE_texture_mapping_default(&tex->base.tex_mapping, TEXMAP_TYPE_POINT);'
#                                 'BKE_texture_colormapping_default(&tex->base.color_mapping);'
#                                 'tex->dropdown1 = SHD_NODE_NAME_PROP1;'
#                                 'tex->dropdown2 = SHD_NODE_NAME_PROP3;'
#                                 'tex->int1 = 0;'
#                                 'tex->box1 = 0;'
#                                 'tex->box2 = 1;'
#                                 '\n\n'
#                                 'node->storage = tex;'
#                                 '}\n\n')

#     def test_generate_node_init_texture_node_no_vector_correct_formatting(self):
#         code_gen = self._create_default_class(node_type='Texture')
#         text = code_gen._generate_node_shader_init()

#         self.assertTrue(text == 'static void node_shader_init_tex_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#                                 '{'
#                                 'NodeTexNodeName *tex = MEM_cnew<NodeNodeName>(__func__);'
#                                 'tex->dropdown1 = SHD_NODE_NAME_PROP1;'
#                                 'tex->dropdown2 = SHD_NODE_NAME_PROP3;'
#                                 'tex->int1 = 0;'
#                                 'tex->box1 = 0;'
#                                 'tex->box2 = 1;'
#                                 '\n\n'
#                                 'node->storage = tex;'
#                                 '}\n\n')

#     def test_generate_node_init_bsdf_correct_formatting(self):
#         code_gen = self._create_default_class(node_type='Bsdf')
#         text = code_gen._generate_node_shader_init()

#         self.assertTrue(text == 'static void node_shader_init_bsdf_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#                                 '{'
#                                 'NodeBsdfNodeName *attr = MEM_cnew<NodeBsdfNodeName>(__func__);'
#                                 'attr->dropdown1 = SHD_NODE_NAME_PROP1;'
#                                 'attr->dropdown2 = SHD_NODE_NAME_PROP3;'
#                                 'attr->int1 = 0;'
#                                 'attr->box1 = 0;'
#                                 'attr->box2 = 1;'
#                                 '\n\n'
#                                 'node->storage = attr;'
#                                 '}\n\n')

#     def test_generate_node_init_no_dna_correct_formatting(self):
#         props = [
#             {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
#              "options": [{"name": "prop1", "desc": "Short description"},
#                          {"name": "prop2", "desc": "Short description"}],
#              "default": 'prop1'},
#             {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
#             {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
#         code_gen = self._create_default_class(props=props)
#         text = code_gen._generate_node_shader_init()

#         self.assertTrue(text == 'static void node_shader_init_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#                                 '{'
#                                 'node->custom1 = SHD_NODE_NAME_PROP1;'
#                                 'node->custom2 = 0;'
#                                 'node->custom3 = 0.0f;\n\n'
#                                 '}\n\n')

#     # def test_generate_node_init_no_dna_two_bools_correct_formatting(self):
#     #     props = [
#     #         {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
#     #          "options": [{"name": "prop1", "desc": "Short description"},
#     #                      {"name": "prop2", "desc": "Short description"}],
#     #          "default": 'prop1'},
#     #         {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
#     #         {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
#     #         {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
#     #     code_gen = self._create_default_class(props=props)
#     #     text = code_gen._generate_node_shader_init()

#     #     self.assertTrue(text == 'static void node_shader_init_node_name(bNodeTree *UNUSED(ntree), bNode *node)'
#     #                             '{'
#     #                             'node->custom1 = SHD_NODE_NAME_PROP1;'
#     #                             'node->custom2 |= 1 << 0;'
#     #                             'node->custom2 |= 0 << 1;'
#     #                             'node->custom3 = 0.0f;\n\n'
#     #                             '}\n\n')

#     # def test_generate_socket_definitions_correct_formatting(self):
#     #     code_gen = self._create_default_class()
#     #     defs = code_gen._generate_node_shader_sockets()

#     #     self.assertTrue(defs ==
#     #                     'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket1"), 0.5f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n'
#     #                     'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n')

#     # def test_generate_socket_definitions_two_inputs_correct_formatting(self):
#     #     sockets = [{'type': "Input", 'name': "socket1", 'data-type': FloatSocket(),
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0", 'default': "0.5"},
#     #                                                    {'type': "Output", 'name': "socket2", 'data-type': FloatSocket(),
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0"},
#     #                                                    {'type': "Input", 'name': "socket3", 'data-type': FloatSocket(),
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0", 'default': "0.5"}
#     #                                                    ]
#     #     code_gen = self._create_default_class(sockets=sockets)
#     #     defs = code_gen._generate_node_shader_sockets()

#     #     self.assertTrue(defs ==
#     #                     'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket1"), 0.5f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{SOCK_FLOAT, N_("Socket3"), 0.5f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n'
#     #                     'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n')

#     # def test_generate_socket_definitions_two_outputs_correct_formatting(self):
#     #     sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0", 'default': "0.5"},
#     #                                                    {'type': "Output", 'name': "socket2", 'data-type': "Float",
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0"},
#     #                                                    {'type': "Output", 'name': "socket3", 'data-type': "Float",
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0"}
#     #                                                    ]
#     #     code_gen = self._create_default_class(sockets=sockets)
#     #     defs = code_gen._generate_node_shader_sockets()

#     #     self.assertTrue(defs ==
#     #                     'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket1"), 0.5f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n'
#     #                     'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{SOCK_FLOAT, N_("Socket3"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n')

#     # def test_generate_socket_definitions_no_inputs_correct_formatting(self):
#     #     sockets = [{'type': "Output", 'name': "socket2", 'data-type': "Float",
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0"}]
#     #     code_gen = self._create_default_class(sockets=sockets)
#     #     defs = code_gen._generate_node_shader_sockets()

#     #     self.assertTrue(defs ==
#     #                     'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n')

#     # def test_generate_socket_definitions_no_outputs_correct_formatting(self):
#     #     sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
#     #                                                     'sub-type': 'PROP_NONE', 'flag': 'None',
#     #                                                     'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
#     #     code_gen = self._create_default_class(sockets=sockets)
#     #     defs = code_gen._generate_node_shader_sockets()

#     #     self.assertTrue(defs ==
#     #                     'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#     #                     '{SOCK_FLOAT, N_("Socket1"), 0.5f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#     #                     '{-1, ""},'
#     #                     '};\n\n')

#     def test_generate_socket_definitions_no_sockets_correct_formatting(self):
#         code_gen = self._create_default_class(sockets=[])
#         defs = code_gen._generate_node_shader_sockets()

#         self.assertTrue(defs == '')

#     def test_generate_socket_definitions_rgba_correct_formatting(self):
#         sockets = [{'type': "Input", 'name': "socket1", 'data-type': "RGBA",
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0", 'default': "0.1,0.2,0.3"},
#                                                        {'type': "Output", 'name': "socket2", 'data-type': "RGBA",
#                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
#                                                         'min': "-1.0", 'max': "1.0"}]
#         code_gen = self._create_default_class(sockets=sockets)
#         defs = code_gen._generate_node_shader_sockets()

#         self.assertTrue(defs ==
#                         'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#                         '{SOCK_RGBA, N_("Socket1"), 0.1f, 0.2f, 0.3f, 0.0f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n'
#                         'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#                         '{SOCK_RGBA, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n')

#     def test_generate_socket_definitions_four_defaults_correct_formatting(self):
#         sockets = \
#             [{'type': "Input", 'name': "socket1", 'data-type': "Vector",
#               'sub-type': 'PROP_NONE', 'flag': 'None',
#               'min': "-1.0", 'max': "1.0", 'default': "0.1,0.2,0.3,0.4"},
#              {'type': "Output", 'name': "socket2", 'data-type': "Vector",
#               'sub-type': 'PROP_NONE', 'flag': 'None',
#               'min': "-1.0", 'max': "1.0"}]
#         code_gen = self._create_default_class(sockets=sockets)
#         defs = code_gen._generate_node_shader_sockets()

#         self.assertTrue(defs ==
#                         'static bNodeSocketTemplate sh_node_node_name_in[] = {'
#                         '{SOCK_VECTOR, N_("Socket1"), 0.1f, 0.2f, 0.3f, 0.4f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n'
#                         'static bNodeSocketTemplate sh_node_node_name_out[] = {'
#                         '{SOCK_VECTOR, N_("Socket2"), 0.0f, 0.0f, 0.0f, 0.0f, -1.0f, 1.0f},'
#                         '{-1, ""},'
#                         '};\n\n')


# if __name__ == '__main__':
#     unittest.main()
