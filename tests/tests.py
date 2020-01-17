from code_generation import CodeGenerator, CodeGeneratorUtil
import unittest
from unittest import mock
from unittest.mock import patch, mock_open, call


class TestUsesDna(unittest.TestCase):
    def test_no_props_false(self):
        self.assertFalse(CodeGeneratorUtil.uses_dna([], "Shader"))

    def test_no_props_texture_type_true(self):
        self.assertTrue(CodeGeneratorUtil.uses_dna([], "Texture"))

    def test_string_true(self):
        self.assertTrue(CodeGeneratorUtil.uses_dna([{"type": "String"}], "Texture"))

    def test_two_enums_one_bool_true(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Boolean"}]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_enums_false(self):
        props = [{"type": "Enum"}, {"type": "Enum"}]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_16_bools_false(self):
        props = [{"type": "Boolean"} for _ in range(16)]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_17_bools_true(self):
        props = [{"type": "Boolean"} for _ in range(17)]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_one_enum_16_bools_false(self):
        props = [{"type": "Boolean"} for _ in range(17)] + [{"type": "Enum"}]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_one_enum_int_false(self):
        props = [{"type": "Enum"}, {"type": "Int"}]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_one_enum_int_bool_true(self):
        props = [{"type": "Enum"}, {"type": "Int"}, {"type": "Boolean"}]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_int_false(self):
        props = [{"type": "Int"}, {"type": "Int"}]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_int_one_bool_false(self):
        props = [{"type": "Int"}, {"type": "Boolean"}]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_three_float_true(self):
        props = [{"type": "Float"} for _ in range(3)]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_float_false(self):
        props = [{"type": "Float"} for _ in range(2)]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_float_enum_false(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Float"}, {"type": "Float"}]
        self.assertFalse(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_two_float_enum_one_int_true(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Int"}, {"type": "Float"}, {"type": "Float"}]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_three_enum_true(self):
        props = [{"type": "Enum"} for _ in range(3)]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Shader"))

    def test_three_enum_texture_type_true(self):
        props = [{"type": "Enum"} for _ in range(3)]
        self.assertTrue(CodeGeneratorUtil.uses_dna(props, "Texture"))


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
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", "type": "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "int1", "type": "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", "type": "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        self.mock_gui.is_texture_node.return_value = False
        self.mock_gui.node_has_properties.return_value = True
        self.mock_gui.node_has_check_box.return_value = True
        self.mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data_type': "Float",
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.0"},
                                                       {'type': "Output", 'name': "socket2", 'data_type': "Float",
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.0"}]

    def test_write_osl_file_correct_formatting(self):
        """Test OSL function generation is correct for paramaters"""
        m = mock.Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name(string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'int int1 = 0,'
                              'float float1 = 0.0,'
                              'string string1 = "",'
                              'float socket1 = 0.0,'
                              'output float socket2 = 0.0){}')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_osl_shader()

                self.assertTrue(all(c in mf.mock_calls for c in calls))

    def test_write_osl_file_texture_correct_formatting(self):
        """Test OSL function generation is correct for texture node"""
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.is_texture_node.return_value = True

        m = mock.Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name_texture(int use_mapping = 0,'
                              'matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                              'string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'int int1 = 0,'
                              'float float1 = 0.0,'
                              'string string1 = "",'
                              'float socket1 = 0.0,'
                              'output float socket2 = 0.0){}')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_osl_shader()

                self.assertTrue(all(c in mf.mock_calls for c in calls))

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

    def test_write_to_node_menu_poll_correct_formatting(self):
        self.mock_gui.get_poll.return_value = 'cycles_shader_nodes_poll'
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

            self.assertTrue(
                '        NodeItem("ShaderNodeNodeName", poll=cycles_shader_nodes_poll)\n' in mf.mock_calls[4][1][0])

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

    def test_write_dna_struct_correct_formatting(self):
        self.mock_gui.get_node_type.return_value = "Texture"
        with patch('builtins.open', mock_open(read_data='typedef struct NodeTexWave {\n'
                                                        '  NodeTexBase base;\n'
                                                        '  int wave_type;\n'
                                                        '  int wave_profile;\n'
                                                        '} NodeTexWave;\n'
                                                        '\n'
                                                        'typedef struct NodeTexMagic {\n'
                                                        '  NodeTexBase base;\n'
                                                        '  int depth;\n'
                                                        '  char _pad[4];\n'
                                                        '} NodeTexMagic;\n'
                                                        '\n'
                                                        'typedef struct NodeShaderAttribute {\n'
                                                        '  char name[64];\n'
                                                        '} NodeShaderAttribute;\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_dna_node_type()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'typedef struct NodeTexWave {\n'
                                                           '  NodeTexBase base;\n'
                                                           '  int wave_type;\n'
                                                           '  int wave_profile;\n'
                                                           '} NodeTexWave;\n'
                                                           '\n'
                                                           'typedef struct NodeTexMagic {\n'
                                                           '  NodeTexBase base;\n'
                                                           '  int depth;\n'
                                                           '  char _pad[4];\n'
                                                           '} NodeTexMagic;\n'
                                                           '\n'
                                                           'typedef struct NodeTexNodeName {NodeTexBase base; int dropdown1, dropdown2, box1, box2, int1; float float1; char string1[64];} NodeTexNodeName;\n'
                                                           '\n'
                                                           'typedef struct NodeShaderAttribute {\n'
                                                           '  char name[64];\n'
                                                           '} NodeShaderAttribute;\n')

    def test_write_dna_struct_requires_padding_correct_formatting(self):
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "options": ["prop1", "prop2"], "default": '"prop1"'}]
        with patch('builtins.open', mock_open(read_data='typedef struct NodeTexWave {\n'
                                                        '  NodeTexBase base;\n'
                                                        '  int wave_type;\n'
                                                        '  int wave_profile;\n'
                                                        '} NodeTexWave;\n'
                                                        '\n'
                                                        'typedef struct NodeTexMagic {\n'
                                                        '  NodeTexBase base;\n'
                                                        '  int depth;\n'
                                                        '  char _pad[4];\n'
                                                        '} NodeTexMagic;\n'
                                                        '\n'
                                                        'typedef struct NodeShaderAttribute {\n'
                                                        '  char name[64];\n'
                                                        '} NodeShaderAttribute;\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_dna_node_type()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'typedef struct NodeTexWave {\n'
                                                           '  NodeTexBase base;\n'
                                                           '  int wave_type;\n'
                                                           '  int wave_profile;\n'
                                                           '} NodeTexWave;\n'
                                                           '\n'
                                                           'typedef struct NodeTexMagic {\n'
                                                           '  NodeTexBase base;\n'
                                                           '  int depth;\n'
                                                           '  char _pad[4];\n'
                                                           '} NodeTexMagic;\n'
                                                           '\n'
                                                           'typedef struct NodeTexNodeName {NodeTexBase base; int dropdown1; char _pad[4];} NodeTexNodeName;\n'
                                                           '\n'
                                                           'typedef struct NodeShaderAttribute {\n'
                                                           '  char name[64];\n'
                                                           '} NodeShaderAttribute;\n')

    def test_write_dna_struct_not_needed_no_call(self):
        self.mock_gui.get_props.return_value = []
        with patch('builtins.open', mock_open()) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_dna_node_type()

            self.assertTrue(len(mf.mock_calls) == 0)

    def test_write_drawnode_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data=
                                              'static void node_shader_buts_white_noise(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)\n'
                                              '{\n'
                                              '  uiItemR(layout, ptr, "noise_dimensions", 0, "", ICON_NONE);\n'
                                              '}\n'
                                              '\n'
                                              '/ * only once called * /\n'
                                              'static void node_shader_set_butfunc(bNodeType *ntype)\n'
                                              '{\n'
                                              '   switch (ntype->type) {\n'
                                              '       case SH_NODE_TEX_WHITE_NOISE:\n'
                                              '           ntype->draw_buttons = node_shader_buts_white_noise;\n'
                                              '           break;\n'
                                              '       case SH_NODE_TEX_TRUCHET:\n'
                                              '           ntype->draw_buttons = node_shader_buts_truchet;\n'
                                              '           break;\n'
                                              '   }\n'
                                              '}\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_node_drawing()

            self.assertTrue(
                'static void node_shader_buts_node_name(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)'
                '{uiItemR(layout, ptr, "dropdown1", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "dropdown2", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "box1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box2", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "int1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "float1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "string1", 0, IFACE_("String1"), ICON_NONE);'
                '}\n\n' in mf.mock_calls[-3][1][0]
                and 'case SH_NODE_NODE_NAME:\n' in mf.mock_calls[-3][1][0]
                and 'ntype->draw_buttons = node_shader_buts_node_name;\n' in mf.mock_calls[-3][1][0])

    def test_write_drawnode_texture_correct_formatting(self):
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.is_texture_node.return_value = True
        with patch('builtins.open', mock_open(read_data=
                                              'static void node_shader_buts_white_noise(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)\n'
                                              '{\n'
                                              '  uiItemR(layout, ptr, "noise_dimensions", 0, "", ICON_NONE);\n'
                                              '}\n'
                                              '\n'
                                              '/ * only once called * /\n'
                                              'static void node_shader_set_butfunc(bNodeType *ntype)\n'
                                              '{\n'
                                              '   switch (ntype->type) {\n'
                                              '       case SH_NODE_TEX_WHITE_NOISE:\n'
                                              '           ntype->draw_buttons = node_shader_buts_white_noise;\n'
                                              '           break;\n'
                                              '       case SH_NODE_TEX_TRUCHET:\n'
                                              '           ntype->draw_buttons = node_shader_buts_truchet;\n'
                                              '           break;\n'
                                              '   }\n'
                                              '}\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_node_drawing()

            self.assertTrue(
                'static void node_shader_buts_node_name(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)'
                '{uiItemR(layout, ptr, "dropdown1", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "dropdown2", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "box1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box2", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "int1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "float1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "string1", 0, IFACE_("String1"), ICON_NONE);'
                '}\n\n' in mf.mock_calls[-3][1][0]
                and 'case SH_NODE_TEX_NODE_NAME:\n' in mf.mock_calls[-3][1][0]
                and 'ntype->draw_buttons = node_shader_buts_tex_node_name;\n' in mf.mock_calls[-3][1][0])

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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'char string1[64];'
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'char string1[64];'
                                                           '};')

    def test_write_node_class_no_bools_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "options": ["prop1", "prop2"], "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "options": ["prop3", "prop4"], "default": '"prop3"'},
            {"name": "int1", "type": "Int", "default": 0, "min": -1, "max": 1},
            {"name": "float1", "type": "Float", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", "type": "String", "size": 64, "default": '""'}]
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'char string1[64];'
                                                           '};')

    def test_write_node_class_no_enums_correct_formatting(self):
        self.mock_gui.get_props.return_value = [{"name": "box1", "type": "Boolean", "default": 0},
                                                {"name": "box2", "type": "Boolean", "default": 1},
                                                {"name": "int1", "type": "Int", "default": 0, "min": -1, "max": 1},
                                                {"name": "float1", "type": "Float", "default": 0.0, "min": -1.0,
                                                 "max": 1.0},
                                                {"name": "string1", "type": "String", "size": 64, "default": '""'}]
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'float socket1, float1;'
                                                           'bool box1, box2;'
                                                           'int int1;'
                                                           'char string1[64];'
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           'int dropdown1, dropdown2, int1;'
                                                           'bool box1, box2;'
                                                           'float float1;'
                                                           'char string1[64];'
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
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
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting'):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_cycles_class()

                self.assertTrue(mf.mock_calls[-3][1][0] == 'class NodeNameNode : public ShaderNode {'
                                                           'public:SHADER_NODE_CLASS(NodeNameNode)'
                                                           'virtual int get_group(){return NODE_GROUP_LEVEL_3;}'
                                                           '};')

    def test_write_node_register_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data='void register_node_type_sh_tex_ies(void);\n'
                                                        'void register_node_type_sh_tex_white_noise(void);\n'
                                                        'void register_node_type_sh_tex_truchet(void);\n'
                                                        '\n'
                                                        'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
                                                        '\n'
                                                        '#endif\n'
                                                        '\n')) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_node_register()

            self.assertTrue(mf.mock_calls[-3][1][0] == 'void register_node_type_sh_node_name(void);\n')

    def test_write_texture_node_register_correct_formatting(self):
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.is_texture_node.return_value = True
        with patch('builtins.open', mock_open(read_data='void register_node_type_sh_tex_ies(void);\n'
                                                        'void register_node_type_sh_tex_white_noise(void);\n'
                                                        'void register_node_type_sh_tex_truchet(void);\n'
                                                        '\n'
                                                        'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
                                                        '\n'
                                                        '#endif\n'
                                                        '\n')) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_node_register()

            self.assertTrue(mf.mock_calls[-3][1][0] == 'void register_node_type_sh_tex_node_name(void);\n')

    def test_write_rna_properties_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_tex_correct_formatting(self):
        self.mock_gui.get_node_type.return_value = "Texture"
        self.mock_gui.is_texture_node.return_value = True
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_tex_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'RNA_def_struct_sdna_from(srna, "NodeTexNodeName", "storage");\n'
                                'def_sh_tex(srna);\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_tex_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_tex_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_enums_correct_formatting(self):
        self.mock_gui.get_props.return_value = [{"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
                                                {"name": "box2", "type": "Boolean", "sub-type": "PROP_NONE", "default": 1},
                                                {"name": "int1", "type": "Int", "sub-type": "PROP_NONE", "default": 0,
                                                 "min": -1, "max": 1},
                                                {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0,
                                                 "min": -1.0, "max": 1.0},
                                                {"name": "string1", "type": "String", "sub-type": "PROP_NONE", "size": 64,
                                                 "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_bools_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "int1", "type": "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", "type": "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_ints_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", "type": "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", "type": "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_string_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", "type": "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "int1", "type": "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "float1");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_floats_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", "type": "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "int1", "type": "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "string1", "type": "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "dropdown2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_props_no_call(self):
        self.mock_gui.get_props.return_value = []
        self.mock_gui.node_has_properties.return_value = False
        with patch('builtins.open', mock_open()) as mf:
            code_gen = CodeGenerator(self.mock_gui)
            code_gen._add_rna_properties()

            self.assertTrue(len(mf.mock_calls) == 0)

    def test_write_rna_properties_one_enum_bool_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "custom2", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_one_enum_bool_float_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "box1", "type": "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "custom2", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "custom3");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_two_enum_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'

                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_two_enum_float_correct_formatting(self):
        self.mock_gui.get_props.return_value = [
            {"name": "dropdown1", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": '"prop1"'},
            {"name": "dropdown2", "type": "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": '"prop3"'},
            {"name": "float1", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "float2", "type": "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.CodeGeneratorUtil.apply_clang_formatting', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "dropdown1", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom1");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown1_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "dropdown2", PROP_ENUM, PROP_NONE);'
                                'RNA_def_property_enum_sdna(prop, NULL, "custom2");'
                                'RNA_def_property_enum_items(prop, rna_enum_node_dropdown2_items);'
                                'RNA_def_property_ui_text(prop, "Dropdown2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float1", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "custom3");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "float2", PROP_FLOAT, PROP_NONE);'
                                'RNA_def_property_float_sdna(prop, NULL, "custom4");'
                                'RNA_def_property_range(prop, -1.0, 1.0);'
                                'RNA_def_property_ui_text(prop, "Float2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])


if __name__ == "__main__":
    unittest.main()
