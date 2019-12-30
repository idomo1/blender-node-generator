from code_generation import CodeGenerator, CodeGeneratorUtil
import unittest
from unittest import mock
from unittest.mock import patch, mock_open, call


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
        self.mock_gui.get_source_path.return_value = "C:/some/path"
        self.mock_gui.get_node_dropdown1_properties.return_value = ["prop1", "prop2"]
        self.mock_gui.get_node_dropdown2_properties.return_value = ["prop2", "prop3"]
        self.mock_gui.get_node_dropdown_property1_name.return_value = "dropdown1"
        self.mock_gui.get_node_dropdown_property2_name.return_value = "dropdown2"
        self.mock_gui.get_node_check_boxes.return_value = [{"name": "box1", "default": False}, {"name": "box2", "default": True}]
        self.mock_gui.get_node_sockets.return_value = [{'type': "Input", 'name': "socket1", 'data_type': "float",
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.0"},
                                                       {'type': "Output", 'name': "socket2", 'data_type': "float",
                                                        'min': "-1.0", 'max': "1.0", 'default': "0.0"}]

    def test_write_osl_file_correct_formatting(self):
        """Test OSL function generation is correct for paramaters"""
        m = mock.MagicMock()
        calls = [call().writelines(['#include "stdosl.h"', '']),
                 call().write('shader node_node_name(string dropdown1 = "prop1", '
                                                    'string dropdown2 = "prop2", '
                                                    'int box1 = 0, '
                                                    'int box2 = 1, '
                                                    'float socket1 = 0.0, '
                                                    'output float socket2 = 0.0){}')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.CodeGeneratorUtil', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_osl_shader()
                self.assertTrue(all(c in mf.mock_calls for c in calls))

    def test_write_osl_file_texture_correct_formatting(self):
        """Test OSL function generation is correct for texture node"""
        self.mock_gui.get_node_type.return_value = "Texture"

        m = mock.MagicMock()
        calls = [call().writelines(['#include "stdosl.h"', '']),
                 call().write('shader node_node_name_texture(int use_mapping = 0, '
                              'matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), '
                              'string dropdown1 = "prop1", '
                              'string dropdown2 = "prop2", '
                              'int box1 = 0, '
                              'int box2 = 1, '
                              'float socket1 = 0.0, '
                              'output float socket2 = 0.0){}')]

        with patch('builtins.open', mock_open(m)) as mf:
            with patch('code_generation.CodeGeneratorUtil', mock.Mock()):
                code_gen = CodeGenerator(self.mock_gui)
                code_gen._add_osl_shader()
                self.assertTrue(all(c in mf.mock_calls for c in calls))


if __name__ == "__main__":
    unittest.main()
