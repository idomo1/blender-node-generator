from os import path
import re

from . import code_generator_util

CMAKE_FILE_NAME = 'CMakeLists.txt'


class CMakeCodeManager:
    """Adds new files to Cmake build list"""

    def __init__(self, gui):
        self._source_path = gui.get_source_path()
        self._node_name = gui.get_node_name()
        self._is_texture_node = gui.is_texture_node()

    def _insert_cmake_file_path(self, names_start_i, file_text, new_file_path):
        """
        Inserts the new file path into the file text and returns the modified text
        :param names_start_i: start index of the list of filenames in text
        :param file_text: file text
        :param new_file_name: file path to be inserter
        :return: file text with new path inserted
        """
        for i in range(names_start_i, len(file_text)):
            if file_text[i] == ')':
                break
        else:
            raise Exception("End of svm not found")
        names_end_i = i - 1
        file_paths = file_text[names_start_i:names_end_i].split('\n')

        # Try to place new file for sorted order, however not all file names are sorted alphabetically,
        # Best that can be done is to place before the first name greater than new file name
        for i, file_name in enumerate(file_paths):
            if file_name > new_file_path:
                break
        else:
            # If element should go last
            i = len(file_paths)
        file_paths.insert(i, new_file_path)

        return file_text[:names_start_i] + '\n'.join(file_paths) + file_text[names_end_i:]

    def _add_svm(self):
        """Adds created svm file to cmake list"""
        with open(path.join(self._source_path, "intern", "cycles", "kernel", CMAKE_FILE_NAME), 'r+') as f:
            text = f.read()
            match = re.search(r'set\(SRC_SVM_HEADERS', text)
            if not match:
                raise Exception("Match not found")

            svm_start = match.end() + 1

            svm_file_path = '  svm/svm_{name}.h'.format(
                name=code_generator_util.string_lower_underscored(self._node_name))

            text = self._insert_cmake_file_path(svm_start, text, svm_file_path)

            f.seek(0)
            f.write(text)
            f.truncate()

    def _add_osl(self):
        with open(path.join(self._source_path, "intern", "cycles", "kernel", "shaders", CMAKE_FILE_NAME), 'r+') as f:
            text = f.read()
            match = re.search(r'set\(SRC_OSL', text)
            if not match:
                raise Exception("Match not found")
            osl_start_i = match.end() + 1

            osl_path = '  node_{name}.osl'.format(name=code_generator_util.string_lower_underscored(self._node_name))

            text = self._insert_cmake_file_path(osl_start_i, text, osl_path)

            f.seek(0)
            f.write(text)
            f.truncate()

    def _add_node(self):
        with open(path.join(self._source_path, "source", "blender", "nodes", CMAKE_FILE_NAME), 'r+') as f:
            text = f.read()
            match = re.search(r'set\(SRC\n', text)
            if not match:
                raise Exception("Match not found")
            node_start_i = match.end()

            node_path = '  shader/nodes/node_shader_{tex}{name}.c'.format(
                tex='tex_' if self._is_texture_node else '',
                name=code_generator_util.string_lower_underscored(self._node_name)
            )

            text = self._insert_cmake_file_path(node_start_i, text, node_path)

            f.seek(0)
            f.write(text)
            f.truncate()

    def add_to_cmake(self):
        """Adds created files to cmake lists"""
        self._add_svm()
        self._add_osl()
        self._add_node()
