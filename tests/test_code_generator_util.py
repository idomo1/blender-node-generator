import unittest

from code_generation import code_generator_util


class TestUsesDna(unittest.TestCase):
    def test_no_props_false(self):
        self.assertFalse(code_generator_util.uses_dna([], "Shader"))

    def test_no_props_texture_type_true(self):
        self.assertTrue(code_generator_util.uses_dna([], "Texture"))

    def test_string_true(self):
        self.assertTrue(code_generator_util.uses_dna([{"type": "String"}], "Texture"))

    def test_two_enums_one_bool_true(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Boolean"}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_two_enums_false(self):
        props = [{"type": "Enum"}, {"type": "Enum"}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_16_bools_false(self):
        props = [{"type": "Boolean"} for _ in range(16)]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_17_bools_true(self):
        props = [{"type": "Boolean"} for _ in range(17)]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_16_bools_false(self):
        props = [{"type": "Boolean"} for _ in range(17)] + [{"type": "Enum"}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_int_false(self):
        props = [{"type": "Enum"}, {"type": "Int"}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_one_enum_int_bool_true(self):
        props = [{"type": "Enum"}, {"type": "Int"}, {"type": "Boolean"}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_two_int_false(self):
        props = [{"type": "Int"}, {"type": "Int"}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_two_int_one_bool_false(self):
        props = [{"type": "Int"}, {"type": "Boolean"}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_three_float_true(self):
        props = [{"type": "Float"} for _ in range(3)]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_two_float_false(self):
        props = [{"type": "Float"} for _ in range(2)]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_two_float_enum_false(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Float"}, {"type": "Float"}]
        self.assertFalse(code_generator_util.uses_dna(props, "Shader"))

    def test_two_float_enum_one_int_true(self):
        props = [{"type": "Enum"}, {"type": "Enum"}, {"type": "Int"}, {"type": "Float"}, {"type": "Float"}]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_three_enum_true(self):
        props = [{"type": "Enum"} for _ in range(3)]
        self.assertTrue(code_generator_util.uses_dna(props, "Shader"))

    def test_three_enum_texture_type_true(self):
        props = [{"type": "Enum"} for _ in range(3)]
        self.assertTrue(code_generator_util.uses_dna(props, "Texture"))


if __name__ == '__main__':
    unittest.main()
