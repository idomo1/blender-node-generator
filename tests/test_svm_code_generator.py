import unittest

from code_generation import SVMCompilationManager


class TestSVMCodeGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Default Props/Sockets"""
        cls.props = [
            {"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
             "default": 'prop1'},
            {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
             "default": 'prop3'},
            {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
            {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
            {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
            {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0, "max": 1.0},
            {"name": "string1", 'data-type': "String", "sub-type": "PROP_NONE", "size": 64, "default": '""'}]
        cls.sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                        'sub-type': 'PROP_NONE', 'flag': 'None',
                        'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                       {'type': "Output", 'name': "socket2", 'data-type': "Float",
                        'sub-type': 'PROP_NONE', 'flag': 'None',
                        'min': "-1.0", 'max': "1.0", 'default': "0.5"}]

    def _create_default_svm_manager(self):
        return SVMCompilationManager(self.props, self.sockets, 'node name', False)

    def test_generate_param_names_correct_formatting(self):
        svm = self._create_default_svm_manager()
        names = svm._generate_param_names()
        self.assertTrue(names == ['dropdown1', 'dropdown2', 'int1', 'box1', 'box2', '__float_as_int(float1)',
                                  'socket1_stack_offset', 'socket2_stack_offset'])

    def test_generate_svm_params_less_than_4_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1}]
        svm = SVMCompilationManager(props, [], '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'dropdown1, dropdown2, int1')

    def test_generate_svm_params_4_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()

        self.assertTrue(params == 'dropdown1, dropdown2, '
                                  'compiler.encode_uchar4(int1, socket1_stack_offset)')

    def test_generate_svm_params_5_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2), '
                                  'compiler.encode_uchar4(int1, __float_as_int(float1)), '
                                  'socket1_stack_offset')

    def test_generate_svm_params_6_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Output", 'name': "socket2", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1), '
                                  'compiler.encode_uchar4(__float_as_int(float1), socket1_stack_offset, socket2_stack_offset)')

    def test_generate_svm_params_7_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Output", 'name': "socket2", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1), '
                                  'compiler.encode_uchar4(box1, __float_as_int(float1), socket1_stack_offset), '
                                  'socket2_stack_offset')

    def test_generate_svm_params_8_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Output", 'name': "socket2", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                  'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                  'socket2_stack_offset')

    def test_generate_svm_params_9_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "socket2", 'data-type': "Vector", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket3", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                  'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset, socket2_stack_offset), '
                                  'socket3_stack_offset')

    def test_generate_svm_params_10_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "socket2", 'data-type': "Vector", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket3", 'data-type': "RGBA", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket4", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                  'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset, socket2_stack_offset), '
                                  'compiler.encode_uchar4(socket3_stack_offset, socket4_stack_offset)')

    def test_generate_svm_params_11_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float2", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float3", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "socket2", 'data-type': "Vector", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket3", 'data-type': "RGBA", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"}]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                  'compiler.encode_uchar4(box2, __float_as_int(float1), __float_as_int(float2), __float_as_int(float3)), '
                                  'compiler.encode_uchar4(socket1_stack_offset, socket2_stack_offset, socket3_stack_offset)')

    def test_generate_svm_params_12_params_correct_formatting(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float2", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float3", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "socket2", 'data-type': "Vector", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket3", 'data-type': "RGBA", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket4", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        params = svm._generate_svm_params()
        self.assertTrue(params == 'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                  'compiler.encode_uchar4(box2, __float_as_int(float1), __float_as_int(float2), __float_as_int(float3)), '
                                  'compiler.encode_uchar4(socket1_stack_offset, socket2_stack_offset, socket3_stack_offset, socket4_stack_offset)')

    def test_generate_svm_params_13_params_raises_exception(self):
        props = [{"name": "dropdown1", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop1", "prop2"],
                  "default": 'prop1'},
                 {"name": "dropdown2", 'data-type': "Enum", "sub-type": "PROP_NONE", "options": ["prop3", "prop4"],
                  "default": 'prop3'},
                 {"name": "int1", 'data-type': "Int", "sub-type": "PROP_NONE", "default": 0, "min": -1, "max": 1},
                 {"name": "box1", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 0},
                 {"name": "box2", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "box3", 'data-type': "Boolean", "sub-type": "PROP_NONE", "default": 1},
                 {"name": "float1", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float2", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0},
                 {"name": "float3", 'data-type': "Float", "sub-type": "PROP_NONE", "default": 0.0, "min": -1.0,
                  "max": 1.0}]
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "socket2", 'data-type': "Vector", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket3", 'data-type': "RGBA", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket4", 'data-type': "Float", 'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}
                   ]
        svm = SVMCompilationManager(props, sockets, '', False)
        self.assertRaises(Exception, svm._generate_svm_params)

    def test_generate_stack_offsets_correct_formatting(self):
        svm = self._create_default_svm_manager()
        offsets = svm._generate_stack_offsets()

        self.assertTrue(offsets == 'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                   'int socket2_stack_offset = compiler.stack_assign(socket2_out);')

    def test_generate_stack_offsets_tex_node_with_vector_correct_formatting(self):
        props = []
        sockets = [{'type': "Input", 'name': "socket1", 'data-type': "Float",
                    'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"},
                   {'type': "Input", 'name': "vector", 'data-type': "Vector",
                    'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"},
                   {'type': "Output", 'name': "socket2", 'data-type': "Float",
                    'sub-type': 'PROP_NONE', 'flag': 'None',
                    'min': "-1.0", 'max': "1.0", 'default': "0.5"}]
        svm = SVMCompilationManager(props, sockets, '', True)
        offsets = svm._generate_stack_offsets()

        self.assertTrue(offsets == 'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                   'int vector_stack_offset = tex_mapping.compile_begin(compiler, vector_in);'
                                   'int socket2_stack_offset = compiler.stack_assign(socket2_out);')

    def test_generate_float_optimizations_correct_formatting(self):
        svm = self._create_default_svm_manager()
        opt = svm._generate_float_optimizations()

        self.assertTrue(opt == 'compiler.add_node(__float_as_int(socket1));')

    def test_generate_float_optimizations_no_float_inputs_correct_formatting(self):
        svm = SVMCompilationManager([], [], '', False)
        opt = svm._generate_float_optimizations()

        self.assertTrue(opt == '')

    def test_generate_float_optimization_4_inputs_correct_formatting(self):
        sockets = [{'name': 'socket1', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket2', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket3', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket4', 'type': 'Input', 'data-type': 'Float'}]
        svm = SVMCompilationManager([], sockets, '', False)
        opt = svm._generate_float_optimizations()

        self.assertTrue(opt == 'compiler.add_node(__float_as_int(socket1), __float_as_int(socket2), '
                               '__float_as_int(socket3), __float_as_int(socket4));')

    def test_generate_float_optimization_5_inputs_correct_formatting(self):
        sockets = [{'name': 'socket1', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket2', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket3', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket4', 'type': 'Input', 'data-type': 'Float'},
                   {'name': 'socket5', 'type': 'Input', 'data-type': 'Float'}]
        svm = SVMCompilationManager([], sockets, '', False)
        opt = svm._generate_float_optimizations()

        self.assertTrue(opt == 'compiler.add_node(__float_as_int(socket1), __float_as_int(socket2), '
                               '__float_as_int(socket3), __float_as_int(socket4));'
                               'compiler.add_node(__float_as_int(socket5));')

    def test_generate_add_node_correct_formatting(self):
        svm = self._create_default_svm_manager()
        node = svm._generate_add_node()

        self.assertTrue(node == 'compiler.add_node(NODE_NODE_NAME, '
                                'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                'socket2_stack_offset'
                                ');'
                                'compiler.add_node(__float_as_int(socket1));')

    def test_generate_add_texture_node_correct_formatting(self):
        svm = SVMCompilationManager(self.props, self.sockets, 'node name', True, False)
        node = svm._generate_add_node()

        self.assertTrue(node == 'compiler.add_node(NODE_TEX_NODE_NAME, '
                                'compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                'socket2_stack_offset'
                                ');'
                                'compiler.add_node(__float_as_int(socket1));')

    def test_generate_get_sockets_correct_formatting(self):
        svm = self._create_default_svm_manager()
        socks = svm._generate_get_sockets()

        self.assertTrue(socks == 'ShaderInput *socket1_in = input("Socket1");'
                                 'ShaderOutput *socket2_out = output("Socket2");')

    def test_generate_svm_func_correct_formatting(self):
        svm = self._create_default_svm_manager()
        func = svm.generate_svm_compile_func()

        self.assertTrue(func == 'void NodeNameNode::compile(SVMCompiler &compiler){'
                                'ShaderInput *socket1_in = input("Socket1");'
                                'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                'compiler.add_node(NODE_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                'socket2_stack_offset'
                                ');'
                                'compiler.add_node(__float_as_int(socket1));'
                                '}\n\n')

    def test_generate_svm_func_texture_node_no_mapping_correct_formatting(self):
        svm = SVMCompilationManager(self.props, self.sockets, 'node name', True, False)
        func = svm.generate_svm_compile_func()

        self.assertTrue(func == 'void NodeNameTextureNode::compile(SVMCompiler &compiler){'
                                'ShaderInput *socket1_in = input("Socket1");'
                                'ShaderOutput *socket2_out = output("Socket2");\n\n'
                                'int socket1_stack_offset = compiler.stack_assign_if_linked(socket1_in);'
                                'int socket2_stack_offset = compiler.stack_assign(socket2_out);\n\n'
                                'compiler.add_node(NODE_TEX_NODE_NAME, compiler.encode_uchar4(dropdown1, dropdown2, int1, box1), '
                                'compiler.encode_uchar4(box2, __float_as_int(float1), socket1_stack_offset), '
                                'socket2_stack_offset'
                                ');'
                                'compiler.add_node(__float_as_int(socket1));'
                                '}\n\n')

    def test_generate_svm_func_texture_node_uses_mapping_correct_formatting(self):
        sockets = self.sockets.copy()
        sockets.insert(0, {'type': "Input", 'name': "vector", 'data-type': "Vector", 'sub-type': 'PROP_NONE',
                           'flag': 'None', 'min': "-1.0,-1.0,-1.0", 'max': "1.0,1.0,1.0", 'default': "0.5,0.5,0.5"})
        svm = SVMCompilationManager(self.props, sockets, 'node name', True, True)
        func = svm.generate_svm_compile_func()

        self.assertTrue(func == 'void NodeNameTextureNode::compile(SVMCompiler &compiler){'
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
                                '}\n\n')


if __name__ == '__main__':
    unittest.main()
