import unittest
from unittest import mock
from unittest.mock import patch, mock_open, call

from code_generation import CodeGenerator


class TestCodeGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_gui = mock.Mock()

    def setUp(self):
        """
        Sets mock gui with default values
        """
        self.mock_gui.get_node_name.return_value = "Node Name"
        self.mock_gui.get_node_type.return_value = "Shader"
        self.mock_gui.get_node_group.return_value = "Shader"
        self.mock_gui.get_source_path.return_value = "C:/some/path"
        self.mock_gui.get_poll.return_value = None
        self.mock_gui.get_node_group_level.return_value = 3
        self.mock_gui.get_node_check_box_count.return_value = 2
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": 'prop3'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        self.mock_gui.is_texture_node.return_value = False
        self.mock_gui.node_has_properties.return_value = True
        self.mock_gui.node_has_check_box.return_value = True
        self.mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                                                        'sub-type': 'PROP_NONE', 'flag': 'None',
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                                                       {'type': "Output", 'name': "socket2", 'data-type': "Float",
                                                        'sub-type': 'PROP_NONE', 'flag': 'None',
                                                        'min': "-1.0", 'max': "1.0"}]
        self.mock_gui.get_socket_availability_maps.return_value = [{'socket-name': 'socket1', 'socket-type': 'in',
                                                                    'prop-avail': [('dropdown1=prop1', True),
                                                                                   ('dropdown1=prop2', True),
                                                                                   ('dropdown2=prop3', True),
                                                                                   ('dropdown2=prop4', True),
                                                                                   ('box1=True', True),
                                                                                   ('box1=False', True),
                                                                                   ('box2=True', True),
                                                                                   ('box2=False', True)]},
                                                                   {'socket-name': 'socket2', 'socket-type': 'out',
                                                                    'prop-avail': [('dropdown1=prop1', True),
                                                                                   ('dropdown1=prop2', True),
                                                                                   ('dropdown2=prop3', True),
                                                                                   ('dropdown2=prop4', False),
                                                                                   ('box1=True', False),
                                                                                   ('box1=False', True),
                                                                                   ('box2=True', True),
                                                                                   ('box2=False', True)]}
                                                                   ]
        self.mock_gui.socket_availability_changes.return_value = True
        self.mock_gui.uses_texture_mapping.return_value = False
        self.mock_gui.type_suffix_abbreviated.return_value = ''
        self.mock_gui.type_suffix.return_value = ''

    def test_write_to_node_menu_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data=
                                              'ShaderNodeCategory("SH_NEW_TEXTURE", "Texture", items=[\n'
                                              ']),\n'
                                              'ShaderNodeCategory("SH_NEW_SHADER", "Shader", items=[\n'
                                              '    NodeItem("ShaderNodeMixShader", poll=eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeAddShader", poll=eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfDiffuse", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfPrincipled", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfGlossy", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfTransparent", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfRefraction", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfGlass", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfTranslucent", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfAnisotropic", poll=object_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfVelvet", poll=object_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfToon", poll=object_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeSubsurfaceScattering", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeEmission", poll=eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfHair", poll=object_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBackground", poll=world_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeHoldout", poll=object_eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeVolumeAbsorption", poll=eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeVolumeScatter", poll=eevee_cycles_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeVolumePrincipled"),\n'
                                              '    NodeItem("ShaderNodeEeveeSpecular", poll=object_eevee_shader_nodes_poll),\n'
                                              '    NodeItem("ShaderNodeBsdfHairPrincipled", poll=object_cycles_shader_nodes_poll)\n'
                                              ']),\n'
                                              'ShaderNodeCategory("SH_NEW_TEXTURE", "Texture", items=[\n'
                                              )) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_to_node_menu()

            self.assertTrue('        NodeItem("ShaderNodeNodeName")\n' in mf.mock_calls[4][1][0])

    def test_write_node_id_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data='#define SH_NODE_TEX_WHITE_NOISE 704\n'
                                                        '#define SH_NODE_VOLUME_INFO 705\n'
                                                        '#define SH_NODE_VERTEX_COLOR 706\n'
                                                        '\n'
                                                        '/* custom defines options for Material node */\n'
                                                        '#define SH_NODE_MAT_DIFF 1\n'
                                                        '#define SH_NODE_MAT_SPEC 2\n'
                                                        '#define SH_NODE_MAT_NEG 4\n'
                                              )) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_node_type_id()
            self.assertTrue(mf.mock_calls[-3][1][0] == '#define SH_NODE_TEX_WHITE_NOISE 704\n'
                                                       '#define SH_NODE_VOLUME_INFO 705\n'
                                                       '#define SH_NODE_VERTEX_COLOR 706\n'
                                                       '#define SH_NODE_NODE_NAME 707\n'
                                                       '\n'
                                                       '/* custom defines options for Material node */\n'
                                                       '#define SH_NODE_MAT_DIFF 1\n'
                                                       '#define SH_NODE_MAT_SPEC 2\n'
                                                       '#define SH_NODE_MAT_NEG 4\n')

    def test_write_node_class_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'ustring string1;'
                                                           '};')

    def test_write_node_class_level_0_correct_formatting(self):
        self.mock_gui.get_node_group_level.return_value = 0
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'ustring string1;'
                                                           '};')

    def test_write_node_class_no_bools_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", 'data-type': "Enum", "options": [{"name": "prop1", "desc": "Short description"},
                                                                   {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "options": [{"name": "prop3", "desc": "Short description"},
                                                                   {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "int1", 'data-type': "Int", "default": 0, "min": -1, "max": 1},
            {"name": "float1", 'data-type': "Float", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'ustring string1;'
                                                           '};')

    def test_write_node_class_no_enums_correct_formatting(self):
        self.mock_gui.get_props.return_value = [{"name": "box1", 'data-type': "Boolean", "default": 0},
                                                {"name": "box2", 'data-type': "Boolean", "default": 1},
                                                {"name": "int1", 'data-type': "Int", "default": 0, "min": -1, "max": 1},
                                                {"name": "float1", 'data-type': "Float", "default": 0.0, "min": -1.0,
                                                 "max": 1.0},
                                                {"name": "string1", 'data-type': "String", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'bool box1, box2;'
                                                           'int int1;'
                                                           'ustring string1;'
                                                           '};')

    def test_write_node_class_no_sockets_correct_formatting(self):
        self.mock_gui.get_node_sockets.return_value = []
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'float float1;'
                                                           'ustring string1;'
                                                           '};')

    def test_write_node_class_no_props_correct_formatting(self):
        self.mock_gui.get_props.return_value = []
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1;'
                                                           '};')

    def test_write_node_class_no_props_or_sockets_correct_formatting(self):
        self.mock_gui.get_props.return_value = []
        self.mock_gui.get_node_sockets.return_value = []
        with patch('builtins.open', mock_open(read_data='};\n'
                                                        '\n'
                                                        'class VectorDisplacementNode : public ShaderNode {\n'
                                                        'public:\n'
                                                        ' SHADER_NODE_CLASS(VectorDisplacementNode)\n'
                                                        ' void attributes(Shader *shader, AttributeRequestSet *attributes);\n'
                                                        ' bool has_attribute_dependency()\n'
                                                        ' {\n'
                                                        '   return true;\n'
                                                        ' }\n'
                                                        ' void constant_fold(const ConstantFolder &folder);\n'
                                                        ' virtual int get_feature()\n'
                                                        ' {\n'
                                                        '   return NODE_FEATURE_BUMP;\n'
                                                        ' }\n'
                                                        '\n'
                                                        ' NodeNormalMapSpace space;\n'
                                                        ' ustring attribute;\n'
                                                        ' float3 vector;\n'
                                                        ' float midlevel;\n'
                                                        ' float scale;\n'
                                                        '};\n'
                                                        '\n'
                                                        'CCL_NAMESPACE_END\n'
                                                        '\n'
                                                        '#endif /* __NODES_H__ */\n'
                                                        '\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)\n'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           '};')

    def test_add_cycles_class_instance_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeNodeName)) {'
                                'BL::ShaderNodeNodeName b_node_name_node(b_node);'
                                'NodeNameNode *node_name = new NodeNameNode();'
                                'node_name->dropdown1 = b_node_name_node.dropdown1();'
                                'node_name->dropdown2 = b_node_name_node.dropdown2();'
                                'node_name->int1 = b_node_name_node.int1();'
                                'node_name->box1 = b_node_name_node.box1();'
                                'node_name->box2 = b_node_name_node.box2();'
                                'node_name->float1 = b_node_name_node.float1();'
                                'node_name->string1 = b_node_name_node.string1();'
                                'node = node_name;'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_texture_node_no_vector_correct_formatting(self):
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeTexNodeName)) {'
                                'BL::ShaderNodeTexNodeName b_node_name_node(b_node);'
                                'NodeNameTextureNode *node_name = new NodeNameTextureNode();'
                                'node_name->dropdown1 = b_node_name_node.dropdown1();'
                                'node_name->dropdown2 = b_node_name_node.dropdown2();'
                                'node_name->int1 = b_node_name_node.int1();'
                                'node_name->box1 = b_node_name_node.box1();'
                                'node_name->box2 = b_node_name_node.box2();'
                                'node_name->float1 = b_node_name_node.float1();'
                                'node_name->string1 = b_node_name_node.string1();'
                                'node = node_name;'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_bsdf_node_correct_formatting(self):
        self.mock_gui.type_suffix_abbreviated.return_value = 'bsdf'
        self.mock_gui.type_suffix.return_value = 'bsdf'
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeBsdfNodeName)) {'
                                'BL::ShaderNodeBsdfNodeName b_node_name_node(b_node);'
                                'NodeNameBsdfNode *node_name = new NodeNameBsdfNode();'
                                'node_name->dropdown1 = b_node_name_node.dropdown1();'
                                'node_name->dropdown2 = b_node_name_node.dropdown2();'
                                'node_name->int1 = b_node_name_node.int1();'
                                'node_name->box1 = b_node_name_node.box1();'
                                'node_name->box2 = b_node_name_node.box2();'
                                'node_name->float1 = b_node_name_node.float1();'
                                'node_name->string1 = b_node_name_node.string1();'
                                'node = node_name;'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_texture_node_with_vector_correct_formatting(self):
        self.mock_gui.uses_texture_mapping.return_value = True
        self.mock_gui.get_node_sockets.return_value.insert(0, {'type': "Input", 'name': "vec1", 'data-type': "Vector",
                                                               'sub-type': 'PROP_NONE', 'flag': 'None',
                                                               'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0",
                                                               'default': "0.5,0.5,0.5"})
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeTexNodeName)) {'
                                'BL::ShaderNodeTexNodeName b_node_name_node(b_node);'
                                'NodeNameTextureNode *node_name = new NodeNameTextureNode();'
                                'node_name->dropdown1 = b_node_name_node.dropdown1();'
                                'node_name->dropdown2 = b_node_name_node.dropdown2();'
                                'node_name->int1 = b_node_name_node.int1();'
                                'node_name->box1 = b_node_name_node.box1();'
                                'node_name->box2 = b_node_name_node.box2();'
                                'node_name->float1 = b_node_name_node.float1();'
                                'node_name->string1 = b_node_name_node.string1();'
                                'BL::TexMapping b_texture_mapping(b_node_name_node.texture_mapping());'
                                'get_tex_mapping(&node_name->tex_mapping, b_texture_mapping);'
                                'node = node_name;'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_no_props_correct_formatting(self):
        self.mock_gui.get_props.return_value = []
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeNodeName)) {'
                                'node = new NodeNameNode();'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_texture_node_no_props_with_vector_correct_formatting(self):
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.get_props.return_value = []
        self.mock_gui.uses_texture_mapping.return_value = True
        self.mock_gui.get_node_sockets.return_value.insert(0, {'type': "Input", 'name': "vec1", 'data-type': "Vector",
                                                               'sub-type': 'PROP_NONE', 'flag': 'None',
                                                               'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0",
                                                               'default': "0.5,0.5,0.5"})
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeTexNodeName)) {'
                                'BL::ShaderNodeTexNodeName b_node_name_node(b_node);'
                                'NodeNameTextureNode *node_name = new NodeNameTextureNode();'
                                'BL::TexMapping b_texture_mapping(b_node_name_node.texture_mapping());'
                                'get_tex_mapping(&node_name->tex_mapping, b_texture_mapping);'
                                'node = node_name;'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_class_instance_texture_node_no_props_no_vector_correct_formatting(self):
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.get_props.return_value = []
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'static ShaderNode *add_node(Scene *scene,\n'
                                              'BL::RenderEngine &b_engine,\n'
                                              'BL::BlendData &b_data,\n'
                                              'BL::Depsgraph &b_depsgraph,\n'
                                              'BL::Scene &b_scene,\n'
                                              'ShaderGraph *graph,\n'
                                              'BL::ShaderNodeTree &b_ntree,\n'
                                              'BL::ShaderNode &b_node)\n'
                                              '{\n'
                                              'ShaderNode *node = NULL;\n\n'

                                              '/* existing blender nodes */\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeRGBCurve)) {\n'
                                              'BL::ShaderNodeRGBCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'RGBCurvesNode *curves = new RGBCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, true);\n'
                                              'curvemapping_minmax(mapping, true, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              'if (b_node.is_a(&RNA_ShaderNodeVectorCurve)) {\n'
                                              'BL::ShaderNodeVectorCurve b_curve_node(b_node);\n'
                                              'BL::CurveMapping mapping(b_curve_node.mapping());\n'
                                              'VectorCurvesNode *curves = new VectorCurvesNode();\n'
                                              'curvemapping_color_to_array(mapping, curves->curves, RAMP_TABLE_SIZE, false);\n'
                                              'curvemapping_minmax(mapping, false, &curves->min_x, &curves->max_x);\n'
                                              'node = curves;\n'
                                              '}\n'
                                              '  else if (b_node.is_a(&RNA_ShaderNodeVectorDisplacement)) {\n'
                                              'BL::ShaderNodeVectorDisplacement b_disp_node(b_node);\n'
                                              'VectorDisplacementNode *disp = new VectorDisplacementNode();\n'
                                              'disp->space = (NodeNormalMapSpace)b_disp_node.space();\n'
                                              'disp->attribute = "";\n'
                                              'node = disp;\n'
                                              '}\n\n'
                                              'if (node) {\n'
                                              'node->name = b_node.name();\n'
                                              'graph->add(node);\n'
                                              '}\n'
                                              'return node;\n'
                                              '}\n'
                                              )) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class_instance()

                self.assertTrue('else if (b_node.is_a(&RNA_ShaderNodeTexNodeName)) {'
                                'node = new NodeNameTextureNode();'
                                '}\n' in mf.mock_calls[-3][1][0])

    def test_add_cycles_node_correct_formatting(self):
        mock_svm_manager = mock.Mock()
        mock_svm_manager.return_value = 'void NodeNameNode::compile(SVMCompiler &compiler){' \
                                        'ShaderInput *socket1_in = input("Socket1");' \
                                        'ShaderOutput *socket2_out = output("Socket2");\n\n' \
                                        'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);' \
                                        'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n' \
                                        'compiler.add_node(NODE_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), ' \
                                        'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), ' \
                                        'socket2_stack_offset' \
                                        ');' \
                                        'compiler.add_node(__float_as_int(socket1));' \
                                        '}\n\n'
        with patch('builtins.open', mock_open(read_data=
                                              'void VectorDisplacementNode::compile(OSLCompiler &compiler)\n'
                                              '{\n'
                                              'if (space == NODE_NORMAL_MAP_TANGENT) {\n'
                                              '  if (attribute.empty()) {\n'
                                              '    compiler.parameter("attr_name", ustring("geom:tangent"));\n'
                                              '    compiler.parameter("attr_sign_name", ustring("geom:tangent_sign"));\n'
                                              '  }\n'
                                              '  else {\n'
                                              '    compiler.parameter("attr_name", ustring((string(attribute.c_str()) + ".tangent").c_str()));\n'
                                              '    compiler.parameter("attr_sign_name",\n'
                                              '                       ustring((string(attribute.c_str()) + ".tangent_sign").c_str()));\n'
                                              '  }\n'
                                              '}\n\n'
                                              'compiler.parameter(this, "space");\n'
                                              'compiler.add(this, "node_vector_displacement");\n'
                                              '}\n\n'
                                              'CCL_NAMESPACE_END\n\n'
                                              )) as mf:
            with patch('code_generation.svm_writer.SVMWriter.generate_svm_compile_func',
                       mock_svm_manager):
                with patch('code_generation.code_generator_util.apply_clang_formatting'):
                    code_gen = CodeGenerator(self.mock_gui)
                    code_gen._add_cycles_node()
                    self.assertTrue(mf.mock_calls[-3][1][0] == '/* Node Name */\n\n'
                                                               'NODE_DEFINE(NodeNameNode){'
                                                               'NodeType *type = NodeType::add("node_name", create, NodeType::SHADER);\n\n'
                                                               'static NodeEnum dropdown1_enum;'
                                                               'dropdown1_enum.insert("PROP1", 1);'
                                                               'dropdown1_enum.insert("PROP2", 2);'
                                                               'SOCKET_ENUM(dropdown1, "Dropdown1", dropdown1_enum, 1);\n\n'
                                                               'static NodeEnum dropdown2_enum;'
                                                               'dropdown2_enum.insert("PROP3", 1);'
                                                               'dropdown2_enum.insert("PROP4", 2);'
                                                               'SOCKET_ENUM(dropdown2, "Dropdown2", dropdown2_enum, 1);\n\n'
                                                               'SOCKET_INT(int1, "Int1", 0);'
                                                               'SOCKET_BOOLEAN(box1, "Box1", false);'
                                                               'SOCKET_BOOLEAN(box2, "Box2", true);'
                                                               'SOCKET_FLOAT(float1, "Float1", 0.0f);'
                                                               'SOCKET_STRING(string1, "String1", ustring());\n\n'
                                                               'SOCKET_IN_FLOAT(socket1, "Socket1", 0.5f);'
                                                               'SOCKET_OUT_FLOAT(socket2, "Socket2");\n\n'
                                                               'return type;'
                                                               '}\n\n'
                                                               'NodeNameNode::NodeNameNode() : ShaderNode(node_type)'
                                                               '{'
                                                               '}\n\n'
                                                               'void NodeNameNode::compile(SVMCompiler &compiler){'
                                                               'ShaderInput *socket1_in = input("Socket1");'
                                                               'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                                               'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                                               'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                                               'compiler.add_node(NODE_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                                               'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                                               'socket2_stack_offset'
                                                               ');'
                                                               'compiler.add_node(__float_as_int(socket1));'
                                                               '}\n\n'
                                                               'void NodeNameNode::compile(OSLCompiler &compiler)'
                                                               '{'
                                                               'compiler.parameter(this, "dropdown1");'
                                                               'compiler.parameter(this, "dropdown2");'
                                                               'compiler.parameter(this, "int1");'
                                                               'compiler.parameter(this, "box1");'
                                                               'compiler.parameter(this, "box2");'
                                                               'compiler.parameter(this, "float1");'
                                                               'compiler.add(this, "node_node_name");'
                                                               '}\n\n'
                                    )

    def test_add_cycles_node_texture_node_no_vector_correct_formatting(self):
        mock_svm_manager = mock.Mock()
        mock_svm_manager.return_value = 'void NodeNameTextureNode::compile(SVMCompiler &compiler){' \
                                        'ShaderInput *socket1_in = input("Socket1");' \
                                        'ShaderOutput *socket2_out = output("Socket2");\n\n' \
                                        'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);' \
                                        'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n' \
                                        'compiler.add_node(NODE_TEX_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), ' \
                                        'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), ' \
                                        'socket2_stack_offset' \
                                        ');' \
                                        'compiler.add_node(__float_as_int(socket1));' \
                                        '}\n\n'
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'void VectorDisplacementNode::compile(OSLCompiler &compiler)\n'
                                              '{\n'
                                              'if (space == NODE_NORMAL_MAP_TANGENT) {\n'
                                              '  if (attribute.empty()) {\n'
                                              '    compiler.parameter("attr_name", ustring("geom:tangent"));\n'
                                              '    compiler.parameter("attr_sign_name", ustring("geom:tangent_sign"));\n'
                                              '  }\n'
                                              '  else {\n'
                                              '    compiler.parameter("attr_name", ustring((string(attribute.c_str()) + ".tangent").c_str()));\n'
                                              '    compiler.parameter("attr_sign_name",\n'
                                              '                       ustring((string(attribute.c_str()) + ".tangent_sign").c_str()));\n'
                                              '  }\n'
                                              '}\n\n'
                                              'compiler.parameter(this, "space");\n'
                                              'compiler.add(this, "node_vector_displacement");\n'
                                              '}\n\n'
                                              'CCL_NAMESPACE_END\n\n'
                                              )) as mf:
            with patch('code_generation.svm_writer.SVMWriter.generate_svm_compile_func',
                       mock_svm_manager):
                with patch('code_generation.code_generator_util.apply_clang_formatting'):
                    code_gen = CodeGenerator(self.mock_gui)
                    code_gen._add_cycles_node()

                    self.assertTrue(mf.mock_calls[-3][1][0] == '/* Node Name Texture */\n\n'
                                                               'NODE_DEFINE(NodeNameTextureNode){'
                                                               'NodeType *type = NodeType::add("node_name_texture", create, NodeType::SHADER);\n\n'
                                                               'static NodeEnum dropdown1_enum;'
                                                               'dropdown1_enum.insert("PROP1", 1);'
                                                               'dropdown1_enum.insert("PROP2", 2);'
                                                               'SOCKET_ENUM(dropdown1, "Dropdown1", dropdown1_enum, 1);\n\n'
                                                               'static NodeEnum dropdown2_enum;'
                                                               'dropdown2_enum.insert("PROP3", 1);'
                                                               'dropdown2_enum.insert("PROP4", 2);'
                                                               'SOCKET_ENUM(dropdown2, "Dropdown2", dropdown2_enum, 1);\n\n'
                                                               'SOCKET_INT(int1, "Int1", 0);'
                                                               'SOCKET_BOOLEAN(box1, "Box1", false);'
                                                               'SOCKET_BOOLEAN(box2, "Box2", true);'
                                                               'SOCKET_FLOAT(float1, "Float1", 0.0f);'
                                                               'SOCKET_STRING(string1, "String1", ustring());\n\n'
                                                               'SOCKET_IN_FLOAT(socket1, "Socket1", 0.5f);'
                                                               'SOCKET_OUT_FLOAT(socket2, "Socket2");\n\n'
                                                               'return type;'
                                                               '}\n\n'
                                                               'NodeNameTextureNode::NodeNameTextureNode() : TextureNode(node_type)'
                                                               '{'
                                                               '}\n\n'
                                                               'void NodeNameTextureNode::compile(SVMCompiler &compiler){'
                                                               'ShaderInput *socket1_in = input("Socket1");'
                                                               'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                                               'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                                               'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                                               'compiler.add_node(NODE_TEX_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                                               'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                                               'socket2_stack_offset'
                                                               ');'
                                                               'compiler.add_node(__float_as_int(socket1));'
                                                               '}\n\n'
                                                               'void NodeNameTextureNode::compile(OSLCompiler &compiler)'
                                                               '{'
                                                               'compiler.parameter(this, "dropdown1");'
                                                               'compiler.parameter(this, "dropdown2");'
                                                               'compiler.parameter(this, "int1");'
                                                               'compiler.parameter(this, "box1");'
                                                               'compiler.parameter(this, "box2");'
                                                               'compiler.parameter(this, "float1");'
                                                               'compiler.add(this, "node_node_name_texture");'
                                                               '}\n\n'
                                    )

    def test_add_cycles_node_bsdf_node_correct_formatting(self):
        mock_svm_manager = mock.Mock()
        mock_svm_manager.return_value = 'void NodeNameBsdfNode::compile(SVMCompiler &compiler){' \
                                        'ShaderInput *socket1_in = input("Socket1");' \
                                        'ShaderOutput *socket2_out = output("Socket2");\n\n' \
                                        'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);' \
                                        'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n' \
                                        'compiler.add_node(NODE_BSDF_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), ' \
                                        'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), ' \
                                        'socket2_stack_offset' \
                                        ');' \
                                        'compiler.add_node(__float_as_int(socket1));' \
                                        '}\n\n'
        self.mock_gui.get_node_type.return_value = "Bsdf"
        self.mock_gui.type_suffix_abbreviated.return_value = 'bsdf'
        self.mock_gui.type_suffix.return_value = 'bsdf'
        with patch('builtins.open', mock_open(read_data=
                                              'void VectorDisplacementNode::compile(OSLCompiler &compiler)\n'
                                              '{\n'
                                              'if (space == NODE_NORMAL_MAP_TANGENT) {\n'
                                              '  if (attribute.empty()) {\n'
                                              '    compiler.parameter("attr_name", ustring("geom:tangent"));\n'
                                              '    compiler.parameter("attr_sign_name", ustring("geom:tangent_sign"));\n'
                                              '  }\n'
                                              '  else {\n'
                                              '    compiler.parameter("attr_name", ustring((string(attribute.c_str()) + ".tangent").c_str()));\n'
                                              '    compiler.parameter("attr_sign_name",\n'
                                              '                       ustring((string(attribute.c_str()) + ".tangent_sign").c_str()));\n'
                                              '  }\n'
                                              '}\n\n'
                                              'compiler.parameter(this, "space");\n'
                                              'compiler.add(this, "node_vector_displacement");\n'
                                              '}\n\n'
                                              'CCL_NAMESPACE_END\n\n'
                                              )) as mf:
            with patch('code_generation.svm_writer.SVMWriter.generate_svm_compile_func',
                       mock_svm_manager):
                with patch('code_generation.code_generator_util.apply_clang_formatting'):
                    code_gen = CodeGenerator(self.mock_gui)
                    code_gen._add_cycles_node()

                    self.assertTrue(mf.mock_calls[-3][1][0] == '/* Node Name Bsdf */\n\n'
                                                               'NODE_DEFINE(NodeNameBsdfNode){'
                                                               'NodeType *type = NodeType::add("node_name_bsdf", create, NodeType::SHADER);\n\n'
                                                               'static NodeEnum dropdown1_enum;'
                                                               'dropdown1_enum.insert("PROP1", 1);'
                                                               'dropdown1_enum.insert("PROP2", 2);'
                                                               'SOCKET_ENUM(dropdown1, "Dropdown1", dropdown1_enum, 1);\n\n'
                                                               'static NodeEnum dropdown2_enum;'
                                                               'dropdown2_enum.insert("PROP3", 1);'
                                                               'dropdown2_enum.insert("PROP4", 2);'
                                                               'SOCKET_ENUM(dropdown2, "Dropdown2", dropdown2_enum, 1);\n\n'
                                                               'SOCKET_INT(int1, "Int1", 0);'
                                                               'SOCKET_BOOLEAN(box1, "Box1", false);'
                                                               'SOCKET_BOOLEAN(box2, "Box2", true);'
                                                               'SOCKET_FLOAT(float1, "Float1", 0.0f);'
                                                               'SOCKET_STRING(string1, "String1", ustring());\n\n'
                                                               'SOCKET_IN_FLOAT(socket1, "Socket1", 0.5f);'
                                                               'SOCKET_OUT_FLOAT(socket2, "Socket2");\n\n'
                                                               'return type;'
                                                               '}\n\n'
                                                               'NodeNameBsdfNode::NodeNameBsdfNode() : BsdfNode(node_type)'
                                                               '{'
                                                               '}\n\n'
                                                               'void NodeNameBsdfNode::compile(SVMCompiler &compiler){'
                                                               'ShaderInput *socket1_in = input("Socket1");'
                                                               'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                                               'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                                               'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                                               'compiler.add_node(NODE_BSDF_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                                               'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                                               'socket2_stack_offset'
                                                               ');'
                                                               'compiler.add_node(__float_as_int(socket1));'
                                                               '}\n\n'
                                                               'void NodeNameBsdfNode::compile(OSLCompiler &compiler)'
                                                               '{'
                                                               'compiler.parameter(this, "dropdown1");'
                                                               'compiler.parameter(this, "dropdown2");'
                                                               'compiler.parameter(this, "int1");'
                                                               'compiler.parameter(this, "box1");'
                                                               'compiler.parameter(this, "box2");'
                                                               'compiler.parameter(this, "float1");'
                                                               'compiler.add(this, "node_node_name_bsdf");'
                                                               '}\n\n'
                                    )

    def test_add_cycles_node_texture_node_with_vector_correct_formatting(self):
        mock_svm_manager = mock.Mock()
        mock_svm_manager.return_value = 'void NodeNameTextureNode::compile(SVMCompiler &compiler){' \
                                        'ShaderInput *vector_in = input("Vector");' \
                                        'ShaderInput *socket1_in = input("Socket1");' \
                                        'ShaderOutput *socket2_out = output("Socket2");\n\n' \
                                        'int vector_stack_offset = tex_mapping.compile_begin(compiler, vector_in);' \
                                        'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);' \
                                        'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n' \
                                        'compiler.add_node(NODE_TEX_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), ' \
                                        'compiler.encode_uchar4(box2, __float_as_int(float1), vector_stack_offset, socket1_stack_offset), ' \
                                        'socket2_stack_offset' \
                                        ');' \
                                        'compiler.add_node(__float_as_int(socket1));\n\n' \
                                        'tex_mapping.compile_end(compiler, vector_in, vector_stack_offset);' \
                                        '}\n\n'
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.uses_texture_mapping.return_value = True
        self.mock_gui.get_node_sockets.return_value.insert(0, {'type': "Input", 'name': "vector", 'data-type': "Vector",
                                                               'sub-type': 'PROP_NONE', 'flag': 'None',
                                                               'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0",
                                                               'default': "0.5,0.5,0.5"})
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        self.mock_gui.type_suffix.return_value = 'texture'
        with patch('builtins.open', mock_open(read_data=
                                              'void VectorDisplacementNode::compile(OSLCompiler &compiler)\n'
                                              '{\n'
                                              'if (space == NODE_NORMAL_MAP_TANGENT) {\n'
                                              '  if (attribute.empty()) {\n'
                                              '    compiler.parameter("attr_name", ustring("geom:tangent"));\n'
                                              '    compiler.parameter("attr_sign_name", ustring("geom:tangent_sign"));\n'
                                              '  }\n'
                                              '  else {\n'
                                              '    compiler.parameter("attr_name", ustring((string(attribute.c_str()) + ".tangent").c_str()));\n'
                                              '    compiler.parameter("attr_sign_name",\n'
                                              '                       ustring((string(attribute.c_str()) + ".tangent_sign").c_str()));\n'
                                              '  }\n'
                                              '}\n\n'
                                              'compiler.parameter(this, "space");\n'
                                              'compiler.add(this, "node_vector_displacement");\n'
                                              '}\n\n'
                                              'CCL_NAMESPACE_END\n\n'
                                              )) as mf:
            with patch('code_generation.svm_writer.SVMWriter.generate_svm_compile_func',
                       mock_svm_manager):
                with patch('code_generation.code_generator_util.apply_clang_formatting'):
                    code_gen = CodeGenerator(self.mock_gui)
                    code_gen._add_cycles_node()

                    self.assertTrue(mf.mock_calls[-3][1][0] == '/* Node Name Texture */\n\n'
                                                               'NODE_DEFINE(NodeNameTextureNode){'
                                                               'NodeType *type = NodeType::add("node_name_texture", create, NodeType::SHADER);\n\n'
                                                               'TEXTURE_MAPPING_DEFINE(NodeNameTextureNode);\n\n'
                                                               'static NodeEnum dropdown1_enum;'
                                                               'dropdown1_enum.insert("PROP1", 1);'
                                                               'dropdown1_enum.insert("PROP2", 2);'
                                                               'SOCKET_ENUM(dropdown1, "Dropdown1", dropdown1_enum, 1);\n\n'
                                                               'static NodeEnum dropdown2_enum;'
                                                               'dropdown2_enum.insert("PROP3", 1);'
                                                               'dropdown2_enum.insert("PROP4", 2);'
                                                               'SOCKET_ENUM(dropdown2, "Dropdown2", dropdown2_enum, 1);\n\n'
                                                               'SOCKET_INT(int1, "Int1", 0);'
                                                               'SOCKET_BOOLEAN(box1, "Box1", false);'
                                                               'SOCKET_BOOLEAN(box2, "Box2", true);'
                                                               'SOCKET_FLOAT(float1, "Float1", 0.0f);'
                                                               'SOCKET_STRING(string1, "String1", ustring());\n\n'
                                                               'SOCKET_IN_POINT(vector, "Vector", make_float3(0.5f, 0.5f, 0.5f), SocketType::LINK_TEXTURE_GENERATED);'
                                                               'SOCKET_IN_FLOAT(socket1, "Socket1", 0.5f);'
                                                               'SOCKET_OUT_FLOAT(socket2, "Socket2");\n\n'
                                                               'return type;'
                                                               '}\n\n'
                                                               'NodeNameTextureNode::NodeNameTextureNode() : TextureNode(node_type)'
                                                               '{'
                                                               '}\n\n'
                                                               'void NodeNameTextureNode::compile(SVMCompiler &compiler){'
                                                               'ShaderInput *vector_in = input("Vector");'
                                                               'ShaderInput *socket1_in = input("Socket1");'
                                                               'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                                               'int vector_stack_offset = tex_mapping.compile_begin(compiler, vector_in);'
                                                               'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                                               'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                                               'compiler.add_node(NODE_TEX_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                                               'compiler.encode_uchar4(box2, __float_as_int(float1), vector_stack_offset, socket1_stack_offset), '
                                                               'socket2_stack_offset'
                                                               ');'
                                                               'compiler.add_node(__float_as_int(socket1));\n\n'
                                                               'tex_mapping.compile_end(compiler, vector_in, vector_stack_offset);'
                                                               '}\n\n'
                                                               'void NodeNameTextureNode::compile(OSLCompiler &compiler)'
                                                               '{'
                                                               'tex_mapping.compile(compiler);\n\n'
                                                               'compiler.parameter(this, "dropdown1");'
                                                               'compiler.parameter(this, "dropdown2");'
                                                               'compiler.parameter(this, "int1");'
                                                               'compiler.parameter(this, "box1");'
                                                               'compiler.parameter(this, "box2");'
                                                               'compiler.parameter(this, "float1");'
                                                               'compiler.add(this, "node_node_name_texture");'
                                                               '}\n\n'
                                    )

    def test_add_node_definition_with_dna_correct_formatting(self):
        with patch('builtins.open', mock_open(
                read_data=
                'DefNode(ShaderNode,     SH_NODE_TEX_WHITE_NOISE,    def_sh_tex_white_noise, "TEX_WHITE_NOISE",    TexWhiteNoise,    "White Noise",       ""       )\n'
                'DefNode(ShaderNode,     SH_NODE_OUTPUT_AOV,         def_sh_output_aov,      "OUTPUT_AOV",         OutputAOV,        "AOV Output",        ""       )\n'
                'DefNode(ShaderNode,     SH_NODE_TEX_TRUCHET,        def_sh_tex_truchet,     "TEX_TRUCHET",        TexTruchet,       "Truchet Texture",   ""       )\n'
                '\n'
                'DefNode(CompositorNode, CMP_NODE_VIEWER,         def_cmp_viewer,         "VIEWER",         Viewer,           "Viewer",            ""              )\n'
                'DefNode(CompositorNode, CMP_NODE_RGB,            0,                      "RGB",            RGB,              "RGB",               ""              )\n')) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_node_definition()

            self.assertTrue(mf.mock_calls[-3][1][0] ==
                            'DefNode(ShaderNode,     SH_NODE_TEX_WHITE_NOISE,    def_sh_tex_white_noise, "TEX_WHITE_NOISE",    TexWhiteNoise,    "White Noise",       ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_OUTPUT_AOV,         def_sh_output_aov,      "OUTPUT_AOV",         OutputAOV,        "AOV Output",        ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_TEX_TRUCHET,        def_sh_tex_truchet,     "TEX_TRUCHET",        TexTruchet,       "Truchet Texture",   ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_NODE_NAME,          def_sh_node_name,       "NODE_NAME",          NodeName,         "Node Name",         ""       )\n'
                            '\n'
                            'DefNode(CompositorNode, CMP_NODE_VIEWER,         def_cmp_viewer,         "VIEWER",         Viewer,           "Viewer",            ""              )\n'
                            'DefNode(CompositorNode, CMP_NODE_RGB,            0,                      "RGB",            RGB,              "RGB",               ""              )\n')

    def test_add_node_definition_no_props_correct_formatting(self):
        self.mock_gui.get_props.return_value = []
        self.mock_gui.node_has_properties.return_value = False
        with patch('builtins.open', mock_open(
                read_data=
                'DefNode(ShaderNode,     SH_NODE_TEX_WHITE_NOISE,    def_sh_tex_white_noise, "TEX_WHITE_NOISE",    TexWhiteNoise,    "White Noise",       ""       )\n'
                'DefNode(ShaderNode,     SH_NODE_OUTPUT_AOV,         def_sh_output_aov,      "OUTPUT_AOV",         OutputAOV,        "AOV Output",        ""       )\n'
                'DefNode(ShaderNode,     SH_NODE_TEX_TRUCHET,        def_sh_tex_truchet,     "TEX_TRUCHET",        TexTruchet,       "Truchet Texture",   ""       )\n'
                '\n'
                'DefNode(CompositorNode, CMP_NODE_VIEWER,         def_cmp_viewer,         "VIEWER",         Viewer,           "Viewer",            ""              )\n'
                'DefNode(CompositorNode, CMP_NODE_RGB,            0,                      "RGB",            RGB,              "RGB",               ""              )\n')) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_node_definition()
            self.assertTrue(mf.mock_calls[-3][1][0] ==
                            'DefNode(ShaderNode,     SH_NODE_TEX_WHITE_NOISE,    def_sh_tex_white_noise, "TEX_WHITE_NOISE",    TexWhiteNoise,    "White Noise",       ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_OUTPUT_AOV,         def_sh_output_aov,      "OUTPUT_AOV",         OutputAOV,        "AOV Output",        ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_TEX_TRUCHET,        def_sh_tex_truchet,     "TEX_TRUCHET",        TexTruchet,       "Truchet Texture",   ""       )\n'
                            'DefNode(ShaderNode,     SH_NODE_NODE_NAME,          0,                      "NODE_NAME",          NodeName,         "Node Name",         ""       )\n'
                            '\n'
                            'DefNode(CompositorNode, CMP_NODE_VIEWER,         def_cmp_viewer,         "VIEWER",         Viewer,           "Viewer",            ""              )\n'
                            'DefNode(CompositorNode, CMP_NODE_RGB,            0,                      "RGB",            RGB,              "RGB",               ""              )\n')


if __name__ == "__main__":
    unittest.main()
