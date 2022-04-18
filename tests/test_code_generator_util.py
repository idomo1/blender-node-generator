import unittest

from code_generation import code_generator_util
from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp
from node_types.prop_int import IntProp


class TestUsesDna(unittest.TestCase):
    def test_no_props_false(self):
        self.assertFalse(code_generator_util.uses_dna([], "Shader"))

    def test_no_props_texture_type_true(self):
        self.assertTrue(code_generator_util.uses_dna([], "Texture"))

    def test_two_enums_one_bool_true(self):
        props = [{'data-type': EnumProp()}, {'data-type': EnumProp()}, {'data-type': BoolProp()}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_two_enums_false(self):
        props = [{'data-type': EnumProp()}, {'data-type': EnumProp()}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_16_bools_false(self):
        props = [{'data-type': BoolProp()} for _ in range(16)]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_17_bools_true(self):
        props = [{'data-type': BoolProp()} for _ in range(17)]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_16_bools_false(self):
        props = [{'data-type': BoolProp()} for _ in range(17)] + [{'data-type': EnumProp()}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_int_false(self):
        props = [{'data-type': EnumProp()}, {'data-type': IntProp()}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_int_bool_true(self):
        props = [{'data-type': EnumProp()}, {'data-type': IntProp()}, {'data-type': BoolProp()}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_two_int_false(self):
        props = [{'data-type': IntProp()}, {'data-type': IntProp()}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_two_int_one_bool_false(self):
        props = [{'data-type': IntProp()}, {'data-type': BoolProp()}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_three_enum_true(self):
        props = [{'data-type': EnumProp()} for _ in range(3)]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_three_enum_texture_type_true(self):
        props = [{'data-type': EnumProp()} for _ in range(3)]
        self.assertTrue(code_generator_util.uses_dna(props, "Texture"))

    def test_fill_whitespace_correct_formatting(self):
        items = ['ShaderNode', 'SH_NODE_OUTPUT_MATERIAL', 'def_sh_output', '"OUTPUT_MATERIAL"',
                 'OutputMaterial', '"Material Output"', '""']
        size = 138
        gaps = [0, 16, 44, 68, 90, 108, 129]
        text = code_generator_util.fill_white_space(items, size, gaps)

        self.assertTrue(text ==
                        'ShaderNode,     SH_NODE_OUTPUT_MATERIAL,    def_sh_output,          "OUTPUT_MATERIAL",    OutputMaterial,   "Material Output",   ""       ')

    def test_fill_whitespace2_correct_formatting(self):
        items = ['ShaderNode', 'SH_NODE_EEVEE_SPECULAR', '0', '"EEVEE_SPECULAR"',
                 'EeveeSpecular', '"Specular"', '""']
        size = 138
        gaps = [0, 16, 44, 68, 90, 108, 129]
        text = code_generator_util.fill_white_space(items, size, gaps)

        self.assertTrue(text ==
                        'ShaderNode,     SH_NODE_EEVEE_SPECULAR,     0,                      "EEVEE_SPECULAR",     EeveeSpecular,    "Specular",          ""       ')


if __name__ == '__main__':
    unittest.main()
