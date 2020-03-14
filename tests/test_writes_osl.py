import unittest
from unittest.mock import Mock, patch, call, mock_open

from code_generation import WritesOSL


class TestWritesOsl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mock_gui = Mock()

    def _create_default_class(self, props=None, sockets=None, uses_texture_mapping=False, node_type='Shader'):
        self._mock_gui.get_source_path.return_value = 'C:/some/path'
        self._mock_gui.get_node_name.return_value = "Node Name"
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
        self._mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
                                                         'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                                                        {'type': "Output", 'name': "socket2", 'data-type': "Float",
                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
                                                         'min': "-1.0", 'max': "1.0",
                                                         }] if sockets is None else sockets
        self._mock_gui.uses_texture_mapping.return_value = uses_texture_mapping
        if node_type == 'Texture':
            suffix = 'texture'
        elif node_type == 'Bsdf':
            suffix = 'bsdf'
        else:
            suffix = ''
        self._mock_gui.type_suffix.return_value = suffix

        return WritesOSL(self._mock_gui)

    def test_write_osl_file_correct_formatting(self):
        """Test OSL function generation is correct for paramaters"""
        m = Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name(string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int int1 = 0,'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'float float1 = 0.0,'
                              'float Socket1 = 0.5,'
                              'output float Socket2 = 0.0){}\n')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class()
                code_gen.write_osl_shader()
                self.assertTrue(all(c in mf.mock_calls for c in calls))

    def test_write_osl_file_texture_no_vector_correct_formatting(self):
        """Test OSL function generation is correct for texture node"""
        m = Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name_texture('
                              'string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int int1 = 0,'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'float float1 = 0.0,'
                              'float Socket1 = 0.5,'
                              'output float Socket2 = 0.0){}\n')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Texture')
                code_gen.write_osl_shader()

                self.assertTrue(all(c in mf.mock_calls for c in calls))

    def test_write_osl_file_bsdf_correct_formatting(self):
        """Test OSL function generation is correct for texture node"""
        m = Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name_bsdf('
                              'string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int int1 = 0,'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'float float1 = 0.0,'
                              'float Socket1 = 0.5,'
                              'output float Socket2 = 0.0){}\n')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Bsdf')
                code_gen.write_osl_shader()

                self.assertTrue(all(c in mf.mock_calls for c in calls))

    def test_write_osl_file_texture_with_vector_correct_formatting(self):
        """Test OSL function generation is correct for texture node"""
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
                                                         'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Output", 'name': "socket2", 'data-type': "Float",
                                                         'sub-type': 'PROP_NONE', 'flag': 'None',
                                                         'min': "-1.0", 'max': "1.0",
                                                         }]
        sockets.insert(0, {'type': "Input", 'name': "vec1", 'data-type': "Vector",
                           'sub-type': 'PROP_NONE', 'flag': 'None',
                           'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0",
                           'default': "0.5,0.5,0.5"})

        m = Mock()
        calls = [call().write('#include "stdosl.h"\n\n'),
                 call().write('shader node_node_name_texture(int use_mapping = 0,'
                              'matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                              'string dropdown1 = "prop1",'
                              'string dropdown2 = "prop3",'
                              'int int1 = 0,'
                              'int box1 = 0,'
                              'int box2 = 1,'
                              'float float1 = 0.0,'
                              'point Vec1 = point(0.5, 0.5, 0.5),'
                              'float Socket1 = 0.5,'
                              'output float Socket2 = 0.0){}\n')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(sockets=sockets, node_type='Texture', uses_texture_mapping=True)
                code_gen.write_osl_shader()

                self.assertTrue(all(c in mf.mock_calls for c in calls))


if __name__ == '__main__':
    unittest.main()
