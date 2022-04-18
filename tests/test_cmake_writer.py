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

    # def test_insert_cmake_middle_sorted_path_correct_formatting(self):
    #     """Insert a path which alphabetically will fall in the middle of the file list"""
    #     cmake = self._create_default_cmake_manager()
    #     file_text = 'closure/bsdf_principled_sheen.h\n' \
    #                 '  closure/bsdf_hair_principled.h\n' \
    #                 ')\n' \
    #                 '\n' \
    #                 'set(SRC_KERNEL_SVM_HEADERS\n' \
    #                 '  svm/svm.h\n' \
    #                 '  svm/ao.h\n' \
    #                 '  svm/aov.h\n' \
    #                 '  svm/attribute.h\n' \
    #                 '  svm/bevel.h\n' \
    #                 '  svm/blackbody.h\n' \
    #                 '  svm/bump.h\n' \
    #                 '  svm/camera.h\n' \
    #                 '  svm/clamp.h\n' \
    #                 '  svm/closure.h\n' \
    #                 '  svm/convert.h\n' \
    #                 '  svm/checker.h\n' \
    #                 '  svm/color_util.h\n' \
    #                 '  svm/brick.h\n' \
    #                 '  svm/displace.h\n' \
    #                 '  svm/fresnel.h\n' \
    #                 '  svm/wireframe.h\n' \
    #                 '  svm/wavelength.h\n' \
    #                 '  svm/gamma.h\n' \
    #                 '  svm/brightness.h\n' \
    #                 '  svm/geometry.h\n' \
    #                 '  svm/gradient.h\n' \
    #                 '  svm/hsv.h\n' \
    #                 '  svm/ies.h\n' \
    #                 '  svm/image.h\n' \
    #                 '  svm/invert.h\n' \
    #                 '  svm/light_path.h\n' \
    #                 '  svm/magic.h\n' \
    #                 '  svm/map_range.h\n' \
    #                 '  svm/mapping.h\n' \
    #                 '  svm/mapping_util.h\n' \
    #                 '  svm/math.h\n' \
    #                 '  svm/math_util.h\n' \
    #                 '  svm/mix.h\n' \
    #                 '  svm/musgrave.h\n' \
    #                 '  svm/noise.h\n' \
    #                 '  svm/noisetex.h\n' \
    #                 '  svm/normal.h\n' \
    #                 '  svm/ramp.h\n' \
    #                 '  svm/ramp_util.h\n' \
    #                 '  svm/sepcomb_hsv.h\n' \
    #                 '  svm/sepcomb_vector.h\n' \
    #                 '  svm/sky.h\n' \
    #                 '  svm/tex_coord.h\n' \
    #                 '  svm/truchet.h\n' \
    #                 '  svm/fractal_noise.h\n' \
    #                 '  svm/types.h\n' \
    #                 '  svm/value.h\n' \
    #                 '  svm/vector_transform.h\n' \
    #                 '  svm/voronoi.h\n' \
    #                 '  svm/voxel.h\n' \
    #                 '  svm/wave.h\n' \
    #                 '  svm/white_noise.h\n' \
    #                 '  svm/vertex_color.h\n' \
    #                 ')\n' \
    #                 '\n' \
    #                 'set(SRC_GEOM_HEADERS\n'
    #     text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
    #                                              ')\n\n'
    #                                              'set(SRC_KERNEL_SVM_HEADERS)'), file_text, '  svm/node_name.h')

    #     self.assertTrue('  svm/fresnel.h\n'
    #                     '  svm/node_name.h\n'
    #                     '  svm/wireframe.h\n' in text)

    def test_insert_cmake_first_sorted_path_correct_formatting(self):
        """Insert a path which alphabetically will fall at the start of the file list"""
        cmake = self._create_default_cmake_manager()
        file_text = 'closure/bsdf_principled_sheen.h\n' \
                    '  closure/bsdf_hair_principled.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_KERNEL_SVM_HEADERS\n' \
                    '  svm/svm.h\n' \
                    '  svm/ao.h\n' \
                    '  svm/aov.h\n' \
                    '  svm/attribute.h\n' \
                    '  svm/bevel.h\n' \
                    '  svm/blackbody.h\n' \
                    '  svm/bump.h\n' \
                    '  svm/camera.h\n' \
                    '  svm/clamp.h\n' \
                    '  svm/closure.h\n' \
                    '  svm/convert.h\n' \
                    '  svm/checker.h\n' \
                    '  svm/color_util.h\n' \
                    '  svm/brick.h\n' \
                    '  svm/displace.h\n' \
                    '  svm/fresnel.h\n' \
                    '  svm/wireframe.h\n' \
                    '  svm/wavelength.h\n' \
                    '  svm/gamma.h\n' \
                    '  svm/brightness.h\n' \
                    '  svm/geometry.h\n' \
                    '  svm/gradient.h\n' \
                    '  svm/hsv.h\n' \
                    '  svm/ies.h\n' \
                    '  svm/image.h\n' \
                    '  svm/invert.h\n' \
                    '  svm/light_path.h\n' \
                    '  svm/magic.h\n' \
                    '  svm/map_range.h\n' \
                    '  svm/mapping.h\n' \
                    '  svm/mapping_util.h\n' \
                    '  svm/math.h\n' \
                    '  svm/math_util.h\n' \
                    '  svm/mix.h\n' \
                    '  svm/musgrave.h\n' \
                    '  svm/noise.h\n' \
                    '  svm/noisetex.h\n' \
                    '  svm/normal.h\n' \
                    '  svm/ramp.h\n' \
                    '  svm/ramp_util.h\n' \
                    '  svm/sepcomb_hsv.h\n' \
                    '  svm/sepcomb_vector.h\n' \
                    '  svm/sky.h\n' \
                    '  svm/tex_coord.h\n' \
                    '  svm/truchet.h\n' \
                    '  svm/fractal_noise.h\n' \
                    '  svm/types.h\n' \
                    '  svm/value.h\n' \
                    '  svm/vector_transform.h\n' \
                    '  svm/voronoi.h\n' \
                    '  svm/voxel.h\n' \
                    '  svm/wave.h\n' \
                    '  svm/white_noise.h\n' \
                    '  svm/vertex_color.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_GEOM_HEADERS\n'
        text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
                                                 ')\n\n'
                                                 'set(SRC_KERNEL_SVM_HEADERS)'), file_text, '  a')

        self.assertTrue('  a\n'
                        '  svm/svm.h\n' in text)

    def test_insert_cmake_last_sorted_path_correct_formatting(self):
        """Insert a path which alphabetically will fall at the end of the file list"""
        cmake = self._create_default_cmake_manager()
        file_text = 'closure/bsdf_principled_sheen.h\n' \
                    '  closure/bsdf_hair_principled.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_KERNEL_SVM_HEADERS\n' \
                    '  svm/svm.h\n' \
                    '  svm/ao.h\n' \
                    '  svm/aov.h\n' \
                    '  svm/attribute.h\n' \
                    '  svm/bevel.h\n' \
                    '  svm/blackbody.h\n' \
                    '  svm/bump.h\n' \
                    '  svm/camera.h\n' \
                    '  svm/clamp.h\n' \
                    '  svm/closure.h\n' \
                    '  svm/convert.h\n' \
                    '  svm/checker.h\n' \
                    '  svm/color_util.h\n' \
                    '  svm/brick.h\n' \
                    '  svm/displace.h\n' \
                    '  svm/fresnel.h\n' \
                    '  svm/wireframe.h\n' \
                    '  svm/wavelength.h\n' \
                    '  svm/gamma.h\n' \
                    '  svm/brightness.h\n' \
                    '  svm/geometry.h\n' \
                    '  svm/gradient.h\n' \
                    '  svm/hsv.h\n' \
                    '  svm/ies.h\n' \
                    '  svm/image.h\n' \
                    '  svm/invert.h\n' \
                    '  svm/light_path.h\n' \
                    '  svm/magic.h\n' \
                    '  svm/map_range.h\n' \
                    '  svm/mapping.h\n' \
                    '  svm/mapping_util.h\n' \
                    '  svm/math.h\n' \
                    '  svm/math_util.h\n' \
                    '  svm/mix.h\n' \
                    '  svm/musgrave.h\n' \
                    '  svm/noise.h\n' \
                    '  svm/noisetex.h\n' \
                    '  svm/normal.h\n' \
                    '  svm/ramp.h\n' \
                    '  svm/ramp_util.h\n' \
                    '  svm/sepcomb_hsv.h\n' \
                    '  svm/sepcomb_vector.h\n' \
                    '  svm/sky.h\n' \
                    '  svm/tex_coord.h\n' \
                    '  svm/truchet.h\n' \
                    '  svm/fractal_noise.h\n' \
                    '  svm/types.h\n' \
                    '  svm/value.h\n' \
                    '  svm/vector_transform.h\n' \
                    '  svm/voronoi.h\n' \
                    '  svm/voxel.h\n' \
                    '  svm/wave.h\n' \
                    '  svm/white_noise.h\n' \
                    '  svm/vertex_color.h\n' \
                    ')\n' \
                    '\n' \
                    'set(SRC_GEOM_HEADERS\n'
        text = cmake._insert_cmake_file_path(len('closure/bsdf_principled_sheen.h\n  closure/bsdf_hair_principled.h\n'
                                                 ')\n\n'
                                                 'set(SRC_KERNEL_SVM_HEADERS)'), file_text, '  z')

        self.assertTrue('  svm/vertex_color.h\n'
                        '  z\n' in text)

    # def test_write_cmake_middle_sorted_name_correct_formatting(self):
    #     """Insert a name which alphabetically will fall in the middle of the file list"""
    #     with patch('builtins.open', mock.mock_open(read_data=
    #                                                'closure/bsdf_principled_sheen.h\n'
    #                                                '  closure/bsdf_hair_principled.h\n'
    #                                                ')\n'
    #                                                '\n'
    #                                                'set(SRC_KERNEL_SVM_HEADERS\n'
    #                                                '  svm/svm.h\n'
    #                                                '  svm/ao.h\n'
    #                                                '  svm/aov.h\n'
    #                                                '  svm/attribute.h\n'
    #                                                '  svm/bevel.h\n'
    #                                                '  svm/blackbody.h\n'
    #                                                '  svm/bump.h\n'
    #                                                '  svm/camera.h\n'
    #                                                '  svm/clamp.h\n'
    #                                                '  svm/closure.h\n'
    #                                                '  svm/convert.h\n'
    #                                                '  svm/checker.h\n'
    #                                                '  svm/color_util.h\n'
    #                                                '  svm/brick.h\n'
    #                                                '  svm/displace.h\n'
    #                                                '  svm/fresnel.h\n'
    #                                                '  svm/wireframe.h\n'
    #                                                '  svm/wavelength.h\n'
    #                                                '  svm/gamma.h\n'
    #                                                '  svm/brightness.h\n'
    #                                                '  svm/geometry.h\n'
    #                                                '  svm/gradient.h\n'
    #                                                '  svm/hsv.h\n'
    #                                                '  svm/ies.h\n'
    #                                                '  svm/image.h\n'
    #                                                '  svm/invert.h\n'
    #                                                '  svm/light_path.h\n'
    #                                                '  svm/magic.h\n'
    #                                                '  svm/map_range.h\n'
    #                                                '  svm/mapping.h\n'
    #                                                '  svm/mapping_util.h\n'
    #                                                '  svm/math.h\n'
    #                                                '  svm/math_util.h\n'
    #                                                '  svm/mix.h\n'
    #                                                '  svm/musgrave.h\n'
    #                                                '  svm/noise.h\n'
    #                                                '  svm/noisetex.h\n'
    #                                                '  svm/normal.h\n'
    #                                                '  svm/ramp.h\n'
    #                                                '  svm/ramp_util.h\n'
    #                                                '  svm/sepcomb_hsv.h\n'
    #                                                '  svm/sepcomb_vector.h\n'
    #                                                '  svm/sky.h\n'
    #                                                '  svm/tex_coord.h\n'
    #                                                '  svm/truchet.h\n'
    #                                                '  svm/fractal_noise.h\n'
    #                                                '  svm/types.h\n'
    #                                                '  svm/value.h\n'
    #                                                '  svm/vector_transform.h\n'
    #                                                '  svm/voronoi.h\n'
    #                                                '  svm/voxel.h\n'
    #                                                '  svm/wave.h\n'
    #                                                '  svm/white_noise.h\n'
    #                                                '  svm/vertex_color.h\n'
    #                                                ')\n'
    #                                                '\n'
    #                                                'set(SRC_GEOM_HEADERS\n')) as mf:
    #         cmake = self._create_default_cmake_manager()
    #         cmake._add_svm()

    #         self.assertTrue('  svm/fresnel.h\n'
    #                         '  svm/node_name.h\n'
    #                         '  svm/wireframe.h\n' in mf.mock_calls[-3][1][0])

    # def test_write_cmake_first_sorted_name_correct_formatting(self):
    #     """Insert a name which alphabetically will fall at the start of the file list"""
    #     self.mock_gui.get_node_name.return_value = 'a'
    #     with patch('builtins.open', mock.mock_open(read_data=
    #                                                'closure/bsdf_principled_sheen.h\n'
    #                                                '  closure/bsdf_hair_principled.h\n'
    #                                                ')\n'
    #                                                '\n'
    #                                                'set(SRC_KERNEL_SVM_HEADERS\n'
    #                                                '  svm/svm.h\n'
    #                                                '  svm/ao.h\n'
    #                                                '  svm/aov.h\n'
    #                                                '  svm/attribute.h\n'
    #                                                '  svm/bevel.h\n'
    #                                                '  svm/blackbody.h\n'
    #                                                '  svm/bump.h\n'
    #                                                '  svm/camera.h\n'
    #                                                '  svm/clamp.h\n'
    #                                                '  svm/closure.h\n'
    #                                                '  svm/convert.h\n'
    #                                                '  svm/checker.h\n'
    #                                                '  svm/color_util.h\n'
    #                                                '  svm/brick.h\n'
    #                                                '  svm/displace.h\n'
    #                                                '  svm/fresnel.h\n'
    #                                                '  svm/wireframe.h\n'
    #                                                '  svm/wavelength.h\n'
    #                                                '  svm/gamma.h\n'
    #                                                '  svm/brightness.h\n'
    #                                                '  svm/geometry.h\n'
    #                                                '  svm/gradient.h\n'
    #                                                '  svm/hsv.h\n'
    #                                                '  svm/ies.h\n'
    #                                                '  svm/image.h\n'
    #                                                '  svm/invert.h\n'
    #                                                '  svm/light_path.h\n'
    #                                                '  svm/magic.h\n'
    #                                                '  svm/map_range.h\n'
    #                                                '  svm/mapping.h\n'
    #                                                '  svm/mapping_util.h\n'
    #                                                '  svm/math.h\n'
    #                                                '  svm/math_util.h\n'
    #                                                '  svm/mix.h\n'
    #                                                '  svm/musgrave.h\n'
    #                                                '  svm/noise.h\n'
    #                                                '  svm/noisetex.h\n'
    #                                                '  svm/normal.h\n'
    #                                                '  svm/ramp.h\n'
    #                                                '  svm/ramp_util.h\n'
    #                                                '  svm/sepcomb_hsv.h\n'
    #                                                '  svm/sepcomb_vector.h\n'
    #                                                '  svm/sky.h\n'
    #                                                '  svm/tex_coord.h\n'
    #                                                '  svm/truchet.h\n'
    #                                                '  svm/fractal_noise.h\n'
    #                                                '  svm/types.h\n'
    #                                                '  svm/value.h\n'
    #                                                '  svm/vector_transform.h\n'
    #                                                '  svm/voronoi.h\n'
    #                                                '  svm/voxel.h\n'
    #                                                '  svm/wave.h\n'
    #                                                '  svm/white_noise.h\n'
    #                                                '  svm/vertex_color.h\n'
    #                                                ')\n'
    #                                                '\n'
    #                                                'set(SRC_GEOM_HEADERS\n')) as mf:
    #         cmake = self._create_default_cmake_manager()
    #         cmake._add_svm()

    #         self.assertTrue('  svm/a.h\n'
    #                         '  svm/ao.h\n' in mf.mock_calls[-3][1][0])

    def test_write_cmake_last_sorted_name_correct_formatting(self):
        """Insert a name which alphabetically will fall at the end of the file list"""
        self.mock_gui.get_node_name.return_value = 'z'
        with patch('builtins.open', mock.mock_open(read_data=
                                                   'closure/bsdf_principled_sheen.h\n'
                                                   '  closure/bsdf_hair_principled.h\n'
                                                   ')\n'
                                                   '\n'
                                                   'set(SRC_KERNEL_SVM_HEADERS\n'
                                                   '  svm/svm.h\n'
                                                   '  svm/ao.h\n'
                                                   '  svm/aov.h\n'
                                                   '  svm/attribute.h\n'
                                                   '  svm/bevel.h\n'
                                                   '  svm/blackbody.h\n'
                                                   '  svm/bump.h\n'
                                                   '  svm/camera.h\n'
                                                   '  svm/clamp.h\n'
                                                   '  svm/closure.h\n'
                                                   '  svm/convert.h\n'
                                                   '  svm/checker.h\n'
                                                   '  svm/color_util.h\n'
                                                   '  svm/brick.h\n'
                                                   '  svm/displace.h\n'
                                                   '  svm/fresnel.h\n'
                                                   '  svm/wireframe.h\n'
                                                   '  svm/wavelength.h\n'
                                                   '  svm/gamma.h\n'
                                                   '  svm/brightness.h\n'
                                                   '  svm/geometry.h\n'
                                                   '  svm/gradient.h\n'
                                                   '  svm/hsv.h\n'
                                                   '  svm/ies.h\n'
                                                   '  svm/image.h\n'
                                                   '  svm/invert.h\n'
                                                   '  svm/light_path.h\n'
                                                   '  svm/magic.h\n'
                                                   '  svm/map_range.h\n'
                                                   '  svm/mapping.h\n'
                                                   '  svm/mapping_util.h\n'
                                                   '  svm/math.h\n'
                                                   '  svm/math_util.h\n'
                                                   '  svm/mix.h\n'
                                                   '  svm/musgrave.h\n'
                                                   '  svm/noise.h\n'
                                                   '  svm/noisetex.h\n'
                                                   '  svm/normal.h\n'
                                                   '  svm/ramp.h\n'
                                                   '  svm/ramp_util.h\n'
                                                   '  svm/sepcomb_hsv.h\n'
                                                   '  svm/sepcomb_vector.h\n'
                                                   '  svm/sky.h\n'
                                                   '  svm/tex_coord.h\n'
                                                   '  svm/truchet.h\n'
                                                   '  svm/fractal_noise.h\n'
                                                   '  svm/types.h\n'
                                                   '  svm/value.h\n'
                                                   '  svm/vector_transform.h\n'
                                                   '  svm/voronoi.h\n'
                                                   '  svm/voxel.h\n'
                                                   '  svm/wave.h\n'
                                                   '  svm/white_noise.h\n'
                                                   '  svm/vertex_color.h\n'
                                                   ')\n'
                                                   '\n'
                                                   'set(SRC_GEOM_HEADERS\n')) as mf:
            cmake = self._create_default_cmake_manager()
            cmake._add_svm()

            self.assertTrue('  svm/vertex_color.h\n'
                            '  svm/z.h\n)' in mf.mock_calls[-3][1][0])

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
            self.assertTrue('  nodes/node_shader_node_name.c' in mf.mock_calls[-3][1][0])

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
            self.assertTrue('  nodes/node_shader_tex_node_name.c' in mf.mock_calls[-3][1][0])


if __name__ == '__main__':
    unittest.main()
