import unittest
from unittest.mock import Mock, mock_open, patch, call

from code_generation import DNAWriter


class TestDNAWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mock_gui = Mock()

    def _create_default_class(self, props=None, sockets=None, node_type='Shader', is_texture_node=False):
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
        if node_type == 'Texture':
            suffix = 'tex'
        elif node_type == 'Bsdf':
            suffix = 'bsdf'
        else:
            suffix = ''
        self._mock_gui.type_suffix_abbreviated.return_value = suffix
        self._mock_gui.get_node_type.return_value = node_type
        self._mock_gui.is_texture_node.return_value = is_texture_node
        return DNAWriter(self._mock_gui)

    def test_write_dna_struct_texture_node_correct_formatting(self):
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
                                                        '} NodeShaderAttribute;\n\n'
                                                        'enum {\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                        '};\n'
                                                        '\n'
                                                        '/* Output shader node */\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(node_type='Texture')
                code_gen.write_dna_node_type()

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
                                                           'typedef struct NodeTexNodeName {NodeTexBase base;int dropdown1, dropdown2, int1, box1, box2; float float1; char string1[64];} NodeTexNodeName;\n'
                                                           '\n'
                                                           'typedef struct NodeShaderAttribute {\n'
                                                           '  char name[64];\n'
                                                           '} NodeShaderAttribute;\n\n'
                                                           'enum {\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                           '};\n'
                                                           '\n'
                                                           '/* node name */\n'
                                                           '#define SHD_NODE_NAME_BOX1 1\n'
                                                           '#define SHD_NODE_NAME_BOX2 2\n\n'
                                                           'enum {'
                                                           'SHD_NODE_NAME_PROP1 = 1,'
                                                           'SHD_NODE_NAME_PROP2 = 2,};\n\n'
                                                           'enum {'
                                                           'SHD_NODE_NAME_PROP3 = 1,'
                                                           'SHD_NODE_NAME_PROP4 = 2,'
                                                           '};\n\n'
                                                           '/* Output shader node */\n')

    def test_write_dna_struct_no_dropdowns_correct_formatting(self):
        props = [
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "int2", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0}]
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
                                                        '} NodeShaderAttribute;\n\n'
                                                        'enum {\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                        '};\n'
                                                        '\n'
                                                        '/* Output shader node */\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props)
                code_gen.write_dna_node_type()

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
                                                           'typedef struct NodeNodeName {int int1, int2, box1, box2; float float1; char _pad[4];} NodeNodeName;\n'
                                                           '\n'
                                                           'typedef struct NodeShaderAttribute {\n'
                                                           '  char name[64];\n'
                                                           '} NodeShaderAttribute;\n\n'
                                                           'enum {\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                           '};\n'
                                                           '\n'
                                                           '/* node name */\n'
                                                           '#define SHD_NODE_NAME_BOX1 1\n'
                                                           '#define SHD_NODE_NAME_BOX2 2\n\n'
                                                           '/* Output shader node */\n')

    def test_write_dna_struct_requires_padding_correct_formatting(self):
        props = [
            {"name": "dropdown1", 'data-type': "Enum", "options": [{"name": "prop1", "desc": "Short description"},
                                                                   {"name": "prop2", "desc": "Short description"}],
             "default": '"prop1"'}]
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
                                                        '} NodeShaderAttribute;\n\n'
                                                        'enum {\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                        '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                        '};\n'
                                                        '\n'
                                                        '/* Output shader node */\n')) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting', Mock()):
                code_gen = self._create_default_class(props=props, node_type='Texture')
                code_gen.write_dna_node_type()

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
                                                           'typedef struct NodeTexNodeName {NodeTexBase base;int dropdown1; char _pad[4];} NodeTexNodeName;\n'
                                                           '\n'
                                                           'typedef struct NodeShaderAttribute {\n'
                                                           '  char name[64];\n'
                                                           '} NodeShaderAttribute;\n\n'
                                                           'enum {\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTCOL = 0,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTWEIGHT = 1,\n'
                                                           '  SHD_POINTDENSITY_COLOR_VERTNOR = 2,\n'
                                                           '};\n\n'
                                                           '/* node name */\n'
                                                           'enum {'
                                                           'SHD_NODE_NAME_PROP1 = 1,'
                                                           'SHD_NODE_NAME_PROP2 = 2,};\n\n'
                                                           '/* Output shader node */\n')

    def test_write_dna_struct_not_needed_no_call(self):
        with patch('builtins.open', mock_open()) as mf:
            with patch('code_generation.code_generator_util.apply_clang_formatting'):
                code_gen = self._create_default_class(props=[])
                code_gen.write_dna_node_type()

                self.assertTrue(call().write('') in mf.mock_calls)


if __name__ == '__main__':
    unittest.main()
