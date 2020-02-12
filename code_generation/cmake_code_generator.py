from os import path
import re

from . import code_generator_util


class CMakeCodeManager:
    """Adds new files to Cmake build list"""

    def __init__(self, gui):
        self._source_path = gui.get_source_path()
        self._node_name = gui.get_node_name()

    def _add_svm(self):
        """Adds created svm file to cmake list"""
        with open(path.join(self._source_path, "intern", "cycles", "kernel", "CMakeLists.txt"), 'r+') as f:
            text = f.read()
            match = re.search('set\(SRC_SVM_HEADERS', text)
            if not match:
                raise Exception("Match not found")

            svm_start = match.end() + 1

            for i in range(svm_start, len(text)):
                if text[i] == ')':
                    break
            else:
                raise Exception("End of svm not found")
            svm_end = i - 1
            svm_files = text[svm_start:svm_end]

            svm_file_name = '  svm/svm_{name}.h'.format(
                name=code_generator_util.string_lower_underscored(self._node_name))
            svm_files = svm_files.split('\n')

            # Try to place new file for sorted order, however not all file names are sorted alphabetically,
            # Best that can be done is to place before the first name greater than new file name
            for i, file_name in enumerate(svm_files):
                if file_name > svm_file_name:
                    break
            else:
                # If element should go last
                i = len(svm_files)
            svm_files.insert(i, svm_file_name)

            text = text[:svm_start] + '\n'.join(svm_files) + text[svm_end:]

            f.seek(0)
            f.write(text)
            f.truncate()

    def add_to_cmake(self):
        """Adds created files to cmake lists"""
        self._add_svm()
