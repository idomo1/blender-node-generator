import unittest
from unittest import mock
from unittest.mock import patch

from code_generation.cmake_code_generator import CMakeCodeManager


class TestCMake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_gui = mock.Mock()

    @classmethod
    def setUp(self):
        self.mock_gui.get_source_path.return_value = 'C:/some/path'
        self.mock_gui.get_node_name.return_value = 'node name'

    def _create_default_cmake_manager(self):
        return CMakeCodeManager(self.mock_gui)

    def test_insert_cmake_middle_sorted_path_correct_formatting(self):
        """Insert a path which alphabetically will fall in the middle of the file list"""
        cmake = self._create_default_cmake_manager()
        file_text = 'closure/bsdf_principled_sheen.h\n' \
                    '  closure/bsdf_hair_principled.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_SVM_HEADERS\n' \
                    '  svm/svm.h\n' \
                    '  svm/svm_ao.h\n' \
                    '  svm/svm_aov.h\n' \
                    '  svm/svm_attribute.h\n' \
                    '  svm/svm_bevel.h\n' \
                    '  svm/svm_blackbody.h\n' \
                    '  svm/svm_bump.h\n' \
                    '  svm/svm_camera.h\n' \
                    '  svm/svm_clamp.h\n' \
                    '  svm/svm_closure.h\n' \
                    '  svm/svm_convert.h\n' \
                    '  svm/svm_checker.h\n' \
                    '  svm/svm_color_util.h\n' \
                    '  svm/svm_brick.h\n' \
                    '  svm/svm_displace.h\n' \
                    '  svm/svm_fresnel.h\n' \
                    '  svm/svm_wireframe.h\n' \
                    '  svm/svm_wavelength.h\n' \
                    '  svm/svm_gamma.h\n' \
                    '  svm/svm_brightness.h\n' \
                    '  svm/svm_geometry.h\n' \
                    '  svm/svm_gradient.h\n' \
                    '  svm/svm_hsv.h\n' \
                    '  svm/svm_ies.h\n' \
                    '  svm/svm_image.h\n' \
                    '  svm/svm_invert.h\n' \
                    '  svm/svm_light_path.h\n' \
                    '  svm/svm_magic.h\n' \
                    '  svm/svm_map_range.h\n' \
                    '  svm/svm_mapping.h\n' \
                    '  svm/svm_mapping_util.h\n' \
                    '  svm/svm_math.h\n' \
                    '  svm/svm_math_util.h\n' \
                    '  svm/svm_mix.h\n' \
                    '  svm/svm_musgrave.h\n' \
                    '  svm/svm_noise.h\n' \
                    '  svm/svm_noisetex.h\n' \
                    '  svm/svm_normal.h\n' \
                    '  svm/svm_ramp.h\n' \
                    '  svm/svm_ramp_util.h\n' \
                    '  svm/svm_sepcomb_hsv.h\n' \
                    '  svm/svm_sepcomb_vector.h\n' \
                    '  svm/svm_sky.h\n' \
                    '  svm/svm_tex_coord.h\n' \
                    '  svm/svm_truchet.h\n' \
                    '  svm/svm_fractal_noise.h\n' \
                    '  svm/svm_types.h\n' \
                    '  svm/svm_value.h\n' \
                    '  svm/svm_vector_transform.h\n' \
                    '  svm/svm_voronoi.h\n' \
                    '  svm/svm_voxel.h\n' \
                    '  svm/svm_wave.h\n' \
                    '  svm/svm_white_noise.h\n' \
                    '  svm/svm_vertex_color.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_GEOM_HEADERS\n'
        text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
                                                 ')\n\n'
                                                 'set(SRC_SVM_HEADERS)'), file_text, '  svm/svm_node_name.h')

        self.assertTrue('  svm/svm_fresnel.h\n'
                        '  svm/svm_node_name.h\n'
                        '  svm/svm_wireframe.h\n' in text)

    def test_insert_cmake_first_sorted_path_correct_formatting(self):
        """Insert a path which alphabetically will fall at the start of the file list"""
        cmake = self._create_default_cmake_manager()
        file_text = 'closure/bsdf_principled_sheen.h\n' \
                    '  closure/bsdf_hair_principled.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_SVM_HEADERS\n' \
                    '  svm/svm.h\n' \
                    '  svm/svm_ao.h\n' \
                    '  svm/svm_aov.h\n' \
                    '  svm/svm_attribute.h\n' \
                    '  svm/svm_bevel.h\n' \
                    '  svm/svm_blackbody.h\n' \
                    '  svm/svm_bump.h\n' \
                    '  svm/svm_camera.h\n' \
                    '  svm/svm_clamp.h\n' \
                    '  svm/svm_closure.h\n' \
                    '  svm/svm_convert.h\n' \
                    '  svm/svm_checker.h\n' \
                    '  svm/svm_color_util.h\n' \
                    '  svm/svm_brick.h\n' \
                    '  svm/svm_displace.h\n' \
                    '  svm/svm_fresnel.h\n' \
                    '  svm/svm_wireframe.h\n' \
                    '  svm/svm_wavelength.h\n' \
                    '  svm/svm_gamma.h\n' \
                    '  svm/svm_brightness.h\n' \
                    '  svm/svm_geometry.h\n' \
                    '  svm/svm_gradient.h\n' \
                    '  svm/svm_hsv.h\n' \
                    '  svm/svm_ies.h\n' \
                    '  svm/svm_image.h\n' \
                    '  svm/svm_invert.h\n' \
                    '  svm/svm_light_path.h\n' \
                    '  svm/svm_magic.h\n' \
                    '  svm/svm_map_range.h\n' \
                    '  svm/svm_mapping.h\n' \
                    '  svm/svm_mapping_util.h\n' \
                    '  svm/svm_math.h\n' \
                    '  svm/svm_math_util.h\n' \
                    '  svm/svm_mix.h\n' \
                    '  svm/svm_musgrave.h\n' \
                    '  svm/svm_noise.h\n' \
                    '  svm/svm_noisetex.h\n' \
                    '  svm/svm_normal.h\n' \
                    '  svm/svm_ramp.h\n' \
                    '  svm/svm_ramp_util.h\n' \
                    '  svm/svm_sepcomb_hsv.h\n' \
                    '  svm/svm_sepcomb_vector.h\n' \
                    '  svm/svm_sky.h\n' \
                    '  svm/svm_tex_coord.h\n' \
                    '  svm/svm_truchet.h\n' \
                    '  svm/svm_fractal_noise.h\n' \
                    '  svm/svm_types.h\n' \
                    '  svm/svm_value.h\n' \
                    '  svm/svm_vector_transform.h\n' \
                    '  svm/svm_voronoi.h\n' \
                    '  svm/svm_voxel.h\n' \
                    '  svm/svm_wave.h\n' \
                    '  svm/svm_white_noise.h\n' \
                    '  svm/svm_vertex_color.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_GEOM_HEADERS\n'
        text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
                                                 ')\n\n'
                                                 'set(SRC_SVM_HEADERS)'), file_text, '  a')

        self.assertTrue('  a\n'
                        '  svm/svm.h\n' in text)

    def test_insert_cmake_last_sorted_path_correct_formatting(self):
        """Insert a path which alphabetically will fall at the end of the file list"""
        cmake = self._create_default_cmake_manager()
        file_text = 'closure/bsdf_principled_sheen.h\n' \
                    '  closure/bsdf_hair_principled.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_SVM_HEADERS\n' \
                    '  svm/svm.h\n' \
                    '  svm/svm_ao.h\n' \
                    '  svm/svm_aov.h\n' \
                    '  svm/svm_attribute.h\n' \
                    '  svm/svm_bevel.h\n' \
                    '  svm/svm_blackbody.h\n' \
                    '  svm/svm_bump.h\n' \
                    '  svm/svm_camera.h\n' \
                    '  svm/svm_clamp.h\n' \
                    '  svm/svm_closure.h\n' \
                    '  svm/svm_convert.h\n' \
                    '  svm/svm_checker.h\n' \
                    '  svm/svm_color_util.h\n' \
                    '  svm/svm_brick.h\n' \
                    '  svm/svm_displace.h\n' \
                    '  svm/svm_fresnel.h\n' \
                    '  svm/svm_wireframe.h\n' \
                    '  svm/svm_wavelength.h\n' \
                    '  svm/svm_gamma.h\n' \
                    '  svm/svm_brightness.h\n' \
                    '  svm/svm_geometry.h\n' \
                    '  svm/svm_gradient.h\n' \
                    '  svm/svm_hsv.h\n' \
                    '  svm/svm_ies.h\n' \
                    '  svm/svm_image.h\n' \
                    '  svm/svm_invert.h\n' \
                    '  svm/svm_light_path.h\n' \
                    '  svm/svm_magic.h\n' \
                    '  svm/svm_map_range.h\n' \
                    '  svm/svm_mapping.h\n' \
                    '  svm/svm_mapping_util.h\n' \
                    '  svm/svm_math.h\n' \
                    '  svm/svm_math_util.h\n' \
                    '  svm/svm_mix.h\n' \
                    '  svm/svm_musgrave.h\n' \
                    '  svm/svm_noise.h\n' \
                    '  svm/svm_noisetex.h\n' \
                    '  svm/svm_normal.h\n' \
                    '  svm/svm_ramp.h\n' \
                    '  svm/svm_ramp_util.h\n' \
                    '  svm/svm_sepcomb_hsv.h\n' \
                    '  svm/svm_sepcomb_vector.h\n' \
                    '  svm/svm_sky.h\n' \
                    '  svm/svm_tex_coord.h\n' \
                    '  svm/svm_truchet.h\n' \
                    '  svm/svm_fractal_noise.h\n' \
                    '  svm/svm_types.h\n' \
                    '  svm/svm_value.h\n' \
                    '  svm/svm_vector_transform.h\n' \
                    '  svm/svm_voronoi.h\n' \
                    '  svm/svm_voxel.h\n' \
                    '  svm/svm_wave.h\n' \
                    '  svm/svm_white_noise.h\n' \
                    '  svm/svm_vertex_color.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_GEOM_HEADERS\n'
        text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
                                                 ')\n\n'
                                                 'set(SRC_SVM_HEADERS)'), file_text, '  z')

        self.assertTrue('  svm/svm_vertex_color.h\n'
                        '  z\n' in text)

    def test_write_svm_cmake_middle_sorted_name_correct_formatting(self):
        """Insert a name which alphabetically will fall in the middle of the file list"""
        with patch('builtins.open', mock.mock_open(read_data=
                                                    'closure/bsdf_principled_sheen.h\n'
                                                    '  closure/bsdf_hair_principled.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_SVM_HEADERS\n'
                                                    '  svm/svm.h\n'
                                                    '  svm/svm_ao.h\n'
                                                    '  svm/svm_aov.h\n'
                                                    '  svm/svm_attribute.h\n'
                                                    '  svm/svm_bevel.h\n'
                                                    '  svm/svm_blackbody.h\n'
                                                    '  svm/svm_bump.h\n'
                                                    '  svm/svm_camera.h\n'
                                                    '  svm/svm_clamp.h\n'
                                                    '  svm/svm_closure.h\n'
                                                    '  svm/svm_convert.h\n'
                                                    '  svm/svm_checker.h\n'
                                                    '  svm/svm_color_util.h\n'
                                                    '  svm/svm_brick.h\n'
                                                    '  svm/svm_displace.h\n'
                                                    '  svm/svm_fresnel.h\n'
                                                    '  svm/svm_wireframe.h\n'
                                                    '  svm/svm_wavelength.h\n'
                                                    '  svm/svm_gamma.h\n'
                                                    '  svm/svm_brightness.h\n'
                                                    '  svm/svm_geometry.h\n'
                                                    '  svm/svm_gradient.h\n'
                                                    '  svm/svm_hsv.h\n'
                                                    '  svm/svm_ies.h\n'
                                                    '  svm/svm_image.h\n'
                                                    '  svm/svm_invert.h\n'
                                                    '  svm/svm_light_path.h\n'
                                                    '  svm/svm_magic.h\n'
                                                    '  svm/svm_map_range.h\n'
                                                    '  svm/svm_mapping.h\n'
                                                    '  svm/svm_mapping_util.h\n'
                                                    '  svm/svm_math.h\n'
                                                    '  svm/svm_math_util.h\n'
                                                    '  svm/svm_mix.h\n'
                                                    '  svm/svm_musgrave.h\n'
                                                    '  svm/svm_noise.h\n'
                                                    '  svm/svm_noisetex.h\n'
                                                    '  svm/svm_normal.h\n'
                                                    '  svm/svm_ramp.h\n'
                                                    '  svm/svm_ramp_util.h\n'
                                                    '  svm/svm_sepcomb_hsv.h\n'
                                                    '  svm/svm_sepcomb_vector.h\n'
                                                    '  svm/svm_sky.h\n'
                                                    '  svm/svm_tex_coord.h\n'
                                                    '  svm/svm_truchet.h\n'
                                                    '  svm/svm_fractal_noise.h\n'
                                                    '  svm/svm_types.h\n'
                                                    '  svm/svm_value.h\n'
                                                    '  svm/svm_vector_transform.h\n'
                                                    '  svm/svm_voronoi.h\n'
                                                    '  svm/svm_voxel.h\n'
                                                    '  svm/svm_wave.h\n'
                                                    '  svm/svm_white_noise.h\n'
                                                    '  svm/svm_vertex_color.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_GEOM_HEADERS\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_svm()

            self.assertTrue('  svm/svm_fresnel.h\n'
                            '  svm/svm_node_name.h\n'
                            '  svm/svm_wireframe.h\n' in mf.mock_calls[-3][1][0])

    def test_write_svm_cmake_first_sorted_name_correct_formatting(self):
        """Insert a name which alphabetically will fall at the start of the file list"""
        self.mock_gui.get_node_name.return_value = 'a'
        with patch('builtins.open', mock.mock_open(read_data=
                                                    'closure/bsdf_principled_sheen.h\n'
                                                    '  closure/bsdf_hair_principled.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_SVM_HEADERS\n'
                                                    '  svm/svm.h\n'
                                                    '  svm/svm_ao.h\n'
                                                    '  svm/svm_aov.h\n'
                                                    '  svm/svm_attribute.h\n'
                                                    '  svm/svm_bevel.h\n'
                                                    '  svm/svm_blackbody.h\n'
                                                    '  svm/svm_bump.h\n'
                                                    '  svm/svm_camera.h\n'
                                                    '  svm/svm_clamp.h\n'
                                                    '  svm/svm_closure.h\n'
                                                    '  svm/svm_convert.h\n'
                                                    '  svm/svm_checker.h\n'
                                                    '  svm/svm_color_util.h\n'
                                                    '  svm/svm_brick.h\n'
                                                    '  svm/svm_displace.h\n'
                                                    '  svm/svm_fresnel.h\n'
                                                    '  svm/svm_wireframe.h\n'
                                                    '  svm/svm_wavelength.h\n'
                                                    '  svm/svm_gamma.h\n'
                                                    '  svm/svm_brightness.h\n'
                                                    '  svm/svm_geometry.h\n'
                                                    '  svm/svm_gradient.h\n'
                                                    '  svm/svm_hsv.h\n'
                                                    '  svm/svm_ies.h\n'
                                                    '  svm/svm_image.h\n'
                                                    '  svm/svm_invert.h\n'
                                                    '  svm/svm_light_path.h\n'
                                                    '  svm/svm_magic.h\n'
                                                    '  svm/svm_map_range.h\n'
                                                    '  svm/svm_mapping.h\n'
                                                    '  svm/svm_mapping_util.h\n'
                                                    '  svm/svm_math.h\n'
                                                    '  svm/svm_math_util.h\n'
                                                    '  svm/svm_mix.h\n'
                                                    '  svm/svm_musgrave.h\n'
                                                    '  svm/svm_noise.h\n'
                                                    '  svm/svm_noisetex.h\n'
                                                    '  svm/svm_normal.h\n'
                                                    '  svm/svm_ramp.h\n'
                                                    '  svm/svm_ramp_util.h\n'
                                                    '  svm/svm_sepcomb_hsv.h\n'
                                                    '  svm/svm_sepcomb_vector.h\n'
                                                    '  svm/svm_sky.h\n'
                                                    '  svm/svm_tex_coord.h\n'
                                                    '  svm/svm_truchet.h\n'
                                                    '  svm/svm_fractal_noise.h\n'
                                                    '  svm/svm_types.h\n'
                                                    '  svm/svm_value.h\n'
                                                    '  svm/svm_vector_transform.h\n'
                                                    '  svm/svm_voronoi.h\n'
                                                    '  svm/svm_voxel.h\n'
                                                    '  svm/svm_wave.h\n'
                                                    '  svm/svm_white_noise.h\n'
                                                    '  svm/svm_vertex_color.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_GEOM_HEADERS\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_svm()

            self.assertTrue('  svm/svm_a.h\n'
                            '  svm/svm_ao.h\n' in mf.mock_calls[-3][1][0])

    def test_write_svm_cmake_last_sorted_name_correct_formatting(self):
        """Insert a name which alphabetically will fall at the end of the file list"""
        self.mock_gui.get_node_name.return_value = 'z'
        with patch('builtins.open', mock.mock_open(read_data=
                                                    'closure/bsdf_principled_sheen.h\n'
                                                    '  closure/bsdf_hair_principled.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_SVM_HEADERS\n'
                                                    '  svm/svm.h\n'
                                                    '  svm/svm_ao.h\n'
                                                    '  svm/svm_aov.h\n'
                                                    '  svm/svm_attribute.h\n'
                                                    '  svm/svm_bevel.h\n'
                                                    '  svm/svm_blackbody.h\n'
                                                    '  svm/svm_bump.h\n'
                                                    '  svm/svm_camera.h\n'
                                                    '  svm/svm_clamp.h\n'
                                                    '  svm/svm_closure.h\n'
                                                    '  svm/svm_convert.h\n'
                                                    '  svm/svm_checker.h\n'
                                                    '  svm/svm_color_util.h\n'
                                                    '  svm/svm_brick.h\n'
                                                    '  svm/svm_displace.h\n'
                                                    '  svm/svm_fresnel.h\n'
                                                    '  svm/svm_wireframe.h\n'
                                                    '  svm/svm_wavelength.h\n'
                                                    '  svm/svm_gamma.h\n'
                                                    '  svm/svm_brightness.h\n'
                                                    '  svm/svm_geometry.h\n'
                                                    '  svm/svm_gradient.h\n'
                                                    '  svm/svm_hsv.h\n'
                                                    '  svm/svm_ies.h\n'
                                                    '  svm/svm_image.h\n'
                                                    '  svm/svm_invert.h\n'
                                                    '  svm/svm_light_path.h\n'
                                                    '  svm/svm_magic.h\n'
                                                    '  svm/svm_map_range.h\n'
                                                    '  svm/svm_mapping.h\n'
                                                    '  svm/svm_mapping_util.h\n'
                                                    '  svm/svm_math.h\n'
                                                    '  svm/svm_math_util.h\n'
                                                    '  svm/svm_mix.h\n'
                                                    '  svm/svm_musgrave.h\n'
                                                    '  svm/svm_noise.h\n'
                                                    '  svm/svm_noisetex.h\n'
                                                    '  svm/svm_normal.h\n'
                                                    '  svm/svm_ramp.h\n'
                                                    '  svm/svm_ramp_util.h\n'
                                                    '  svm/svm_sepcomb_hsv.h\n'
                                                    '  svm/svm_sepcomb_vector.h\n'
                                                    '  svm/svm_sky.h\n'
                                                    '  svm/svm_tex_coord.h\n'
                                                    '  svm/svm_truchet.h\n'
                                                    '  svm/svm_fractal_noise.h\n'
                                                    '  svm/svm_types.h\n'
                                                    '  svm/svm_value.h\n'
                                                    '  svm/svm_vector_transform.h\n'
                                                    '  svm/svm_voronoi.h\n'
                                                    '  svm/svm_voxel.h\n'
                                                    '  svm/svm_wave.h\n'
                                                    '  svm/svm_white_noise.h\n'
                                                    '  svm/svm_vertex_color.h\n'
                                                    ')\n'
                                                    '\n'
                                                    'set(SRC_GEOM_HEADERS\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_svm()

            self.assertTrue('  svm/svm_vertex_color.h\n'
                            '  svm/svm_z.h\n)' in mf.mock_calls[-3][1][0])


if __name__ == '__main__':
    unittest.main()
