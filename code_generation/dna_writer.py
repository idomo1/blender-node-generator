from os import path
from collections import defaultdict
import re

import code_generation.code_generator_util as code_generator_util
from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp


class DNAWriter:
    """Writes code related to DNA"""
    def __init__(self, gui):
        self._node_name = gui.get_node_name()
        self._props = gui.get_props()
        self._source_path = gui.get_source_path()
        self._node_type = gui.get_node_type()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._is_texture_node = self._node_type == 'Texture'

    def _generate_enums(self):
        """Enums used for enum props"""
        return ''.join('enum {{'
                       '{enums}'
                       '}};\n\n'.format(
            enums=''.join('SHD_{NAME}_{OPTION} = {i},'.format(
                NAME=code_generator_util.string_upper_underscored(self._node_name),
                OPTION=code_generator_util.string_upper_underscored(option['name']),
                i=i + 1
            ) for i, option in enumerate(dropdown['options'])))
                       for dropdown in self._props if isinstance(dropdown['data-type'], EnumProp))

    def _generate_macros(self):
        """Macros used for bool props"""
        return ''.join('#define SHD_{NAME}_{BOOL} {i}\n'.format(
            NAME=code_generator_util.string_upper_underscored(self._node_name),
            BOOL=code_generator_util.string_upper_underscored(prop['name']),
            i=i + 1
        ) for i, prop in enumerate([prop for prop in self._props if isinstance(prop['data-type'], BoolProp)]))

    def write_dna_node_type(self):
        """
        DNA_node_types.h
        """
        dna_path = path.join(self._source_path, "source", "blender", "makesdna", "DNA_node_types.h")
        with open(dna_path, 'r+') as f:
            text = f.read()

            if code_generator_util.uses_dna(self._props, self._node_type):
                props = defaultdict(list)
                for prop in self._props:
                    prop_name = code_generator_util.string_lower_underscored(prop['name'])
                    props['int'].append(prop_name)
                props_definitions = "; ".join(
                    '{key} {names}'.format(key=key, names=", ".join(names)) for key, names in props.items()) + ";"
                struct = 'typedef struct Node{Suff}{name} {{{base}{props}{pad}}} Node{Suff}{name};\n\n'.format(
                    Suff=self._type_suffix_abbreviated.capitalize(),
                    base='NodeTexBase base;' if self._is_texture_node else '',
                    name=code_generator_util.string_capitalized_no_space(self._node_name),
                    props=props_definitions,
                    pad=' char _pad[{size}];'.format(size=code_generator_util.dna_padding_size(self._props))
                    if code_generator_util.dna_padding_size(self._props) != 0 else '')

                match = re.search('} NodeTex'[::-1], text[::-1])  # Reversed to find last occurrence
                if not match:
                    raise Exception("No match found")

                i = len(text) - match.end()
                for _ in range(i, len(text)):
                    if text[i] == '\n':
                        break
                    i += 1
                else:
                    print("No newline found")
                text = text[:i + 2] + struct + text[i + 2:]

            if [prop for prop in self._props if isinstance(prop['data-type'], (EnumProp, BoolProp))]:
                macros = self._generate_macros()
                defs = '/* {name} */\n' \
                       '{macros}' \
                       '{enums}'.format(name=self._node_name.lower(),
                                        macros='{0}\n'.format(macros) if macros else '',
                                        enums=self._generate_enums())

                match = re.search(r'/\* Output shader node \*/', text)
                if not match:
                    raise Exception("No match found")

                text = text[:match.start()] + defs + text[match.start():]

            f.seek(0)
            f.write(text)
            f.truncate()

        code_generator_util.apply_clang_formatting(dna_path, self._source_path)
