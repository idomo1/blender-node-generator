from os import path, SEEK_SET

from . import code_generator_util


class RNAWriter:
    def __init__(self, gui):
        self._node_has_properties = gui.node_has_properties()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._source_path = gui.get_source_path()
        self._props = gui.get_props()
        self._node_type = gui.get_node_type()
        self._node_name = gui.get_node_name()
        self._is_texture_node = self._node_type == 'Texture'

    def _generate_enum_prop_item(self, enum):
        """Generates RNA enum property item"""
        if enum['data-type'] != 'Enum':
            raise Exception("Given prop must be an Enum")

        return 'static const EnumPropertyItem rna_enum_node_{suff}{enum}_items[] = {{' \
               '{options}' \
               '{{0, NULL, 0, NULL, NULL}},' \
               '}};\n\n'.format(suff='{suff}_'.format(
            suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                enum=code_generator_util.string_lower_underscored(enum['name']),
                                options=''.join('{{{i}, "{OPTION}", 0, "{Option}", "{desc}"}},'.format(
                                    i=i + 1,
                                    OPTION=code_generator_util.string_upper_underscored(option['name']),
                                    Option=code_generator_util.string_capitalized_spaced(option['name']),
                                    desc=option['desc']
                                ) for i, option in enumerate(enum['options'])))

    def write_rna_properties(self):
        """rna_nodetree.c"""
        if self._node_has_properties:
            file_path = path.join(self._source_path, "source", "blender", "makesrna", "intern",
                                  "rna_nodetree.c")
            with open(file_path, 'r+') as f:
                props = []
                enum_defs = []
                s_custom_i = 1
                f_custom_i = 3
                uses_dna = code_generator_util.uses_dna(self._props, self._node_type)
                for prop in self._props:
                    if not uses_dna:
                        if prop['data-type'] == "Enum" or prop['data-type'] == "Int":
                            custom_i = s_custom_i
                            s_custom_i += 1
                        elif prop['data-type'] == "Boolean":
                            custom_i = s_custom_i
                        elif prop['data-type'] == "Float":
                            custom_i = f_custom_i
                            f_custom_i += 1
                    if prop['data-type'] == "Enum":
                        enum_name = 'rna_enum_node_{suff}{name}_items'. \
                            format(suff='{suff}_'.format(
                            suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                   name=code_generator_util.string_lower_underscored(prop['name']))
                        enum_defs.append(self._generate_enum_prop_item(prop))

                    props.append('prop = RNA_def_property(srna, "{name}", PROP_{TYPE}, {SUBTYPE});'
                                 'RNA_def_property_{type}_sdna(prop, NULL, "{sdna}"{enum});'
                                 '{enum_items}'
                                 '{prop_range}'
                                 'RNA_def_property_ui_text(prop, "{Name}", "{desc}");'
                                 'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");'.
                        format(
                        name=code_generator_util.string_lower_underscored(prop['name']),
                        TYPE=code_generator_util.string_upper_underscored(prop['data-type']),
                        SUBTYPE=prop['sub-type'],
                        type=code_generator_util.string_lower_underscored(prop['data-type']),
                        sdna=code_generator_util.string_lower_underscored(
                            prop['name'] if uses_dna else "custom{index}".format(index=custom_i)),
                        enum=', SHD_{NAME}_{PROP}'.format(
                            NAME=code_generator_util.string_upper_underscored(self._node_name),
                            PROP=code_generator_util.string_upper_underscored(prop['name']))
                        if prop['data-type'] == "Boolean" else '',
                        enum_items='RNA_def_property_enum_items(prop, {enum_name});'.format(enum_name=enum_name) if
                        prop['data-type'] == "Enum" else '',
                        prop_range='RNA_def_property_range(prop, {min}, {max});'.format(min=prop['min'],
                                                                                        max=prop['max']) if prop[
                                                                                                                'data-type'] == "Int" or
                                                                                                            prop[
                                                                                                                'data-type'] == "Float" else '',
                        Name=code_generator_util.string_capitalized_spaced(prop['name']),
                        desc=""))

                func = 'static void def_sh_{suff}{name}(StructRNA *srna)\n' \
                       '{{\n' \
                       'PropertyRNA *prop;\n\n' \
                       '{sdna}' \
                       '{props}\n' \
                       '}}\n\n'.format(suff="{suff}_".format(
                    suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                                       name=self._node_name.replace(" ", "_").lower(),
                                       sdna='RNA_def_struct_sdna_from(srna, "Node{Tex}{Name}", "storage");\ndef_sh_tex(srna);\n\n'. \
                                       format(Name=code_generator_util.string_capitalized_no_space(
                                           self._node_name),
                                           Tex="Tex" if self._is_texture_node else "")
                                       if self._is_texture_node else '',
                                       props="\n\n".join(props))
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line == '/* -- Compositor Nodes ------------------------------------------------------ */\n':
                        lines.insert(i, func)
                        break
                else:
                    raise Exception("Reached end of file without match")

                if len(enum_defs) > 0:
                    for i, line in enumerate(lines):
                        if line == '#ifndef RNA_RUNTIME\n':
                            j = i
                            while lines[j] != '#endif\n':
                                j += 1
                            for enum in enum_defs:
                                lines.insert(j + 1, enum)
                            break
                    else:
                        raise Exception("Reached end of file without match")

                f.seek(0, SEEK_SET)
                f.writelines(lines)
                f.truncate()
            code_generator_util.apply_clang_formatting(file_path, self._source_path)
