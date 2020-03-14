import unittest
from unittest import mock
from unittest.mock import patch

from code_generation.cmake_writer import CMakeWriter


class TestCMake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_gui = mock.Mock()

    @classmethod
    def setUp(self):
        self.mock_gui.get_source_path.return_value = 'C:/some/path'
        self.mock_gui.get_node_name.return_value = 'node name'
        self.mock_gui.is_texture_node.return_value = False
        self.mock_gui.type_suffix.return_value = ''
        self.mock_gui.type_suffix_abbreviated.return_value = ''

    def _create_default_cmake_manager(self):
        return CMakeWriter(self.mock_gui)

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

    def test_write_osl_cmake_correct_formatting(self):
        with patch('builtins.open', mock.mock_open(read_data=
                                                   '\n'
                                                   '# OSL node shaders'
                                                   '\n'
                                                   'set(SRC_OSL\n'
                                                   '  node_add_closure.osl\n'
                                                   '  node_ambient_occlusion.osl\n'
                                                   '  node_anisotropic_bsdf.osl\n'
                                                   '  node_attribute.osl\n'
                                                   '  node_background.osl\n'
                                                   '  node_bevel.osl\n'
                                                   '  node_brick_texture.osl\n'
                                                   '  node_brightness.osl\n'
                                                   '  node_bump.osl\n'
                                                   '  node_camera.osl\n'
                                                   '  node_checker_texture.osl\n'
                                                   '  node_clamp.osl\n'
                                                   '  node_combine_rgb.osl\n'
                                                   '  node_combine_hsv.osl\n'
                                                   '  node_combine_xyz.osl\n'
                                                   '  node_convert_from_color.osl\n'
                                                   '  node_convert_from_float.osl\n'
                                                   '  node_convert_from_int.osl\n'
                                                   '  node_convert_from_normal.osl\n'
                                                   '  node_convert_from_point.osl\n'
                                                   '  node_convert_from_vector.osl\n'
                                                   '  node_diffuse_bsdf.osl\n'
                                                   '  node_displacement.osl\n'
                                                   '  node_vector_displacement.osl\n'
                                                   '  node_emission.osl\n'
                                                   '  node_environment_texture.osl\n'
                                                   '  node_fresnel.osl\n'
                                                   '  node_gamma.osl\n'
                                                   '  node_geometry.osl\n'
                                                   '  node_glass_bsdf.osl\n'
                                                   '  node_glossy_bsdf.osl\n'
                                                   '  node_gradient_texture.osl\n'
                                                   '  node_hair_info.osl\n'
                                                   '  node_scatter_volume.osl\n'
                                                   '  node_absorption_volume.osl\n'
                                                   '  node_principled_volume.osl\n'
                                                   '  node_holdout.osl\n'
                                                   '  node_hsv.osl\n'
                                                   '  node_ies_light.osl\n'
                                                   '  node_image_texture.osl\n'
                                                   '  node_invert.osl\n'
                                                   '  node_layer_weight.osl\n'
                                                   '  node_light_falloff.osl\n'
                                                   '  node_light_path.osl\n'
                                                   '  node_magic_texture.osl\n'
                                                   '  node_map_range.osl\n'
                                                   '  node_mapping.osl\n'
                                                   '  node_math.osl\n'
                                                   '  node_mix.osl\n'
                                                   '  node_mix_closure.osl\n'
                                                   '  node_musgrave_texture.osl\n'
                                                   '  node_noise_texture.osl\n'
                                                   '  node_normal.osl\n'
                                                   '  node_normal_map.osl\n'
                                                   '  node_object_info.osl\n'
                                                   '  node_output_displacement.osl\n'
                                                   '  node_output_surface.osl\n'
                                                   '  node_output_volume.osl\n'
                                                   '  node_particle_info.osl\n'
                                                   '  node_refraction_bsdf.osl\n'
                                                   '  node_rgb_curves.osl\n'
                                                   '  node_rgb_ramp.osl\n'
                                                   '  node_separate_rgb.osl\n'
                                                   '  node_separate_hsv.osl\n'
                                                   '  node_separate_xyz.osl\n'
                                                   '  node_set_normal.osl\n'
                                                   '  node_sky_texture.osl\n'
                                                   '  node_subsurface_scattering.osl\n'
                                                   '  node_tangent.osl\n'
                                                   '  node_texture_coordinate.osl\n'
                                                   '  node_toon_bsdf.osl\n'
                                                   '  node_truchet_texture.osl\n'
                                                   '  node_translucent_bsdf.osl\n'
                                                   '  node_transparent_bsdf.osl\n'
                                                   '  node_value.osl\n'
                                                   '  node_vector_curves.osl\n'
                                                   '  node_vector_math.osl\n'
                                                   '  node_vector_transform.osl\n'
                                                   '  node_velvet_bsdf.osl\n'
                                                   '  node_vertex_color.osl\n'
                                                   '  node_voronoi_texture.osl\n'
                                                   '  node_voxel_texture.osl\n'
                                                   '  node_wavelength.osl\n'
                                                   '  node_blackbody.osl\n'
                                                   '  node_wave_texture.osl\n'
                                                   '  node_white_noise_texture.osl\n'
                                                   '  node_wireframe.osl\n'
                                                   '  node_hair_bsdf.osl\n'
                                                   '  node_principled_hair_bsdf.osl\n'
                                                   '  node_uv_map.osl\n'
                                                   '  node_principled_bsdf.osl\n'
                                                   '  node_rgb_to_bw.osl\n'
                                                   ')\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_osl()

            self.assertTrue('  node_node_name.osl\n' in mf.mock_calls[-3][1][0])

    def test_write_node_cmake_correct_formatting(self):
        with patch('builtins.open', mock.mock_open(read_data=
                                                   'set(SRC\n'
                                                   '  composite/nodes/node_composite_alphaOver.c\n' \
                                                   '  composite/nodes/node_composite_bilateralblur.c\n' \
                                                   '  composite/nodes/node_composite_blur.c\n' \
                                                   '  composite/nodes/node_composite_bokehblur.c\n' \
                                                   '  composite/nodes/node_composite_bokehimage.c\n' \
                                                   '  composite/nodes/node_composite_boxmask.c\n' \
                                                   '  composite/nodes/node_composite_brightness.c\n' \
                                                   '  composite/nodes/node_composite_channelMatte.c\n' \
                                                   '  composite/nodes/node_composite_chromaMatte.c\n' \
                                                   '  composite/nodes/node_composite_colorMatte.c\n' \
                                                   '  composite/nodes/node_composite_colorSpill.c\n' \
                                                   '  composite/nodes/node_composite_colorbalance.c\n' \
                                                   '  composite/nodes/node_composite_colorcorrection.c\n' \
                                                   '  composite/nodes/node_composite_common.c\n' \
                                                   '  composite/nodes/node_composite_composite.c\n' \
                                                   '  composite/nodes/node_composite_cornerpin.c\n' \
                                                   '  composite/nodes/node_composite_crop.c\n' \
                                                   '  composite/nodes/node_composite_cryptomatte.c\n' \
                                                   '  composite/nodes/node_composite_curves.c\n' \
                                                   '  composite/nodes/node_composite_defocus.c\n' \
                                                   '  composite/nodes/node_composite_denoise.c\n' \
                                                   '  composite/nodes/node_composite_despeckle.c\n' \
                                                   '  composite/nodes/node_composite_diffMatte.c\n' \
                                                   '  composite/nodes/node_composite_dilate.c\n' \
                                                   '  composite/nodes/node_composite_directionalblur.c\n' \
                                                   '  composite/nodes/node_composite_displace.c\n' \
                                                   '  composite/nodes/node_composite_distanceMatte.c\n' \
                                                   '  composite/nodes/node_composite_doubleEdgeMask.c\n' \
                                                   '  composite/nodes/node_composite_ellipsemask.c\n' \
                                                   '  composite/nodes/node_composite_filter.c\n' \
                                                   '  composite/nodes/node_composite_flip.c\n' \
                                                   '  composite/nodes/node_composite_gamma.c\n' \
                                                   '  composite/nodes/node_composite_glare.c\n' \
                                                   '  composite/nodes/node_composite_hueSatVal.c\n' \
                                                   '  composite/nodes/node_composite_huecorrect.c\n' \
                                                   '  composite/nodes/node_composite_idMask.c\n' \
                                                   '  composite/nodes/node_composite_image.c\n' \
                                                   '  composite/nodes/node_composite_inpaint.c\n' \
                                                   '  composite/nodes/node_composite_invert.c\n' \
                                                   '  composite/nodes/node_composite_keying.c\n' \
                                                   '  composite/nodes/node_composite_keyingscreen.c\n' \
                                                   '  composite/nodes/node_composite_lensdist.c\n' \
                                                   '  composite/nodes/node_composite_levels.c\n' \
                                                   '  composite/nodes/node_composite_lummaMatte.c\n' \
                                                   '  composite/nodes/node_composite_mapRange.c\n' \
                                                   '  composite/nodes/node_composite_mapUV.c\n' \
                                                   '  composite/nodes/node_composite_mapValue.c\n' \
                                                   '  composite/nodes/node_composite_mask.c\n' \
                                                   '  composite/nodes/node_composite_math.c\n' \
                                                   '  composite/nodes/node_composite_mixrgb.c\n' \
                                                   '  composite/nodes/node_composite_movieclip.c\n' \
                                                   '  composite/nodes/node_composite_moviedistortion.c\n' \
                                                   '  composite/nodes/node_composite_normal.c\n' \
                                                   '  composite/nodes/node_composite_normalize.c\n' \
                                                   '  composite/nodes/node_composite_outputFile.c\n' \
                                                   '  composite/nodes/node_composite_pixelate.c\n' \
                                                   '  composite/nodes/node_composite_planetrackdeform.c\n' \
                                                   '  composite/nodes/node_composite_premulkey.c\n' \
                                                   '  composite/nodes/node_composite_rgb.c\n' \
                                                   '  composite/nodes/node_composite_rotate.c\n' \
                                                   '  composite/nodes/node_composite_scale.c\n' \
                                                   '  composite/nodes/node_composite_sepcombHSVA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombRGBA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombYCCA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombYUVA.c\n' \
                                                   '  composite/nodes/node_composite_setalpha.c\n' \
                                                   '  composite/nodes/node_composite_splitViewer.c\n' \
                                                   '  composite/nodes/node_composite_stabilize2d.c\n' \
                                                   '  composite/nodes/node_composite_sunbeams.c\n' \
                                                   '  composite/nodes/node_composite_switch.c\n' \
                                                   '  composite/nodes/node_composite_switchview.c\n' \
                                                   '  composite/nodes/node_composite_texture.c\n' \
                                                   '  composite/nodes/node_composite_tonemap.c\n' \
                                                   '  composite/nodes/node_composite_trackpos.c\n' \
                                                   '  composite/nodes/node_composite_transform.c\n' \
                                                   '  composite/nodes/node_composite_translate.c\n' \
                                                   '  composite/nodes/node_composite_valToRgb.c\n' \
                                                   '  composite/nodes/node_composite_value.c\n' \
                                                   '  composite/nodes/node_composite_vecBlur.c\n' \
                                                   '  composite/nodes/node_composite_viewer.c\n' \
                                                   '  composite/nodes/node_composite_zcombine.c\n' \
                                                   '\n'
                                                   '  composite/node_composite_tree.c\n' \
                                                   '  composite/node_composite_util.c\n' \
                                                   '\n'
                                                   '  shader/nodes/node_shader_add_shader.c\n' \
                                                   '  shader/nodes/node_shader_ambient_occlusion.c\n' \
                                                   '  shader/nodes/node_shader_attribute.c\n' \
                                                   '  shader/nodes/node_shader_background.c\n' \
                                                   '  shader/nodes/node_shader_bevel.c\n' \
                                                   '  shader/nodes/node_shader_blackbody.c\n' \
                                                   '  shader/nodes/node_shader_brightness.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_anisotropic.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_diffuse.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_glass.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_glossy.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_hair.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_hair_principled.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_principled.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_refraction.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_toon.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_translucent.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_transparent.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_velvet.c\n' \
                                                   '  shader/nodes/node_shader_bump.c\n' \
                                                   '  shader/nodes/node_shader_camera.c\n' \
                                                   '  shader/nodes/node_shader_clamp.c\n' \
                                                   '  shader/nodes/node_shader_common.c\n' \
                                                   '  shader/nodes/node_shader_curves.c\n' \
                                                   '  shader/nodes/node_shader_displacement.c\n' \
                                                   '  shader/nodes/node_shader_eevee_specular.c\n' \
                                                   '  shader/nodes/node_shader_emission.c\n' \
                                                   '  shader/nodes/node_shader_fresnel.c\n' \
                                                   '  shader/nodes/node_shader_gamma.c\n' \
                                                   '  shader/nodes/node_shader_geometry.c\n' \
                                                   '  shader/nodes/node_shader_hair_info.c\n' \
                                                   '  shader/nodes/node_shader_holdout.c\n' \
                                                   '  shader/nodes/node_shader_hueSatVal.c\n' \
                                                   '  shader/nodes/node_shader_ies_light.c\n' \
                                                   '  shader/nodes/node_shader_invert.c\n' \
                                                   '  shader/nodes/node_shader_layer_weight.c\n' \
                                                   '  shader/nodes/node_shader_light_falloff.c\n' \
                                                   '  shader/nodes/node_shader_light_path.c\n' \
                                                   '  shader/nodes/node_shader_map_range.c\n' \
                                                   '  shader/nodes/node_shader_mapping.c\n' \
                                                   '  shader/nodes/node_shader_math.c\n' \
                                                   '  shader/nodes/node_shader_mixRgb.c\n' \
                                                   '  shader/nodes/node_shader_mix_shader.c\n' \
                                                   '  shader/nodes/node_shader_normal.c\n' \
                                                   '  shader/nodes/node_shader_normal_map.c\n' \
                                                   '  shader/nodes/node_shader_object_info.c\n' \
                                                   '  shader/nodes/node_shader_output_aov.c\n' \
                                                   '  shader/nodes/node_shader_output_light.c\n' \
                                                   '  shader/nodes/node_shader_output_linestyle.c\n' \
                                                   '  shader/nodes/node_shader_output_material.c\n' \
                                                   '  shader/nodes/node_shader_output_world.c\n' \
                                                   '  shader/nodes/node_shader_particle_info.c\n' \
                                                   '  shader/nodes/node_shader_rgb.c\n' \
                                                   '  shader/nodes/node_shader_script.c\n' \
                                                   '  shader/nodes/node_shader_sepcombHSV.c\n' \
                                                   '  shader/nodes/node_shader_sepcombRGB.c\n' \
                                                   '  shader/nodes/node_shader_sepcombXYZ.c\n' \
                                                   '  shader/nodes/node_shader_shaderToRgb.c\n' \
                                                   '  shader/nodes/node_shader_squeeze.c\n' \
                                                   '  shader/nodes/node_shader_subsurface_scattering.c\n' \
                                                   '  shader/nodes/node_shader_tangent.c\n' \
                                                   '  shader/nodes/node_shader_tex_brick.c\n' \
                                                   '  shader/nodes/node_shader_tex_checker.c\n' \
                                                   '  shader/nodes/node_shader_tex_coord.c\n' \
                                                   '  shader/nodes/node_shader_tex_environment.c\n' \
                                                   '  shader/nodes/node_shader_tex_gradient.c\n' \
                                                   '  shader/nodes/node_shader_tex_image.c\n' \
                                                   '  shader/nodes/node_shader_tex_magic.c\n' \
                                                   '  shader/nodes/node_shader_tex_musgrave.c\n' \
                                                   '  shader/nodes/node_shader_tex_noise.c\n' \
                                                   '  shader/nodes/node_shader_tex_pointdensity.c\n' \
                                                   '  shader/nodes/node_shader_tex_sky.c\n' \
                                                   '  shader/nodes/node_shader_tex_truchet.c\n' \
                                                   '  shader/nodes/node_shader_tex_voronoi.c\n' \
                                                   '  shader/nodes/node_shader_tex_wave.c\n' \
                                                   '  shader/nodes/node_shader_tex_white_noise.c\n' \
                                                   '  shader/nodes/node_shader_uvAlongStroke.c\n' \
                                                   '  shader/nodes/node_shader_uvmap.c\n' \
                                                   '  shader/nodes/node_shader_valToRgb.c\n' \
                                                   '  shader/nodes/node_shader_value.c\n' \
                                                   '  shader/nodes/node_shader_vectTransform.c\n' \
                                                   '  shader/nodes/node_shader_vector_displacement.c\n' \
                                                   '  shader/nodes/node_shader_vector_math.c\n' \
                                                   '  shader/nodes/node_shader_vertex_color.c\n' \
                                                   '  shader/nodes/node_shader_volume_absorption.c\n' \
                                                   '  shader/nodes/node_shader_volume_info.c\n' \
                                                   '  shader/nodes/node_shader_volume_principled.c\n' \
                                                   '  shader/nodes/node_shader_volume_scatter.c\n' \
                                                   '  shader/nodes/node_shader_wavelength.c\n' \
                                                   '  shader/nodes/node_shader_wireframe.c\n' \
                                                   '  shader/node_shader_tree.c\n' \
                                                   '  shader/node_shader_util.c\n' \
                                                   '\n'
                                                   '  texture/nodes/node_texture_at.c\n' \
                                                   '  texture/nodes/node_texture_bricks.c\n' \
                                                   '  texture/nodes/node_texture_checker.c\n' \
                                                   '  texture/nodes/node_texture_common.c\n' \
                                                   '  texture/nodes/node_texture_compose.c\n' \
                                                   '  texture/nodes/node_texture_coord.c\n' \
                                                   '  texture/nodes/node_texture_curves.c\n' \
                                                   '  texture/nodes/node_texture_decompose.c\n' \
                                                   '  texture/nodes/node_texture_distance.c\n' \
                                                   '  texture/nodes/node_texture_hueSatVal.c\n' \
                                                   '  texture/nodes/node_texture_image.c\n' \
                                                   '  texture/nodes/node_texture_invert.c\n' \
                                                   '  texture/nodes/node_texture_math.c\n' \
                                                   '  texture/nodes/node_texture_mixRgb.c\n' \
                                                   '  texture/nodes/node_texture_output.c\n' \
                                                   '  texture/nodes/node_texture_proc.c\n' \
                                                   '  texture/nodes/node_texture_rotate.c\n' \
                                                   '  texture/nodes/node_texture_scale.c\n' \
                                                   '  texture/nodes/node_texture_texture.c\n' \
                                                   '  texture/nodes/node_texture_translate.c\n' \
                                                   '  texture/nodes/node_texture_valToNor.c\n' \
                                                   '  texture/nodes/node_texture_valToRgb.c\n' \
                                                   '  texture/nodes/node_texture_viewer.c\n' \
                                                   '  texture/node_texture_tree.c\n' \
                                                   '  texture/node_texture_util.c\n' \
                                                   '\n'
                                                   '  intern/node_common.c\n' \
                                                   '  intern/node_exec.c\n' \
                                                   '  intern/node_socket.c\n' \
                                                   '  intern/node_util.c\n' \
                                                   '\n'
                                                   '  composite/node_composite_util.h\n' \
                                                   '  shader/node_shader_util.h\n' \
                                                   '  texture/node_texture_util.h\n' \
                                                   '\n'
                                                   '  NOD_common.h\n' \
                                                   '  NOD_composite.h\n' \
                                                   '  NOD_shader.h\n' \
                                                   '  NOD_socket.h\n' \
                                                   '  NOD_static_types.h\n' \
                                                   '  NOD_texture.h\n' \
                                                   '  intern/node_common.h\n' \
                                                   '  intern/node_exec.h\n' \
                                                   '  intern/node_util.h\n' \
                                                   ')\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_node()
            self.assertTrue('  shader/nodes/node_shader_node_name.c' in mf.mock_calls[-3][1][0])

    def test_write_node_cmake_texture_node_correct_formatting(self):
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.type_suffix.return_value = 'texture'
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        with patch('builtins.open', mock.mock_open(read_data=
                                                   'set(SRC\n'
                                                   '  composite/nodes/node_composite_alphaOver.c\n' \
                                                   '  composite/nodes/node_composite_bilateralblur.c\n' \
                                                   '  composite/nodes/node_composite_blur.c\n' \
                                                   '  composite/nodes/node_composite_bokehblur.c\n' \
                                                   '  composite/nodes/node_composite_bokehimage.c\n' \
                                                   '  composite/nodes/node_composite_boxmask.c\n' \
                                                   '  composite/nodes/node_composite_brightness.c\n' \
                                                   '  composite/nodes/node_composite_channelMatte.c\n' \
                                                   '  composite/nodes/node_composite_chromaMatte.c\n' \
                                                   '  composite/nodes/node_composite_colorMatte.c\n' \
                                                   '  composite/nodes/node_composite_colorSpill.c\n' \
                                                   '  composite/nodes/node_composite_colorbalance.c\n' \
                                                   '  composite/nodes/node_composite_colorcorrection.c\n' \
                                                   '  composite/nodes/node_composite_common.c\n' \
                                                   '  composite/nodes/node_composite_composite.c\n' \
                                                   '  composite/nodes/node_composite_cornerpin.c\n' \
                                                   '  composite/nodes/node_composite_crop.c\n' \
                                                   '  composite/nodes/node_composite_cryptomatte.c\n' \
                                                   '  composite/nodes/node_composite_curves.c\n' \
                                                   '  composite/nodes/node_composite_defocus.c\n' \
                                                   '  composite/nodes/node_composite_denoise.c\n' \
                                                   '  composite/nodes/node_composite_despeckle.c\n' \
                                                   '  composite/nodes/node_composite_diffMatte.c\n' \
                                                   '  composite/nodes/node_composite_dilate.c\n' \
                                                   '  composite/nodes/node_composite_directionalblur.c\n' \
                                                   '  composite/nodes/node_composite_displace.c\n' \
                                                   '  composite/nodes/node_composite_distanceMatte.c\n' \
                                                   '  composite/nodes/node_composite_doubleEdgeMask.c\n' \
                                                   '  composite/nodes/node_composite_ellipsemask.c\n' \
                                                   '  composite/nodes/node_composite_filter.c\n' \
                                                   '  composite/nodes/node_composite_flip.c\n' \
                                                   '  composite/nodes/node_composite_gamma.c\n' \
                                                   '  composite/nodes/node_composite_glare.c\n' \
                                                   '  composite/nodes/node_composite_hueSatVal.c\n' \
                                                   '  composite/nodes/node_composite_huecorrect.c\n' \
                                                   '  composite/nodes/node_composite_idMask.c\n' \
                                                   '  composite/nodes/node_composite_image.c\n' \
                                                   '  composite/nodes/node_composite_inpaint.c\n' \
                                                   '  composite/nodes/node_composite_invert.c\n' \
                                                   '  composite/nodes/node_composite_keying.c\n' \
                                                   '  composite/nodes/node_composite_keyingscreen.c\n' \
                                                   '  composite/nodes/node_composite_lensdist.c\n' \
                                                   '  composite/nodes/node_composite_levels.c\n' \
                                                   '  composite/nodes/node_composite_lummaMatte.c\n' \
                                                   '  composite/nodes/node_composite_mapRange.c\n' \
                                                   '  composite/nodes/node_composite_mapUV.c\n' \
                                                   '  composite/nodes/node_composite_mapValue.c\n' \
                                                   '  composite/nodes/node_composite_mask.c\n' \
                                                   '  composite/nodes/node_composite_math.c\n' \
                                                   '  composite/nodes/node_composite_mixrgb.c\n' \
                                                   '  composite/nodes/node_composite_movieclip.c\n' \
                                                   '  composite/nodes/node_composite_moviedistortion.c\n' \
                                                   '  composite/nodes/node_composite_normal.c\n' \
                                                   '  composite/nodes/node_composite_normalize.c\n' \
                                                   '  composite/nodes/node_composite_outputFile.c\n' \
                                                   '  composite/nodes/node_composite_pixelate.c\n' \
                                                   '  composite/nodes/node_composite_planetrackdeform.c\n' \
                                                   '  composite/nodes/node_composite_premulkey.c\n' \
                                                   '  composite/nodes/node_composite_rgb.c\n' \
                                                   '  composite/nodes/node_composite_rotate.c\n' \
                                                   '  composite/nodes/node_composite_scale.c\n' \
                                                   '  composite/nodes/node_composite_sepcombHSVA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombRGBA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombYCCA.c\n' \
                                                   '  composite/nodes/node_composite_sepcombYUVA.c\n' \
                                                   '  composite/nodes/node_composite_setalpha.c\n' \
                                                   '  composite/nodes/node_composite_splitViewer.c\n' \
                                                   '  composite/nodes/node_composite_stabilize2d.c\n' \
                                                   '  composite/nodes/node_composite_sunbeams.c\n' \
                                                   '  composite/nodes/node_composite_switch.c\n' \
                                                   '  composite/nodes/node_composite_switchview.c\n' \
                                                   '  composite/nodes/node_composite_texture.c\n' \
                                                   '  composite/nodes/node_composite_tonemap.c\n' \
                                                   '  composite/nodes/node_composite_trackpos.c\n' \
                                                   '  composite/nodes/node_composite_transform.c\n' \
                                                   '  composite/nodes/node_composite_translate.c\n' \
                                                   '  composite/nodes/node_composite_valToRgb.c\n' \
                                                   '  composite/nodes/node_composite_value.c\n' \
                                                   '  composite/nodes/node_composite_vecBlur.c\n' \
                                                   '  composite/nodes/node_composite_viewer.c\n' \
                                                   '  composite/nodes/node_composite_zcombine.c\n' \
                                                   '\n'
                                                   '  composite/node_composite_tree.c\n' \
                                                   '  composite/node_composite_util.c\n' \
                                                   '\n'
                                                   '  shader/nodes/node_shader_add_shader.c\n' \
                                                   '  shader/nodes/node_shader_ambient_occlusion.c\n' \
                                                   '  shader/nodes/node_shader_attribute.c\n' \
                                                   '  shader/nodes/node_shader_background.c\n' \
                                                   '  shader/nodes/node_shader_bevel.c\n' \
                                                   '  shader/nodes/node_shader_blackbody.c\n' \
                                                   '  shader/nodes/node_shader_brightness.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_anisotropic.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_diffuse.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_glass.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_glossy.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_hair.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_hair_principled.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_principled.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_refraction.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_toon.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_translucent.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_transparent.c\n' \
                                                   '  shader/nodes/node_shader_bsdf_velvet.c\n' \
                                                   '  shader/nodes/node_shader_bump.c\n' \
                                                   '  shader/nodes/node_shader_camera.c\n' \
                                                   '  shader/nodes/node_shader_clamp.c\n' \
                                                   '  shader/nodes/node_shader_common.c\n' \
                                                   '  shader/nodes/node_shader_curves.c\n' \
                                                   '  shader/nodes/node_shader_displacement.c\n' \
                                                   '  shader/nodes/node_shader_eevee_specular.c\n' \
                                                   '  shader/nodes/node_shader_emission.c\n' \
                                                   '  shader/nodes/node_shader_fresnel.c\n' \
                                                   '  shader/nodes/node_shader_gamma.c\n' \
                                                   '  shader/nodes/node_shader_geometry.c\n' \
                                                   '  shader/nodes/node_shader_hair_info.c\n' \
                                                   '  shader/nodes/node_shader_holdout.c\n' \
                                                   '  shader/nodes/node_shader_hueSatVal.c\n' \
                                                   '  shader/nodes/node_shader_ies_light.c\n' \
                                                   '  shader/nodes/node_shader_invert.c\n' \
                                                   '  shader/nodes/node_shader_layer_weight.c\n' \
                                                   '  shader/nodes/node_shader_light_falloff.c\n' \
                                                   '  shader/nodes/node_shader_light_path.c\n' \
                                                   '  shader/nodes/node_shader_map_range.c\n' \
                                                   '  shader/nodes/node_shader_mapping.c\n' \
                                                   '  shader/nodes/node_shader_math.c\n' \
                                                   '  shader/nodes/node_shader_mixRgb.c\n' \
                                                   '  shader/nodes/node_shader_mix_shader.c\n' \
                                                   '  shader/nodes/node_shader_normal.c\n' \
                                                   '  shader/nodes/node_shader_normal_map.c\n' \
                                                   '  shader/nodes/node_shader_object_info.c\n' \
                                                   '  shader/nodes/node_shader_output_aov.c\n' \
                                                   '  shader/nodes/node_shader_output_light.c\n' \
                                                   '  shader/nodes/node_shader_output_linestyle.c\n' \
                                                   '  shader/nodes/node_shader_output_material.c\n' \
                                                   '  shader/nodes/node_shader_output_world.c\n' \
                                                   '  shader/nodes/node_shader_particle_info.c\n' \
                                                   '  shader/nodes/node_shader_rgb.c\n' \
                                                   '  shader/nodes/node_shader_script.c\n' \
                                                   '  shader/nodes/node_shader_sepcombHSV.c\n' \
                                                   '  shader/nodes/node_shader_sepcombRGB.c\n' \
                                                   '  shader/nodes/node_shader_sepcombXYZ.c\n' \
                                                   '  shader/nodes/node_shader_shaderToRgb.c\n' \
                                                   '  shader/nodes/node_shader_squeeze.c\n' \
                                                   '  shader/nodes/node_shader_subsurface_scattering.c\n' \
                                                   '  shader/nodes/node_shader_tangent.c\n' \
                                                   '  shader/nodes/node_shader_tex_brick.c\n' \
                                                   '  shader/nodes/node_shader_tex_checker.c\n' \
                                                   '  shader/nodes/node_shader_tex_coord.c\n' \
                                                   '  shader/nodes/node_shader_tex_environment.c\n' \
                                                   '  shader/nodes/node_shader_tex_gradient.c\n' \
                                                   '  shader/nodes/node_shader_tex_image.c\n' \
                                                   '  shader/nodes/node_shader_tex_magic.c\n' \
                                                   '  shader/nodes/node_shader_tex_musgrave.c\n' \
                                                   '  shader/nodes/node_shader_tex_noise.c\n' \
                                                   '  shader/nodes/node_shader_tex_pointdensity.c\n' \
                                                   '  shader/nodes/node_shader_tex_sky.c\n' \
                                                   '  shader/nodes/node_shader_tex_truchet.c\n' \
                                                   '  shader/nodes/node_shader_tex_voronoi.c\n' \
                                                   '  shader/nodes/node_shader_tex_wave.c\n' \
                                                   '  shader/nodes/node_shader_tex_white_noise.c\n' \
                                                   '  shader/nodes/node_shader_uvAlongStroke.c\n' \
                                                   '  shader/nodes/node_shader_uvmap.c\n' \
                                                   '  shader/nodes/node_shader_valToRgb.c\n' \
                                                   '  shader/nodes/node_shader_value.c\n' \
                                                   '  shader/nodes/node_shader_vectTransform.c\n' \
                                                   '  shader/nodes/node_shader_vector_displacement.c\n' \
                                                   '  shader/nodes/node_shader_vector_math.c\n' \
                                                   '  shader/nodes/node_shader_vertex_color.c\n' \
                                                   '  shader/nodes/node_shader_volume_absorption.c\n' \
                                                   '  shader/nodes/node_shader_volume_info.c\n' \
                                                   '  shader/nodes/node_shader_volume_principled.c\n' \
                                                   '  shader/nodes/node_shader_volume_scatter.c\n' \
                                                   '  shader/nodes/node_shader_wavelength.c\n' \
                                                   '  shader/nodes/node_shader_wireframe.c\n' \
                                                   '  shader/node_shader_tree.c\n' \
                                                   '  shader/node_shader_util.c\n' \
                                                   '\n'
                                                   '  texture/nodes/node_texture_at.c\n' \
                                                   '  texture/nodes/node_texture_bricks.c\n' \
                                                   '  texture/nodes/node_texture_checker.c\n' \
                                                   '  texture/nodes/node_texture_common.c\n' \
                                                   '  texture/nodes/node_texture_compose.c\n' \
                                                   '  texture/nodes/node_texture_coord.c\n' \
                                                   '  texture/nodes/node_texture_curves.c\n' \
                                                   '  texture/nodes/node_texture_decompose.c\n' \
                                                   '  texture/nodes/node_texture_distance.c\n' \
                                                   '  texture/nodes/node_texture_hueSatVal.c\n' \
                                                   '  texture/nodes/node_texture_image.c\n' \
                                                   '  texture/nodes/node_texture_invert.c\n' \
                                                   '  texture/nodes/node_texture_math.c\n' \
                                                   '  texture/nodes/node_texture_mixRgb.c\n' \
                                                   '  texture/nodes/node_texture_output.c\n' \
                                                   '  texture/nodes/node_texture_proc.c\n' \
                                                   '  texture/nodes/node_texture_rotate.c\n' \
                                                   '  texture/nodes/node_texture_scale.c\n' \
                                                   '  texture/nodes/node_texture_texture.c\n' \
                                                   '  texture/nodes/node_texture_translate.c\n' \
                                                   '  texture/nodes/node_texture_valToNor.c\n' \
                                                   '  texture/nodes/node_texture_valToRgb.c\n' \
                                                   '  texture/nodes/node_texture_viewer.c\n' \
                                                   '  texture/node_texture_tree.c\n' \
                                                   '  texture/node_texture_util.c\n' \
                                                   '\n'
                                                   '  intern/node_common.c\n' \
                                                   '  intern/node_exec.c\n' \
                                                   '  intern/node_socket.c\n' \
                                                   '  intern/node_util.c\n' \
                                                   '\n'
                                                   '  composite/node_composite_util.h\n' \
                                                   '  shader/node_shader_util.h\n' \
                                                   '  texture/node_texture_util.h\n' \
                                                   '\n'
                                                   '  NOD_common.h\n' \
                                                   '  NOD_composite.h\n' \
                                                   '  NOD_shader.h\n' \
                                                   '  NOD_socket.h\n' \
                                                   '  NOD_static_types.h\n' \
                                                   '  NOD_texture.h\n' \
                                                   '  intern/node_common.h\n' \
                                                   '  intern/node_exec.h\n' \
                                                   '  intern/node_util.h\n' \
                                                   ')\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_node()
            self.assertTrue('  shader/nodes/node_shader_tex_node_name.c' in mf.mock_calls[-3][1][0])

    def test_write_glsl_cmake_correct_formatting(self):
        with patch('builtins.open', mock.mock_open(read_data=
                                                   'endif()\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_depth_only_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_checker_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_diag_stripes_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_smooth_color_alpha_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_color_alpha_test_0_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_id_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_area_borders_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_area_borders_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_base_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_base_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_shadow_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_shadow_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_nodelink_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_nodelink_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_flat_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_line_dashed_uniform_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_line_dashed_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_dithered_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_rect_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_multi_rect_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_desaturate_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_linear_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_shuffle_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_mask_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_modulate_alpha_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_alpha_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_varying_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_depth_linear_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_depth_copy_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_interlace_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_multisample_resolve_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_image_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_normal_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_flat_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_line_dashed_uniform_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_normal_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_passthrough_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_clipped_uniform_color_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_instance_variying_size_variying_color_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_varying_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_fixed_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_varying_size_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_varying_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_uniform_size_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_uniform_size_outline_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_varying_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_outline_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_varying_color_outline_aa_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_points_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_facedots_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_edges_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_faces_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_stretch_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_text_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_text_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_keyframe_diamond_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_keyframe_diamond_frag.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_geometry.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_add_shader.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_ambient_occlusion.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_anisotropic.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_attribute.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_background.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bevel.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_blackbody.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bright_contrast.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bump.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_camera.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_clamp.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_color_ramp.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_color_util.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_hsv.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_xyz.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_diffuse.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_displacement.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_eevee_specular.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_emission.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_fractal_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_fresnel.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_gamma.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_geometry.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_glass.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_glossy.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hair_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hash.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_holdout.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hue_sat_val.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_invert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_layer_weight.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_light_falloff.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_light_path.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mapping.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_map_range.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_math.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_math_util.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mix_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mix_shader.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_normal.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_normal_map.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_object_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_output_material.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_output_world.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_particle_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_principled.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_refraction.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_rgb_curves.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_rgb_to_bw.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_hsv.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_xyz.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_set.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_shader_to_rgba.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_squeeze.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_subsurface_scattering.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tangent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_brick.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_checker.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_environment.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_gradient.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_image.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_magic.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_musgrave.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_sky.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_truchet.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_texture_coordinates.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_voronoi.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_wave.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_white_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_toon.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_translucent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_transparent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_uv_map.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_curves.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_displacement.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_math.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_velvet.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vertex_color.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_absorption.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_principled.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_scatter.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_wireframe.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_world_normals.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_geom.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_fill_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_fill_frag.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_cfg_world_clip_lib.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_common_obinfos_lib.glsl SRC)\n' \
                                                   '\n' \
                                                   'if (WITH_MOD_FLUID)\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_glsl()

            self.assertTrue(
                'data_to_c_simple(shaders/material/gpu_shader_material_node_name.glsl SRC)\n' in mf.mock_calls[-3][1][
                    0])

    def test_write_glsl_cmake_texture_node_correct_formatting(self):
        self.mock_gui.is_texture_node.return_value = True
        self.mock_gui.type_suffix.return_value = 'texture'
        self.mock_gui.type_suffix_abbreviated.return_value = 'tex'
        with patch('builtins.open', mock.mock_open(read_data=
                                                   'endif()\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_depth_only_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_checker_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_diag_stripes_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_simple_lighting_smooth_color_alpha_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_color_alpha_test_0_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_flat_id_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_area_borders_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_area_borders_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_base_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_base_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_shadow_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_widget_shadow_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_nodelink_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_nodelink_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_flat_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_line_dashed_uniform_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_line_dashed_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_smooth_color_dithered_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_rect_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_image_multi_rect_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_desaturate_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_linear_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_shuffle_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_mask_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_modulate_alpha_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_alpha_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_varying_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_depth_linear_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_depth_copy_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_interlace_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_image_multisample_resolve_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_image_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_normal_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_flat_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_line_dashed_uniform_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_normal_smooth_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_smooth_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_passthrough_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_clipped_uniform_color_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_instance_variying_size_variying_color_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_uniform_color_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_varying_outline_aa_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_point_varying_color_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_fixed_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_varying_size_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_varying_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_uniform_size_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_3D_point_uniform_size_outline_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_varying_size_varying_color_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_outline_aa_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_point_uniform_size_varying_color_outline_aa_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_points_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_facedots_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_edges_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_faces_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_2D_edituvs_stretch_vert.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_text_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_text_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_keyframe_diamond_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_keyframe_diamond_frag.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_geometry.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_add_shader.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_ambient_occlusion.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_anisotropic.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_attribute.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_background.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bevel.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_blackbody.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bright_contrast.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_bump.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_camera.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_clamp.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_color_ramp.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_color_util.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_hsv.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_combine_xyz.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_diffuse.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_displacement.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_eevee_specular.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_emission.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_fractal_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_fresnel.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_gamma.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_geometry.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_glass.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_glossy.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hair_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hash.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_holdout.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_hue_sat_val.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_invert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_layer_weight.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_light_falloff.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_light_path.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mapping.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_map_range.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_math.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_math_util.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mix_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_mix_shader.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_normal.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_normal_map.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_object_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_output_material.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_output_world.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_particle_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_principled.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_refraction.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_rgb_curves.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_rgb_to_bw.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_hsv.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_rgb.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_separate_xyz.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_set.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_shader_to_rgba.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_squeeze.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_subsurface_scattering.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tangent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_brick.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_checker.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_environment.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_gradient.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_image.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_magic.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_musgrave.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_sky.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_truchet.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_texture_coordinates.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_voronoi.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_wave.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_tex_white_noise.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_toon.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_translucent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_transparent.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_uv_map.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_curves.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_displacement.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vector_math.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_velvet.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_vertex_color.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_absorption.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_info.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_principled.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_volume_scatter.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_wireframe.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/material/gpu_shader_material_world_normals.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_frag.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_stroke_geom.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_fill_vert.glsl SRC)\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_gpencil_fill_frag.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_cfg_world_clip_lib.glsl SRC)\n' \
                                                   '\n' \
                                                   'data_to_c_simple(shaders/gpu_shader_common_obinfos_lib.glsl SRC)\n' \
                                                   '\n' \
                                                   'if (WITH_MOD_FLUID)\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_glsl()

            self.assertTrue('data_to_c_simple(shaders/material/gpu_shader_material_tex_node_name.glsl SRC)\n' in
                            mf.mock_calls[-3][1][0])


if __name__ == '__main__':
    unittest.main()
