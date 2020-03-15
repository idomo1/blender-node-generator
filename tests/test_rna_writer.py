import unittest
from unittest.mock import Mock, patch, mock_open

from code_generation.rna_writer import RNAWriter


class TestRNAWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mock_gui = Mock()

    def _create_default_class(self, props=None, node_type='Shader'):
        self._mock_gui.get_node_type.return_value = node_type
        self._mock_gui.get_source_path.return_value = "C:/some_path"
        self._mock_gui.get_node_name.return_value = "node name"
        self._mock_gui.get_props.return_value = [
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
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64,
             "default": '""'}] if props is None else props
        self._mock_gui.node_has_properties.return_value = props is None or (props is not None and len(props)) > 0
        if node_type == 'Texture':
            suff = 'tex'
            suffix = 'texture'
        elif node_type == 'Bsdf':
            suff = 'bsdf'
            suffix = suff
        else:
            suff = ''
            suffix = suff
        self._mock_gui.type_suffix_abbreviated.return_value = suff
        self._mock_gui.type_suffix.return_value = suffix
        return RNAWriter(self._mock_gui)

    def test_write_rna_properties_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data=
                                              '#ifndef RNA_RUNTIME\n'
                                              'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                              '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                              '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                              '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                              '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                              '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                              '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                              '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                              '  {0, NULL, 0, NULL, NULL},\n'
                                              '};\n\n'
                                              '#endif\n'
                                              'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                              '#  endif\n'
                                              '}\n'
                                              '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                              '\n'
                                              'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                              '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class()
                code_gen.write_rna_properties()
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
                                '}\n\n' in mf.mock_calls[-3][1][0]
                                and 'static const EnumPropertyItem rna_enum_node_dropdown1_items[] = {'
                                    '{1, "PROP1", 0, "Prop1", "Short description"},'
                                    '{2, "PROP2", 0, "Prop2", "Short description"},'
                                    '{0, NULL, 0, NULL, NULL},'
                                    '};\n\n' in mf.mock_calls[-3][1][0]
                                and 'static const EnumPropertyItem rna_enum_node_dropdown2_items[] = {'
                                    '{1, "PROP3", 0, "Prop3", "Short description"},'
                                    '{2, "PROP4", 0, "Prop4", "Short description"},'
                                    '{0, NULL, 0, NULL, NULL},'
                                    '};\n\n' in mf.mock_calls[-3][1][0]
                                )

    def test_write_rna_properties_tex_correct_formatting(self):
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Texture')
                code_gen.write_rna_properties()

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

                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
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

    def test_write_rna_properties_no_enums_correct_formatting(self):
        props = [
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0,
             "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64,
             "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

                self.assertTrue('static void def_sh_node_name(StructRNA *srna)\n'
                                '{\n'
                                'PropertyRNA *prop;\n\n'
                                'prop = RNA_def_property(srna, "int1", PROP_INT, PROP_NONE);'
                                'RNA_def_property_int_sdna(prop, NULL, "int1");'
                                'RNA_def_property_range(prop, -1, 1);'
                                'RNA_def_property_ui_text(prop, "Int1", "");'
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

    def test_write_rna_properties_no_bools_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_floats_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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

                                'prop = RNA_def_property(srna, "box1", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box1", SHD_NODE_NAME_BOX1);'
                                'RNA_def_property_ui_text(prop, "Box1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "box2", PROP_BOOLEAN, PROP_NONE);'
                                'RNA_def_property_boolean_sdna(prop, NULL, "box2", SHD_NODE_NAME_BOX2);'
                                'RNA_def_property_ui_text(prop, "Box2", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n\n'

                                'prop = RNA_def_property(srna, "string1", PROP_STRING, PROP_NONE);'
                                'RNA_def_property_string_sdna(prop, NULL, "string1");'
                                'RNA_def_property_ui_text(prop, "String1", "");'
                                'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");\n'
                                '}\n\n' in mf.mock_calls[-3][1][0])

    def test_write_rna_properties_no_props_no_call(self):
        with patch('builtins.open', mock_open()) as mf:
            code_gen = self._create_default_class(props=[])
            code_gen.write_rna_properties()

            self.assertTrue(len(mf.mock_calls) == 0)

    def test_write_rna_properties_one_enum_bool_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": '"prop3"'},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "float2", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
        with patch('builtins.open', mock_open(read_data='#ifndef RNA_RUNTIME\n'
                                                        'const EnumPropertyItem rna_enum_node_filter_items[] = {'
                                                        '  {0, "SOFTEN", 0, "Soften", ""},\n'
                                                        '  {1, "SHARPEN", 0, "Sharpen", ""},\n'
                                                        '  {2, "LAPLACE", 0, "Laplace", ""},\n'
                                                        '  {3, "SOBEL", 0, "Sobel", ""},\n'
                                                        '  {4, "PREWITT", 0, "Prewitt", ""},\n'
                                                        '  {5, "KIRSCH", 0, "Kirsch", ""},\n'
                                                        '  {6, "SHADOW", 0, "Shadow", ""},\n'
                                                        '  {0, NULL, 0, NULL, NULL},\n'
                                                        '};\n\n'
                                                        '#endif\n'
                                                        'static const EnumPropertyItem node_sampler_type_items[] = {\n'
                                                        '#  endif\n'
                                                        '}\n'
                                                        '/* -- Compositor Nodes ------------------------------------------------------ */\n'
                                                        '\n'
                                                        'static void def_cmp_alpha_over(StructRNA *srna)\n'
                                                        '{\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_rna_properties()

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

    def test_generate_enum_definitions_correct_formatting(self):
        prop = {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
                "options": [{"name": "prop1", "desc": "Short description"},
                            {"name": "prop2", "desc": "Short description"}],
                "default": 'prop1'}
        code_gen = self._create_default_class()
        enum = code_gen._generate_enum_prop_item(prop)

        self.assertTrue(enum == 'static const EnumPropertyItem rna_enum_node_dropdown1_items[] = {'
                                '{1, "PROP1", 0, "Prop1", "Short description"},'
                                '{2, "PROP2", 0, "Prop2", "Short description"},'
                                '{0, NULL, 0, NULL, NULL},'
                                '};\n\n')

    def test_generate_enum_definitions_texture_node_correct_formatting(self):
        prop = {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
                "options": [{"name": "prop1", "desc": "Short description"},
                            {"name": "prop2", "desc": "Short description"}],
                "default": 'prop1'}
        code_gen = self._create_default_class(node_type='Texture')
        enum = code_gen._generate_enum_prop_item(prop)

        self.assertTrue(enum == 'static const EnumPropertyItem rna_enum_node_tex_dropdown1_items[] = {'
                                '{1, "PROP1", 0, "Prop1", "Short description"},'
                                '{2, "PROP2", 0, "Prop2", "Short description"},'
                                '{0, NULL, 0, NULL, NULL},'
                                '};\n\n')


if __name__ == '__main__':
    unittest.main()
