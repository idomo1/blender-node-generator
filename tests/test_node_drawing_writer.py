import unittest
from unittest.mock import Mock, patch, mock_open

from code_generation import NodeDrawingWriter
from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp
from node_types.prop_int import IntProp


class TestNodeDrawingWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mock_gui = Mock()

    def _create_default_class(self, props=None, node_type='Shader'):
        self._mock_gui.get_node_name.return_value = 'node name'
        self._mock_gui.get_source_path.return_value = 'C:/some/path'
        self._mock_gui.get_node_type.return_value = node_type
        self._mock_gui.get_props.return_value = [
            {"name": "dropdown1", 'data-type': EnumProp(), "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "dropdown2", 'data-type': EnumProp(), "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": 'prop3'},
            {"name": "int1", 'data-type': IntProp(), "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': BoolProp(), "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': BoolProp(), "sub-type": "PROP_NONE", "default": 1}] if props is None else props
        if node_type == 'Texture':
            suffix = 'tex'
        elif node_type == 'Bsdf':
            suffix = 'bsdf'
        else:
            suffix = ''
        self._mock_gui.type_suffix_abbreviated.return_value = suffix
        return NodeDrawingWriter(self._mock_gui)

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
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class()
                code_gen.write_node_drawing()

            self.assertTrue(
                'static void node_shader_buts_node_name(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)'
                '{uiItemR(layout, ptr, "dropdown1", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "dropdown2", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "int1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box2", 0, NULL, ICON_NONE);'
                '}\n\n' in mf.mock_calls[-3][1][0]
                and 'case SH_NODE_NODE_NAME:\n' in mf.mock_calls[-3][1][0]
                and 'ntype->draw_buttons = node_shader_buts_node_name;\n' in mf.mock_calls[-3][1][0])

    def test_write_drawnode_texture_correct_formatting(self):
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
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Texture')
                code_gen.write_node_drawing()

            self.assertTrue(
                'static void node_shader_buts_tex_node_name(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)'
                '{uiItemR(layout, ptr, "dropdown1", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "dropdown2", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "int1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box2", 0, NULL, ICON_NONE);'
                '}\n\n' in mf.mock_calls[-3][1][0]
                and 'case SH_NODE_TEX_NODE_NAME:\n' in mf.mock_calls[-3][1][0]
                and 'ntype->draw_buttons = node_shader_buts_tex_node_name;\n' in mf.mock_calls[-3][1][0])

    def test_write_drawnode_bsdf_correct_formatting(self):
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
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Bsdf')
                code_gen.write_node_drawing()

            self.assertTrue(
                'static void node_shader_buts_bsdf_node_name(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)'
                '{uiItemR(layout, ptr, "dropdown1", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "dropdown2", 0, "", ICON_NONE);'
                'uiItemR(layout, ptr, "int1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box1", 0, NULL, ICON_NONE);'
                'uiItemR(layout, ptr, "box2", 0, NULL, ICON_NONE);'
                '}\n\n' in mf.mock_calls[-3][1][0]
                and 'case SH_NODE_BSDF_NODE_NAME:\n' in mf.mock_calls[-3][1][0]
                and 'ntype->draw_buttons = node_shader_buts_bsdf_node_name;\n' in mf.mock_calls[-3][1][0])


if __name__ == '__main__':
    unittest.main()
