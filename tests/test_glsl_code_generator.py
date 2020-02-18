import unittest
from unittest import mock
from unittest.mock import patch

from code_generation.glsl_code_generator import GLSLCodeManager


class TestGLSLCodeGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_gui = mock.Mock()

    def _create_default_class(self, props=None, sockets=None, name='node name', node_type='Shader',
                              uses_texture_mapping=False):
        """Helper method to create class with some default parameters suitable for testing with"""
        self.mock_gui.get_node_name.return_value = "Node Name" if name is None else name
        self.mock_gui.get_node_type.return_value = "Shader" if node_type is None else node_type
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
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64,
             "default": '""'}] if props is None else props
        self.mock_gui.is_texture_node.return_value = node_type == 'Texture'
        self.mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                                                        'sub-type': 'PROP_NONE', 'flag': 'None',
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                                                       {'type': "Output", 'name': "socket2", 'data-type': "Float",
                                                        'sub-type': 'PROP_NONE', 'flag': 'None',
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
        self.mock_gui.uses_texture_mapping.return_value = uses_texture_mapping
        if node_type == 'Texture':
            suff = 'tex'
            suffix = 'texture'
        elif node_type == 'Bsdf':
            suff = 'bsdf'
            suffix = suff
        else:
            suff = ''
            suffix = suff

        self.mock_gui.type_suffix_abbreviated.return_value = suff
        self.mock_gui.type_suffix.return_value = suffix
        return GLSLCodeManager(self.mock_gui)

    def test_generate_func_names_0_dropdowns_correct_formatting(self):
        glsl = self._create_default_class(props=[])
        names = glsl._generate_shader_func_names()

        self.assertTrue(names == [''])

    def test_generate_func_names_1_dropdown_correct_formatting(self):
        glsl = self._create_default_class(props=[
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'}])
        names = glsl._generate_shader_func_names()

        self.assertTrue(names == ['"node_node_name_prop1"', '"node_node_name_prop2"'])

    def test_generate_func_names_2_dropdowns_correct_formatting(self):
        glsl = self._create_default_class()
        names = glsl._generate_shader_func_names()

        self.assertTrue(names == [['"node_node_name_prop1_prop3"', '"node_node_name_prop1_prop4"'],
                                  ['"node_node_name_prop2_prop3"', '"node_node_name_prop2_prop4"']])

    def test_additional_params_correct_formatting(self):
        glsl = self._create_default_class()
        params = glsl._generate_additional_params()

        self.assertTrue(params == ['GPU_constant(&int1)',
                                   'GPU_constant(&box1)',
                                   'GPU_constant(&box2)',
                                   'GPU_constant(&float1)'])

    def test_additional_params_no_props_correct_formatting(self):
        glsl = self._create_default_class(props=[])
        params = glsl._generate_additional_params()

        self.assertTrue(params == [])

    def test_generate_get_function_name_0_dropdowns_correct_formatting(self):
        glsl = self._create_default_class(props=[])
        names = glsl._generate_get_function_name()

        self.assertTrue(names == '"node_node_name"')

    def test_generate_get_function_name_1_dropdown_with_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        glsl = self._create_default_class(props=props)
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[attr->dropdown1]')

    def test_generate_get_function_name_1_dropdown_no_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'}]
        glsl = self._create_default_class(props=props)
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[node->custom1]')

    def test_generate_get_function_name_1_dropdown_with_dna_texture_node_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        glsl = self._create_default_class(props=props, node_type='Texture')
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[tex->dropdown1]')

    def test_generate_get_function_name_2_dropdowns_with_dna_correct_formatting(self):
        glsl = self._create_default_class()
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[attr->dropdown1][attr->dropdown2]')

    def test_generate_get_function_name_2_dropdowns_no_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": 'prop3'}]
        glsl = self._create_default_class(props=props)
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[node->custom1][node->custom2]')

    def test_generate_get_function_name_2_dropdowns_with_dna_texture_node_correct_formatting(self):
        glsl = self._create_default_class(node_type='Texture')
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[tex->dropdown1][tex->dropdown2]')

    def test_generate_get_function_name_2_dropdowns_with_dna_bsdf_node_correct_formatting(self):
        glsl = self._create_default_class(node_type='Bsdf')
        names = glsl._generate_get_function_name()

        self.assertTrue(names == 'names[attr->dropdown1][attr->dropdown2]')

    def test_generate_return_statement_correct_formatting(self):
        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = ['GPU_constant(&int1)',
                                               'GPU_constant(&box1)',
                                               'GPU_constant(&box2)',
                                               'GPU_constant(&float1)']

        func_name_mock = mock.Mock()
        func_name_mock.return_value = 'names[attr->dropdown1][attr->dropdown2]'
        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                   additional_params_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_get_function_name',
                       func_name_mock):
                glsl = self._create_default_class()
                statement = glsl._generate_return_statement()
                self.assertTrue(
                    statement == 'return GPU_stack_link(mat, node, names[attr->dropdown1][attr->dropdown2], in, out,'
                                 ' GPU_constant(&int1), '
                                 'GPU_constant(&box1), '
                                 'GPU_constant(&box2), '
                                 'GPU_constant(&float1));')

    def test_generate_names_array_0_dropdowns_correct_formatting(self):
        names_mock = mock.Mock()
        names_mock.return_value = []

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_shader_func_names', names_mock):
            glsl = self._create_default_class(props=[])
            arr = glsl._generate_names_array()
            self.assertTrue(arr == '')

    def test_generate_names_array_1_dropdown_correct_formatting(self):
        names_mock = mock.Mock()
        names_mock.return_value = ['"node_node_name_prop1"', '"node_node_name_prop2"']

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_shader_func_names', names_mock):
            props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
                      "options": [{"name": "prop1", "desc": "Short description"},
                                  {"name": "prop2", "desc": "Short description"}],
                      "default": 'prop1'}]
            glsl = self._create_default_class(props=props)
            arr = glsl._generate_names_array()

            self.assertTrue(arr == 'static const char *names[] = {'
                                   '"",'
                                   '"node_node_name_prop1",'
                                   '"node_node_name_prop2",'
                                   '};\n\n')

    def test_generate_names_array_2_dropdowns_correct_formatting(self):
        names_mock = mock.Mock()
        names_mock.return_value = [['"node_node_name_prop1_prop3"', '"node_node_name_prop1_prop4"'],
                                   ['"node_node_name_prop2_prop3"', '"node_node_name_prop2_prop4"']]

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_shader_func_names', names_mock):
            glsl = self._create_default_class()
            arr = glsl._generate_names_array()
            self.assertTrue(arr == 'static const char *names[][2] = {'
                                   '[SHD_NODE_NAME_PROP1] = {'
                                   '"",'
                                   '"node_node_name_prop1_prop3",'
                                   '"node_node_name_prop1_prop4",'
                                   '},'
                                   '[SHD_NODE_NAME_PROP2] = {'
                                   '"",'
                                   '"node_node_name_prop2_prop3",'
                                   '"node_node_name_prop2_prop4",'
                                   '},'
                                   '};\n\n')

    def test_generate_assertions_0_dropdowns_correct_formatting(self):
        glsl = self._create_default_class(props=[])
        a = glsl._generate_assertions()

        self.assertTrue(a == '')

    def test_generate_assertions_1_dropdown_with_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        glsl = self._create_default_class(props=props)
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                             '\n\n')

    def test_generate_assertions_1_dropdown_with_dna_texture_node_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0}]
        glsl = self._create_default_class(props=props, node_type='Texture')
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);'
                             '\n\n')

    def test_generate_assertions_1_dropdown_no_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'}]
        glsl = self._create_default_class(props=props)
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(node->custom1 >= 0 && node->custom1 < 3);'
                             '\n\n')

    def test_generate_assertions_2_dropdowns_with_dna_correct_formatting(self):
        glsl = self._create_default_class()
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                             'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n')

    def test_generate_assertions_2_dropdowns_with_dna_texture_node_correct_formatting(self):
        glsl = self._create_default_class(node_type='Texture')
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);'
                             'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n')

    def test_generate_assertions_2_dropdowns_no_dna_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop3", "desc": "Short description"},
                         {"name": "prop4", "desc": "Short description"}],
             "default": 'prop3'}]
        glsl = self._create_default_class(props=props)
        a = glsl._generate_assertions()

        self.assertTrue(a == 'BLI_assert(node->custom1 >= 0 && node->custom1 < 3);'
                             'BLI_assert(node->custom2 >= 0 && node->custom2 < 3);\n\n')

    def test_generate_retrieve_props_correct_formatting(self):
        assertions_mock = mock.Mock()
        assertions_mock.return_value = 'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);' \
                                       'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'
        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_assertions', assertions_mock):
            glsl = self._create_default_class()
            props = glsl._generate_retrieve_props()

            self.assertTrue(props == 'NodeNodeName *attr = (NodeNodeName *)node->storage;'
                                     'float int1 = attr->int1;'
                                     'float box1 = (attr->box1) ? 1.0f : 0.0f;'
                                     'float box2 = (attr->box2) ? 1.0f : 0.0f;'
                                     'float float1 = attr->float1;\n\n'
                                     'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                                     'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n')

    def test_generate_retrieve_props_texture_node_correct_formatting(self):
        assertions_mock = mock.Mock()
        assertions_mock.return_value = 'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);' \
                                       'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n'
        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_assertions', assertions_mock):
            glsl = self._create_default_class(node_type='Texture')
            props = glsl._generate_retrieve_props()

            self.assertTrue(props == 'NodeTexNodeName *tex = (NodeTexNodeName *)node->storage;'
                                     'float int1 = tex->int1;'
                                     'float box1 = (tex->box1) ? 1.0f : 0.0f;'
                                     'float box2 = (tex->box2) ? 1.0f : 0.0f;'
                                     'float float1 = tex->float1;\n\n'
                                     'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);'
                                     'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n')

    def test_generate_retrieve_props_bsdf_node_correct_formatting(self):
        assertions_mock = mock.Mock()
        assertions_mock.return_value = 'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);' \
                                       'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'
        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_assertions', assertions_mock):
            glsl = self._create_default_class(node_type='Bsdf')
            props = glsl._generate_retrieve_props()

            self.assertTrue(props == 'NodeBsdfNodeName *attr = (NodeBsdfNodeName *)node->storage;'
                                     'float int1 = attr->int1;'
                                     'float box1 = (attr->box1) ? 1.0f : 0.0f;'
                                     'float box2 = (attr->box2) ? 1.0f : 0.0f;'
                                     'float float1 = attr->float1;\n\n'
                                     'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                                     'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n')

    def test_generate_retrieve_props_no_props_correct_formatting(self):
        assertions_mock = mock.Mock()
        assertions_mock.return_value = ''
        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_assertions', assertions_mock):
            glsl = self._create_default_class(props=[])
            props = glsl._generate_retrieve_props()
            self.assertTrue(props == '')

    def test_generate_gpu_function_correct_formatting(self):
        names_array_mock = mock.Mock()
        names_array_mock.return_value = 'static const char *names[][2] = {' \
                                        '[SHD_NODE_NAME_PROP1] = {' \
                                        '"",' \
                                        '"node_node_name_prop1_prop3",' \
                                        '"node_node_name_prop1_prop4",' \
                                        '},' \
                                        '[SHD_NODE_NAME_PROP2] = {' \
                                        '"",' \
                                        '"node_node_name_prop2_prop3",' \
                                        '"node_node_name_prop2_prop4",' \
                                        '},' \
                                        '};\n\n'

        retrieve_props_mock = mock.Mock()
        retrieve_props_mock.return_value = 'NodeNodeName *attr = (NodeNodeName *)node->storage;' \
                                           'float int1 = attr->int1;' \
                                           'float box1 = (attr->box1) ? 1.0f : 0.0f;' \
                                           'float box2 = (attr->box2) ? 1.0f : 0.0f;' \
                                           'float float1 = attr->float1;\n\n' \
                                           'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);' \
                                           'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'

        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = ['GPU_constant(&int1)',
                                               'GPU_constant(&box1)',
                                               'GPU_constant(&box2)',
                                               'GPU_constant(&float1)']

        return_statement_mock = mock.Mock()
        return_statement_mock.return_value = 'return GPU_stack_link(mat, node, ' \
                                             'names[attr->dropdown1][attr->dropdown2], in, out,' \
                                             ' GPU_constant(&int1), ' \
                                             'GPU_constant(&box1), ' \
                                             'GPU_constant(&box2), ' \
                                             'GPU_constant(&float1));'

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_names_array', names_array_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_retrieve_props',
                       retrieve_props_mock):
                with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                           additional_params_mock):
                    with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_return_statement',
                               return_statement_mock):
                        glsl = self._create_default_class()
                        func = glsl.generate_gpu_func()

                        self.assertTrue(func == 'static int gpu_shader_node_name(GPUMaterial *mat, '
                                                'bNode *node, '
                                                'bNodeExecData *UNUSED(execdata), '
                                                'GPUNodeStack *in, '
                                                'GPUNodeStack *out)'
                                                '{'
                                                'static const char *names[][2] = {'
                                                '[SHD_NODE_NAME_PROP1] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop1_prop3",'
                                                '"node_node_name_prop1_prop4",'
                                                '},'
                                                '[SHD_NODE_NAME_PROP2] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop2_prop3",'
                                                '"node_node_name_prop2_prop4",'
                                                '},'
                                                '};\n\n'
                                                'NodeNodeName *attr = (NodeNodeName *)node->storage;'
                                                'float int1 = attr->int1;'
                                                'float box1 = (attr->box1) ? 1.0f : 0.0f;'
                                                'float box2 = (attr->box2) ? 1.0f : 0.0f;'
                                                'float float1 = attr->float1;\n\n'
                                                'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                                                'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'
                                                'return GPU_stack_link(mat, node, '
                                                'names[attr->dropdown1][attr->dropdown2], '
                                                'in, out, GPU_constant(&int1), GPU_constant(&box1), '
                                                'GPU_constant(&box2), GPU_constant(&float1));'
                                                '};\n\n'
                                        )

    def test_generate_gpu_function_texture_node_with_mapping_correct_formatting(self):
        names_array_mock = mock.Mock()
        names_array_mock.return_value = 'static const char *names[][2] = {' \
                                        '[SHD_NODE_NAME_PROP1] = {' \
                                        '"",' \
                                        '"node_node_name_prop1_prop3",' \
                                        '"node_node_name_prop1_prop4",' \
                                        '},' \
                                        '[SHD_NODE_NAME_PROP2] = {' \
                                        '"",' \
                                        '"node_node_name_prop2_prop3",' \
                                        '"node_node_name_prop2_prop4",' \
                                        '},' \
                                        '};\n\n'

        retrieve_props_mock = mock.Mock()
        retrieve_props_mock.return_value = 'NodeTexNodeName *tex = (NodeTexNodeName *)node->storage;' \
                                           'float int1 = tex->int1;' \
                                           'float box1 = (tex->box1) ? 1.0f : 0.0f;' \
                                           'float box2 = (tex->box2) ? 1.0f : 0.0f;' \
                                           'float float1 = tex->float1;\n\n' \
                                           'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);' \
                                           'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n'

        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = ['GPU_constant(&int1)',
                                               'GPU_constant(&box1)',
                                               'GPU_constant(&box2)',
                                               'GPU_constant(&float1)']

        return_statement_mock = mock.Mock()
        return_statement_mock.return_value = 'return GPU_stack_link(mat, node, ' \
                                             'names[tex->dropdown1][tex->dropdown2], in, out,' \
                                             ' GPU_constant(&int1), ' \
                                             'GPU_constant(&box1), ' \
                                             'GPU_constant(&box2), ' \
                                             'GPU_constant(&float1));'

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_names_array', names_array_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_retrieve_props',
                       retrieve_props_mock):
                with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                           additional_params_mock):
                    with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_return_statement',
                               return_statement_mock):
                        glsl = self._create_default_class(node_type='Texture', uses_texture_mapping=True)
                        func = glsl.generate_gpu_func()

                        self.assertTrue(func == 'static int gpu_shader_tex_node_name(GPUMaterial *mat, '
                                                'bNode *node, '
                                                'bNodeExecData *UNUSED(execdata), '
                                                'GPUNodeStack *in, '
                                                'GPUNodeStack *out)'
                                                '{'
                                                'node_shader_gpu_default_tex_coord(mat, node, &in[0].link);'
                                                'node_shader_gpu_tex_mapping(mat, node, in, out);\n\n'
                                                'static const char *names[][2] = {'
                                                '[SHD_NODE_NAME_PROP1] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop1_prop3",'
                                                '"node_node_name_prop1_prop4",'
                                                '},'
                                                '[SHD_NODE_NAME_PROP2] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop2_prop3",'
                                                '"node_node_name_prop2_prop4",'
                                                '},'
                                                '};\n\n'
                                                'NodeTexNodeName *tex = (NodeTexNodeName *)node->storage;'
                                                'float int1 = tex->int1;'
                                                'float box1 = (tex->box1) ? 1.0f : 0.0f;'
                                                'float box2 = (tex->box2) ? 1.0f : 0.0f;'
                                                'float float1 = tex->float1;\n\n'
                                                'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);'
                                                'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n'
                                                'return GPU_stack_link(mat, node, '
                                                'names[tex->dropdown1][tex->dropdown2], '
                                                'in, out, GPU_constant(&int1), GPU_constant(&box1), '
                                                'GPU_constant(&box2), GPU_constant(&float1));'
                                                '};\n\n'
                                        )

    def test_generate_gpu_function_bsdf_node_correct_formatting(self):
        names_array_mock = mock.Mock()
        names_array_mock.return_value = 'static const char *names[][2] = {' \
                                        '[SHD_NODE_NAME_PROP1] = {' \
                                        '"",' \
                                        '"node_node_name_prop1_prop3",' \
                                        '"node_node_name_prop1_prop4",' \
                                        '},' \
                                        '[SHD_NODE_NAME_PROP2] = {' \
                                        '"",' \
                                        '"node_node_name_prop2_prop3",' \
                                        '"node_node_name_prop2_prop4",' \
                                        '},' \
                                        '};\n\n'

        retrieve_props_mock = mock.Mock()
        retrieve_props_mock.return_value = 'NodeBsdfNodeName *attr = (NodeBsdfNodeName *)node->storage;' \
                                           'float int1 = attr->int1;' \
                                           'float box1 = (attr->box1) ? 1.0f : 0.0f;' \
                                           'float box2 = (attr->box2) ? 1.0f : 0.0f;' \
                                           'float float1 = attr->float1;\n\n' \
                                           'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);' \
                                           'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'

        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = ['GPU_constant(&int1)',
                                               'GPU_constant(&box1)',
                                               'GPU_constant(&box2)',
                                               'GPU_constant(&float1)']

        return_statement_mock = mock.Mock()
        return_statement_mock.return_value = 'return GPU_stack_link(mat, node, ' \
                                             'names[attr->dropdown1][attr->dropdown2], in, out,' \
                                             ' GPU_constant(&int1), ' \
                                             'GPU_constant(&box1), ' \
                                             'GPU_constant(&box2), ' \
                                             'GPU_constant(&float1));'

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_names_array', names_array_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_retrieve_props',
                       retrieve_props_mock):
                with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                           additional_params_mock):
                    with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_return_statement',
                               return_statement_mock):
                        glsl = self._create_default_class(node_type='Bsdf')
                        func = glsl.generate_gpu_func()

                        self.assertTrue(func == 'static int gpu_shader_bsdf_node_name(GPUMaterial *mat, '
                                                'bNode *node, '
                                                'bNodeExecData *UNUSED(execdata), '
                                                'GPUNodeStack *in, '
                                                'GPUNodeStack *out)'
                                                '{'
                                                'static const char *names[][2] = {'
                                                '[SHD_NODE_NAME_PROP1] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop1_prop3",'
                                                '"node_node_name_prop1_prop4",'
                                                '},'
                                                '[SHD_NODE_NAME_PROP2] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop2_prop3",'
                                                '"node_node_name_prop2_prop4",'
                                                '},'
                                                '};\n\n'
                                                'NodeBsdfNodeName *attr = (NodeBsdfNodeName *)node->storage;'
                                                'float int1 = attr->int1;'
                                                'float box1 = (attr->box1) ? 1.0f : 0.0f;'
                                                'float box2 = (attr->box2) ? 1.0f : 0.0f;'
                                                'float float1 = attr->float1;\n\n'
                                                'BLI_assert(attr->dropdown1 >= 0 && attr->dropdown1 < 3);'
                                                'BLI_assert(attr->dropdown2 >= 0 && attr->dropdown2 < 3);\n\n'
                                                'return GPU_stack_link(mat, node, '
                                                'names[attr->dropdown1][attr->dropdown2], '
                                                'in, out, GPU_constant(&int1), GPU_constant(&box1), '
                                                'GPU_constant(&box2), GPU_constant(&float1));'
                                                '};\n\n'
                                        )

    def test_generate_gpu_function_texture_node_no_mapping_correct_formatting(self):
        names_array_mock = mock.Mock()
        names_array_mock.return_value = 'static const char *names[][2] = {' \
                                        '[SHD_NODE_NAME_PROP1] = {' \
                                        '"",' \
                                        '"node_node_name_prop1_prop3",' \
                                        '"node_node_name_prop1_prop4",' \
                                        '},' \
                                        '[SHD_NODE_NAME_PROP2] = {' \
                                        '"",' \
                                        '"node_node_name_prop2_prop3",' \
                                        '"node_node_name_prop2_prop4",' \
                                        '},' \
                                        '};\n\n'

        retrieve_props_mock = mock.Mock()
        retrieve_props_mock.return_value = 'NodeTexNodeName *tex = (NodeTexNodeName *)node->storage;' \
                                           'float int1 = tex->int1;' \
                                           'float box1 = (tex->box1) ? 1.0f : 0.0f;' \
                                           'float box2 = (tex->box2) ? 1.0f : 0.0f;' \
                                           'float float1 = tex->float1;\n\n' \
                                           'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);' \
                                           'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n'

        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = ['GPU_constant(&int1)',
                                               'GPU_constant(&box1)',
                                               'GPU_constant(&box2)',
                                               'GPU_constant(&float1)']

        return_statement_mock = mock.Mock()
        return_statement_mock.return_value = 'return GPU_stack_link(mat, node, ' \
                                             'names[tex->dropdown1][tex->dropdown2], in, out,' \
                                             ' GPU_constant(&int1), ' \
                                             'GPU_constant(&box1), ' \
                                             'GPU_constant(&box2), ' \
                                             'GPU_constant(&float1));'

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_names_array', names_array_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_retrieve_props',
                       retrieve_props_mock):
                with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                           additional_params_mock):
                    with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_return_statement',
                               return_statement_mock):
                        glsl = self._create_default_class(node_type='Texture')
                        func = glsl.generate_gpu_func()

                        self.assertTrue(func == 'static int gpu_shader_tex_node_name(GPUMaterial *mat, '
                                                'bNode *node, '
                                                'bNodeExecData *UNUSED(execdata), '
                                                'GPUNodeStack *in, '
                                                'GPUNodeStack *out)'
                                                '{'
                                                'static const char *names[][2] = {'
                                                '[SHD_NODE_NAME_PROP1] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop1_prop3",'
                                                '"node_node_name_prop1_prop4",'
                                                '},'
                                                '[SHD_NODE_NAME_PROP2] = '
                                                '{'
                                                '"",'
                                                '"node_node_name_prop2_prop3",'
                                                '"node_node_name_prop2_prop4",'
                                                '},'
                                                '};\n\n'
                                                'NodeTexNodeName *tex = (NodeTexNodeName *)node->storage;'
                                                'float int1 = tex->int1;'
                                                'float box1 = (tex->box1) ? 1.0f : 0.0f;'
                                                'float box2 = (tex->box2) ? 1.0f : 0.0f;'
                                                'float float1 = tex->float1;\n\n'
                                                'BLI_assert(tex->dropdown1 >= 0 && tex->dropdown1 < 3);'
                                                'BLI_assert(tex->dropdown2 >= 0 && tex->dropdown2 < 3);\n\n'
                                                'return GPU_stack_link(mat, node, '
                                                'names[tex->dropdown1][tex->dropdown2], '
                                                'in, out, GPU_constant(&int1), GPU_constant(&box1), '
                                                'GPU_constant(&box2), GPU_constant(&float1));'
                                                '};\n\n'
                                        )

    def test_generate_gpu_function_no_props_correct_formatting(self):
        names_array_mock = mock.Mock()
        names_array_mock.return_value = ''

        retrieve_props_mock = mock.Mock()
        retrieve_props_mock.return_value = ''

        additional_params_mock = mock.Mock()
        additional_params_mock.return_value = []

        return_statement_mock = mock.Mock()
        return_statement_mock.return_value = 'return GPU_stack_link(mat, node, ' \
                                             '"node_node_name", in, out);'

        with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_names_array', names_array_mock):
            with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_retrieve_props',
                       retrieve_props_mock):
                with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_additional_params',
                           additional_params_mock):
                    with patch('code_generation.glsl_code_generator.GLSLCodeManager._generate_return_statement',
                               return_statement_mock):
                        glsl = self._create_default_class(props=[])
                        func = glsl.generate_gpu_func()

                        self.assertTrue(func == 'static int gpu_shader_node_name(GPUMaterial *mat, '
                                                'bNode *node, '
                                                'bNodeExecData *UNUSED(execdata), '
                                                'GPUNodeStack *in, '
                                                'GPUNodeStack *out)'
                                                '{'
                                                'return GPU_stack_link(mat, node, '
                                                '"node_node_name", '
                                                'in, out);'
                                                '};\n\n'
                                        )

    def test_generate_glsl_correct_formatting(self):
        glsl = self._create_default_class()
        shader = glsl._generate_glsl_shader()

        self.assertTrue(shader == 'void node_node_name_prop1_prop3('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop1_prop4('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop2_prop3('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop2_prop4('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                        )

    def test_generate_glsl_0_dropdowns_correct_formatting(self):
        props = [
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        glsl = self._create_default_class(props=props)
        shader = glsl._generate_glsl_shader()

        self.assertTrue(shader == 'void node_node_name('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                        )

    def test_generate_glsl_1_dropdown_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE",
             "options": [{"name": "prop1", "desc": "Short description"},
                         {"name": "prop2", "desc": "Short description"}],
             "default": 'prop1'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        glsl = self._create_default_class(props=props)
        shader = glsl._generate_glsl_shader()

        self.assertTrue(shader == 'void node_node_name_prop1('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop2('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                        )

    def test_generate_glsl_2_dropdowns_correct_formatting(self):
        glsl = self._create_default_class()
        shader = glsl._generate_glsl_shader()

        self.assertTrue(shader == 'void node_node_name_prop1_prop3('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop1_prop4('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop2_prop3('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                                  '\n\n'
                                  'void node_node_name_prop2_prop4('
                                  'float int1,'
                                  'float box1,'
                                  'float box2,'
                                  'float float1,'
                                  'float socket1,'
                                  'out float socket2){}'
                        )


if __name__ == '__main__':
    unittest.main()
