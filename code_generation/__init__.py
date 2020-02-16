from os import path, SEEK_END, SEEK_SET
import re
from collections import defaultdict

from . import code_generator_util
from .svm_code_generator import SVMCompilationManager
from .glsl_code_generator import GLSLCodeManager
from .cmake_code_generator import CMakeCodeManager


class CodeGenerator:
    """Generates code required for a new node"""

    def __init__(self, gui):
        self._gui = gui

    def _add_node_type_id(self):
        """BKE_node.h"""
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenkernel", "BKE_node.h"),
                  "r+") as f:
            file_text = f.read()
            last_i = -1
            last_id = re.search('[7-9][0-9][0-9]\n\n', file_text)
            if last_id is not None:
                last_i = last_id.end()
            else:
                print("Node ID not found")
            last = int(file_text[last_i - 5:last_i - 2])
            name_underscored = "_".join(self._gui.get_node_name().split(" "))
            line = "#define SH_NODE_{0}{1} {2}\n".format("TEX_" if self._gui.is_texture_node() else "",
                                                         name_underscored.upper(), str(last + 1))
            file_text = file_text[:last_i - 1] + line + file_text[last_i - 1:]

            f.seek(0)
            f.write(file_text)
            f.truncate()

    def _generate_enums(self):
        """Enums used for enum props"""
        return ''.join('enum {{'
                       '{enums}'
                       '}};\n\n'.format(
            enums=''.join('SHD_{NAME}_{OPTION} = {i},'.format(
                NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                OPTION=code_generator_util.string_upper_underscored(option['name']),
                i=i + 1
            ) for i, option in enumerate(dropdown['options'])))
                       for dropdown in self._gui.get_props() if dropdown['data-type'] == 'Enum')

    def _generate_macros(self):
        """Macros used for bool props"""
        return ''.join('#define SHD_{NAME}_{BOOL} {i}\n'.format(
            NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
            BOOL=code_generator_util.string_upper_underscored(prop['name']),
            i=i + 1
        ) for i, prop in enumerate([prop for prop in self._gui.get_props() if prop['data-type'] == 'Boolean']))

    def _add_dna_node_type(self):
        """
        DNA_node_types.h
        """
        dna_path = path.join(self._gui.get_source_path(), "source", "blender", "makesdna", "DNA_node_types.h")
        with open(dna_path, 'r+') as f:
            text = f.read()

            if code_generator_util.uses_dna(self._gui.get_props(), self._gui.get_node_type()):
                props = defaultdict(list)
                for prop in self._gui.get_props():
                    prop_name = code_generator_util.string_lower_underscored(prop['name'])
                    if prop['data-type'] in ['Enum', 'Boolean', 'Int']:
                        props['int'].append(prop_name)
                    elif prop['data-type'] == 'String':
                        props['char'].append("{name}[{size}]".format(name=prop_name, size=prop['size']))
                    elif prop['data-type'] == 'Float':
                        props['float'].append(prop_name)
                    else:
                        raise Exception("Invalid Property Type")
                props_definitions = "; ".join(
                    '{key} {names}'.format(key=key, names=", ".join(names)) for key, names in props.items()) + ";"
                struct = 'typedef struct Node{Tex}{name} {{{base}{props}{pad}}} Node{Tex}{name};\n\n'.format(
                    Tex='Tex' if self._gui.is_texture_node() else '',
                    base='NodeTexBase base;' if self._gui.is_texture_node() else '',
                    name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                    props=props_definitions,
                    pad=' char _pad[{size}];'.format(size=code_generator_util.dna_padding_size(self._gui.get_props()))
                        if code_generator_util.dna_padding_size(self._gui.get_props()) != 0 else '')

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

            if [prop for prop in self._gui.get_props() if prop['data-type'] in ['Enum', 'Boolean']]:
                macros = self._generate_macros()
                defs = '/* {name} */\n' \
                       '{macros}' \
                       '{enums}'.format(name=self._gui.get_node_name().lower(),
                                        macros='{0}\n'.format(macros) if macros else '',
                                        enums=self._generate_enums())

                match = re.search(r'/\* Output shader node \*/', text)
                if not match:
                    raise Exception("No match found")

                text = text[:match.start()] + defs + text[match.start():]

            f.seek(0)
            f.write(text)
            f.truncate()

        code_generator_util.apply_clang_formatting(dna_path, self._gui.get_source_path())

    def _generate_enum_prop_item(self, enum):
        """Generates RNA enum property item"""
        if enum['data-type'] != 'Enum':
            raise Exception("Given prop must be an Enum")

        return 'static const EnumPropertyItem rna_enum_node_{tex}{enum}_items[] = {{' \
               '{options}' \
               '{{0, NULL, 0, NULL, NULL}},' \
               '}};\n\n'.format(tex='tex_' if self._gui.is_texture_node() else '',
                                enum=code_generator_util.string_lower_underscored(enum['name']),
                                options=''.join('{{{i}, "{OPTION}", 0, "{Option}", "{desc}"}},'.format(
                                    i=i + 1,
                                    OPTION=code_generator_util.string_upper_underscored(option['name']),
                                    Option=code_generator_util.string_capitalized_spaced(option['name']),
                                    desc=option['desc']
                                ) for i, option in enumerate(enum['options'])))

    def _add_rna_properties(self):
        """rna_nodetree.c"""
        if self._gui.node_has_properties():
            file_path = path.join(self._gui.get_source_path(), "source", "blender", "makesrna", "intern",
                                  "rna_nodetree.c")
            with open(file_path, 'r+') as f:
                props = []
                enum_defs = []
                s_custom_i = 1
                f_custom_i = 3
                uses_dna = code_generator_util.uses_dna(self._gui.get_props(), self._gui.get_node_type())
                for prop in self._gui.get_props():
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
                        enum_name = 'rna_enum_node_{tex}{name}_items'. \
                            format(tex='tex_' if self._gui.is_texture_node() else '',
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
                            NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
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

                func = 'static void def_sh_{tex}{name}(StructRNA *srna)\n' \
                       '{{\n' \
                       'PropertyRNA *prop;\n\n' \
                       '{sdna}' \
                       '{props}\n' \
                       '}}\n\n'.format(tex="tex_" if self._gui.is_texture_node() else '',
                                       name=self._gui.get_node_name().replace(" ", "_").lower(),
                                       sdna='RNA_def_struct_sdna_from(srna, "Node{Tex}{Name}", "storage");\ndef_sh_tex(srna);\n\n'. \
                                       format(Name=code_generator_util.string_capitalized_no_space(
                                           self._gui.get_node_name()),
                                           Tex="Tex" if self._gui.is_texture_node() else "")
                                       if self._gui.is_texture_node() else '',
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
            code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_node_definition(self):
        """NOD_static_types.h"""
        def_node_line_length = 138
        def_node_parameter_offsets = [0, 16, 44, 68, 90, 108, 129]
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")
        with open(file_path, "r+") as f:
            params = 'ShaderNode,' \
                     'SH_NODE_{TEX}{NAME},' \
                     '{rna},' \
                     '"{NAME}",' \
                     '{struct},' \
                     '"{Name}{Texture}",' \
                     '""'.format(
                TEX='TEX_' if self._gui.is_texture_node() else '',
                NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                rna='def_sh_{tex}{name}'.format(
                    tex='tex_' if self._gui.is_texture_node() else '',
                    name=code_generator_util.string_lower_underscored(
                        self._gui.get_node_name())) if self._gui.node_has_properties() else 0,
                struct='{Tex}{Name}'.format(Tex='Tex' if self._gui.is_texture_node() else '',
                                            Name=code_generator_util.string_capitalized_no_space(
                                                self._gui.get_node_name())),
                Tex='Tex' if self._gui.is_texture_node() else '',
                Name=code_generator_util.string_capitalized_spaced(self._gui.get_node_name()),
                Texture=' Texture' if self._gui.is_texture_node() else '')

            node_definition = 'DefNode({params})\n'.format(
                params=code_generator_util.fill_white_space(
                    params.split(','), def_node_line_length, def_node_parameter_offsets))

            # Find last shader node definition, write new node def under that
            text = f.read()
            matches = re.search(r'edoNredahS\(edoNfeD', text[::-1])
            if not matches:
                raise Exception("Match not found")
            match_i = len(text) - matches.end()
            for i in range(match_i, len(text)):
                if text[i] == '\n':
                    break
            else:
                raise Exception("No newline found")

            text = text[:i + 1] + node_definition + text[i + 1:]
            f.seek(0)
            f.write(text)
            f.truncate()

    def _add_node_drawing(self):
        """drawnode.c"""
        drawnode_path = path.join(self._gui.get_source_path(), "source", "blender", "editors", "space_node",
                                  "drawnode.c")
        with open(drawnode_path, "r+") as f:
            if self._gui.node_has_properties():
                draw_props = ''
                if self._gui.node_has_properties():
                    prop_lines = []
                    for prop in self._gui.get_props():
                        name = "NULL"
                        if prop['data-type'] == "Enum":
                            name = '""'
                        elif prop['data-type'] == "String":
                            name = 'IFACE_("{name}")'.format(
                                name=code_generator_util.string_capitalized_spaced(prop['name']))
                        prop_lines.append(
                            'uiItemR(layout, ptr, "{propname}", 0, {name}, ICON_NONE);'.format(
                                propname=code_generator_util.string_lower_underscored(prop['name']),
                                name=name))

                    draw_props = ''.join(prop_lines)
                func = 'static void node_shader_buts_{tex}{name}(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)' \
                       '{{{props}}}\n\n'.format(
                    tex='tex_' if self._gui.is_texture_node() else '',
                    name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                    props=draw_props)
                lines = f.readlines()
                line_i = lines.index("static void node_shader_set_butfunc(bNodeType *ntype)\n") - 1

                lines.insert(line_i, func)

                case = [
                    "case SH_NODE_{tex}{name}:\n".format(tex="TEX_" if self._gui.is_texture_node() else "",
                                                         name=code_generator_util.string_upper_underscored(
                                                             self._gui.get_node_name())),
                    "ntype->draw_buttons = node_shader_buts_{tex}{name};\n".format(
                        tex="tex_" if self._gui.is_texture_node() else "",
                        name=code_generator_util.string_lower_underscored(self._gui.get_node_name())),
                    "break;\n"]

                for i in range(line_i, len(lines)):
                    if "break" in lines[i] and '}' in lines[i + 1]:
                        line_i = i + 1
                        break
                else:
                    print("Not Found")
                    return

                for line in reversed(case):
                    lines.insert(line_i, line)

                f.seek(0)
                f.writelines(lines)
                f.truncate()
        code_generator_util.apply_clang_formatting(drawnode_path, self._gui.get_source_path())

    def _generate_node_shader_sockets(self):
        """
        Generates node socket definition function code
        :return: socket definition code as text, or empty string if no sockets
        """
        sockets = self._gui.get_node_sockets()
        if len(sockets) == 0:
            return ''
        sockets_in = []
        sockets_out = []
        out = []
        for sock in sockets:
            socket_text = '{{SOCK_{TYPE}, {input_count}, N_("{Name}"), {default}, {min}, {max}{subtype}{flag}}},'.format(
                TYPE=sock['data-type'].upper(), Name=code_generator_util.string_capitalized_spaced(sock['name']),
                input_count=1 if sock['type'] == 'Input' else 0,
                default=code_generator_util.fill_socket_default(sock['default']), min=sock['min'] + 'f',
                max=sock['max'] + 'f',
                subtype=(', ' + sock['sub-type']) if sock['sub-type'] != 'PROP_NONE' or sock[
                    'flag'] != "None" else '',
                flag=(', ' + sock['flag']) if sock['flag'] != 'None' else '')
            if sock['type'] == "Input":
                sockets_in.append(socket_text)
            else:
                sockets_out.append(socket_text)
        if len(sockets_in) > 0:
            in_sockets_text = 'static bNodeSocketTemplate sh_node_{tex}{name}_in[] = {{{sockets}{{-1, 0, ""}},}};\n\n'.format(
                tex="tex_" if self._gui.is_texture_node() else "",
                name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                sockets="".join(sockets_in))
            out.append(in_sockets_text)

        if len(sockets_out) > 0:
            out_sockets_text = 'static bNodeSocketTemplate sh_node_{tex}{name}_out[] = {{{sockets}{{-1, 0, ""}},}};\n\n'.format(
                tex="tex_" if self._gui.is_texture_node() else "",
                name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                sockets="".join(sockets_out))
            out.append(out_sockets_text)
        return ''.join(out)

    def _generate_node_shader_init(self):
        """
        Generates node init function code
        :return: init function code as text
        """

        if not self._gui.node_has_properties():
            return ''

        props = self._gui.get_props()
        prop_init = ''
        uses_dna = code_generator_util.uses_dna(self._gui.get_props(), self._gui.get_node_type())
        if uses_dna:
            struct = 'tex' if self._gui.is_texture_node() else 'attr'
            defaults = []
            for prop in props:
                if prop['data-type'] == 'Enum':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default='SHD_{NAME}_{PROP}'.format(
                            NAME=code_generator_util.string_upper_underscored(
                                self._gui.get_node_name()),
                            PROP=code_generator_util.string_upper_underscored(
                                prop['default']))))
                elif prop['data-type'] == 'Boolean' or prop['data-type'] == 'Int':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default=prop['default']))
                elif prop['data-type'] == 'Float':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        default='{default}f'.format(default=prop['default'])))
            prop_init = ''.join(defaults)
        else:  # Use custom
            defaults = []
            s_custom_i = 1
            f_custom_i = 3
            boolean_bit = 0
            for prop in props:
                if prop['data-type'] == 'Enum':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i,
                                                                          default='SHD_{NAME}_{PROP}'.format(
                                                                              NAME=code_generator_util.string_upper_underscored(
                                                                                  self._gui.get_node_name()),
                                                                              PROP=code_generator_util.string_upper_underscored(
                                                                                  prop['default']))))
                    s_custom_i += 1
                elif prop['data-type'] == 'Int':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    s_custom_i += 1
                elif prop['data-type'] == 'Boolean':
                    # Need to set bits if multiple bools
                    if len([prop for prop in props if prop['data-type'] == 'Boolean']) == 1:
                        defaults.append(
                            'node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    else:
                        # Set nth bit
                        defaults.append('node->custom{i} |= {default} << {boolean_bit};'.format(
                            i=s_custom_i,
                            default=int(prop['default']),
                            boolean_bit=boolean_bit))
                        boolean_bit += 1
                elif prop['data-type'] == 'Float':
                    defaults.append('node->custom{i} = {default}f;'.format(i=f_custom_i, default=prop['default']))
            prop_init = ''.join(defaults)

        init_func = 'static void node_shader_init_{tex}{name}(bNodeTree *UNUSED(ntree), bNode *node){{' \
                    '{get_storage}' \
                    '{texture_mapping}' \
                    '{prop_init}\n\n' \
                    '{set_storage}' \
                    '}}\n\n'.format(
            tex='tex_' if self._gui.is_texture_node() else '',
            name=code_generator_util.string_lower_underscored(
                self._gui.get_node_name()),
            Tex='Tex' if self._gui.is_texture_node() else '',
            get_storage='Node{Tex}{Name} *{struct} = MEM_callocN(sizeof(Node{Tex}{Name}), "Node{Tex}{Name}");'.format(
                Tex='Tex' if self._gui.is_texture_node() else '',
                Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                struct=struct) if uses_dna else '',
            Name=code_generator_util.string_capitalized_no_space(
                self._gui.get_node_name()),
            texture_mapping='BKE_texture_mapping_default(&tex->base.tex_mapping, TEXMAP_TYPE_POINT);'
                            'BKE_texture_colormapping_default(&tex->base.color_mapping);'
            if self._gui.uses_texture_mapping() else '',
            prop_init=prop_init,
            set_storage='node->storage = {struct};'.format(struct=struct) if uses_dna else '')
        return init_func

    def _generate_node_shader_gpu(self):
        """
        Generate node gpu function code
        :return: gpu function as text
        """
        glsl_manager = GLSLCodeManager(self._gui)
        return glsl_manager.generate_gpu_func()

    def _generate_node_shader_socket_availability(self):
        if not self._gui.socket_availability_changes():
            return ''

        props = self._gui.get_props()
        if len(props) == 0:
            return ''

        struct = 'tex' if self._gui.is_texture_node() else 'attr'

        in_sockets = []
        out_sockets = []
        socket_availability = []
        for map in self._gui.get_socket_availability_maps():
            if any(not available for prop, available in map['prop-avail']):
                type = map['socket-type']
                socket_get = 'bNodeSocket *{type}{Name}Sock = nodeFindSocket(node, SOCK_{TYPE}, "{Name_Spaced}");'.format(
                    type=type,
                    Name=code_generator_util.string_capitalized_no_space(map['socket-name']),
                    TYPE=map['socket-type'].upper(),
                    Name_Spaced=code_generator_util.string_capitalized_spaced(map['socket-name']))
                if map['socket-type'] == 'in':
                    in_sockets.append(socket_get)
                else:
                    out_sockets.append(socket_get)

                constraints = []
                avail_count = sum(avail for prop, avail in map['prop-avail'])
                invert_avail = avail_count / len(map['prop-avail']) < 0.5
                if code_generator_util.uses_dna(props, self._gui.get_node_type()):
                    for prop, avail in map['prop-avail']:
                        prop_name, value = prop.split('=')
                        is_enum = not (value == 'False' or value == 'True')
                        if not invert_avail and not avail:
                            constraints.append('{struct}->{prop} != {value}'.format(
                                struct=struct,
                                prop=code_generator_util.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                                    OPTION=code_generator_util.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                        elif invert_avail and avail:
                            constraints.append('{struct}->{prop} == {value}'.format(
                                struct=struct,
                                prop=code_generator_util.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                                    OPTION=code_generator_util.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                else:
                    bool_count = len(list(filter(lambda p: p['data-type'] == 'Boolean', props)))
                    s_custom_i = 1
                    boolean_bit = 0
                    last_prop = None
                    last_prop_is_enum = None
                    for prop, avail in map['prop-avail']:
                        prop_name, value = prop.split('=')
                        is_enum = not (value == 'False' or value == 'True')

                        if last_prop is None:
                            last_prop = prop_name
                            last_prop_is_enum = is_enum

                        if prop_name != last_prop:
                            if not last_prop_is_enum:
                                boolean_bit += 1
                            else:
                                s_custom_i += 1
                        last_prop = prop_name
                        last_prop_is_enum = is_enum

                        if not invert_avail and not avail:
                            if not is_enum and bool_count > 1:
                                constraints.append('(node->custom{i} >> {bit}) & 1 != {value}'.format(
                                    i=s_custom_i,
                                    bit=boolean_bit,
                                    value=int(avail)
                                ))
                            else:
                                constraints.append('node->custom{i} != {value}'.format(
                                    i=s_custom_i,
                                    prop=code_generator_util.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                                        OPTION=code_generator_util.string_upper_underscored(value))
                                    if is_enum else int(value == 'True')))
                        elif invert_avail and avail:
                            if not is_enum and bool_count > 1:
                                constraints.append('(node->custom{i} >> {bit}) & 1 == {value}'.format(
                                    i=s_custom_i,
                                    bit=boolean_bit,
                                    value=int(avail)
                                ))
                            else:
                                constraints.append('node->custom{i} == {value}'.format(
                                    i=s_custom_i,
                                    prop=code_generator_util.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                                        OPTION=code_generator_util.string_upper_underscored(value))
                                    if is_enum else int(value == 'True')))
                socket_availability.append('nodeSetSocketAvailability({socket}, {constraints});'.format(
                    socket='{type}{Name}Sock'.format(
                        type=type,
                        Name=code_generator_util.string_capitalized_no_space(map['socket-name'])),
                    constraints=' || '.join(constraints) if invert_avail else ' && '.join(constraints)))

        if len(in_sockets) > 0:
            in_sockets.append('\n\n')
        if len(out_sockets) > 0:
            out_sockets.append('\n\n')
        get_struct = 'Node{Tex}{Name} *{struct} = (Node{Tex}{Name} *)node->storage;\n\n'.format(
            Tex='Tex' if self._gui.is_texture_node() else '',
            Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
            struct='tex' if self._gui.is_texture_node() else 'attr')

        socket_availability_func = 'static void node_shader_update_{tex}{name}(bNodeTree *UNUSED(ntree), bNode *node)' \
                                   '{{' \
                                   '{in_sockets}' \
                                   '{out_sockets}' \
                                   '{struct}' \
                                   '{availability}' \
                                   '}}\n\n'.format(
            tex='tex_' if self._gui.is_texture_node() else '',
            name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
            in_sockets=''.join(in_sockets),
            out_sockets=''.join(out_sockets),
            struct=get_struct if code_generator_util.uses_dna(props, self._gui.get_node_type()) else '',
            availability=''.join(socket_availability))
        return socket_availability_func

    def _generate_node_shader_register(self):
        register_text = 'void register_node_type_sh_{tex}{name}(void)' \
                        '{{' \
                        'static bNodeType ntype;\n\n' \
                        'sh_node_type_base(&ntype, SH_NODE_{TEX}{NAME}, "{Name}", NODE_CLASS_{CLASS}, 0);' \
                        'node_type_socket_templates(&ntype, sh_node_{tex}{name}_in, sh_node_{tex}{name}_out);' \
                        '{init}' \
                        '{storage}' \
                        'node_type_gpu(&ntype, gpu_shader_{tex}{name});' \
                        '{update}\n\n' \
                        'nodeRegisterType(&ntype);' \
                        '}}\n'.format(tex='tex_' if self._gui.is_texture_node() else '',
                                      name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                                      TEX='TEX_' if self._gui.is_texture_node() else '',
                                      NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()),
                                      Name=code_generator_util.string_capitalized_spaced(self._gui.get_node_name()),
                                      CLASS=self._gui.get_node_group().upper(),
                                      init='node_type_init(&ntype, node_shader_init_{tex}{name});'.format(
                                          tex='tex_' if self._gui.is_texture_node() else '',
                                          name=code_generator_util.string_lower_underscored(
                                              self._gui.get_node_name())) if self._gui.node_has_properties() else '',
                                      storage='node_type_storage(&ntype, "Node{Tex}{Name}", node_free_standard_storage, node_copy_standard_storage);'.format(
                                          Tex='Tex' if self._gui.is_texture_node() else '',
                                          Name=code_generator_util.string_capitalized_no_space(
                                              self._gui.get_node_name())
                                      )
                                      if code_generator_util.uses_dna(
                                          self._gui.get_props(),
                                          self._gui.get_node_type()) else 'node_type_storage(&ntype, "", NULL, NULL);',
                                      Tex='Tex' if self._gui.is_texture_node() else '',
                                      update='node_type_update(&ntype, node_shader_update_{tex}{name});'.format(
                                          tex='tex_' if self._gui.is_texture_node() else '',
                                          name=code_generator_util.string_lower_underscored(self._gui.get_node_name()))
                                      if self._gui.socket_availability_changes() else '')
        return register_text

    def _add_shader_node_file(self):
        """node_shader_*.c"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "shader", "nodes",
                              "node_shader_{tex}{name}.c".format(
                                  tex="tex_" if self._gui.is_texture_node() else "",
                                  name=code_generator_util.string_lower_underscored(
                                      self._gui.get_node_name())))
        with open(file_path, "w") as f:
            code_generator_util.write_license(f)

            file_lines = ['', '#include "../node_shader_util.h"\n\n', '/**************** {NAME} ****************/\n\n'.
                format(NAME=code_generator_util.string_upper_underscored(self._gui.get_node_name()))]

            file_lines.append(self._generate_node_shader_sockets())

            file_lines.append(self._generate_node_shader_init())

            file_lines.append(self._generate_node_shader_gpu())

            file_lines.append(self._generate_node_shader_socket_availability())

            file_lines.append(self._generate_node_shader_register())

            f.writelines(file_lines)

        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_node_register(self):
        """NOD_shader.h"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "NOD_shader.h")
        with open(file_path, 'r+') as f:

            func = 'void register_node_type_sh_{tex}{name}(void);\n'. \
                format(tex="tex_" if self._gui.is_texture_node() else '',
                       name=code_generator_util.string_lower_underscored(self._gui.get_node_name()))

            f.seek(0, SEEK_END)
            f.seek(f.tell() - 500, SEEK_SET)
            line = f.readline()
            while line != '\n':
                if line == '':
                    raise Exception("Reached end of file")
                line = f.readline()
            f.seek(f.tell() - 2, SEEK_SET)
            f.write(func)
            f.write('\n'
                    'void register_node_type_sh_custom_group(bNodeType *ntype);\n'
                    '\n'
                    '#endif\n'
                    '\n')

    def _add_call_node_register(self):
        """node.c"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "blenkernel", "intern", "node.c")
        with open(file_path, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line == 'static void registerShaderNodes(void)\n':
                    while lines[i] != '}\n':
                        i += 1
                    lines.insert(i, 'register_node_type_sh_{tex}{name}();'.format(
                        tex='tex_' if self._gui.is_texture_node() else '',
                        name=code_generator_util.string_lower_underscored(self._gui.get_node_name())
                    ))
                    break
            else:
                raise Exception("Match not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_cycles_class(self):
        """nodes.h"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.h")
        with open(file_path, 'r+') as f:
            props = defaultdict(list)
            types_convert = {"Boolean": "bool", "Int": "int", "Float": "float", "Enum": "int", "Vector": "float3",
                             "RGBA": "float3", "String": "ustring"}
            for socket in list(filter(lambda s: s['type'] == 'Input', self._gui.get_node_sockets())):
                props[types_convert[socket['data-type']]].append(
                    code_generator_util.string_lower_underscored(socket['name']))

            for prop in self._gui.get_props():
                props[types_convert[prop['data-type']]].append(
                    code_generator_util.string_lower_underscored(prop['name']))

            props_string = "".join(
                '{type} {names};'.format(type=type,
                                         names=", ".join(names)) for
                type, names in props.items())

            node = "class {name}{tex}Node : public {type}Node {{" \
                   "public:" \
                   "SHADER_NODE_CLASS({name}{tex}Node)\n" \
                   "{node_group}" \
                   "{props}" \
                   "}};".format(name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                                tex="Texture" if self._gui.is_texture_node() else "",
                                type=self._gui.get_node_type(),
                                node_group="virtual int get_group(){{return NODE_GROUP_LEVEL_{level};}}".
                                format(
                                    level=self._gui.get_node_group_level()) if self._gui.get_node_group_level() is not 0 else "",
                                props=props_string)
            f.seek(0, SEEK_END)
            f.seek(f.tell() - 100, SEEK_SET)
            line = f.readline()
            while line != '\n':
                if line == '':
                    raise Exception("Reached end of file")
                line = f.readline()
            f.seek(f.tell(), SEEK_SET)
            f.write(node)
            f.write("""

                    CCL_NAMESPACE_END

                    #endif /* __NODES_H__ */
                    """)
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_cycles_class_instance(self):
        """blender_shader.cpp"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "blender", "blender_shader.cpp")
        with open(file_path, 'r+') as f:
            props = self._gui.get_props()
            text = 'else if (b_node.is_a(&RNA_ShaderNode{Tex}{Name})) {{' \
                   'BL::ShaderNode{Tex}{Name} b_{tex}{name}_node(b_node);' \
                   '{Name}{Texture}Node *{name} = new {Name}{Texture}Node();' \
                   '{props}' \
                   '{texture_mapping}' \
                   'node = {name};' \
                   '}}\n'.format(
                Tex='Tex' if self._gui.is_texture_node() else '',
                Name=code_generator_util.string_capitalized_no_space(
                    self._gui.get_node_name()),
                tex='tex_' if self._gui.is_texture_node() else '',
                name=code_generator_util.string_lower_underscored(
                    self._gui.get_node_name()),
                Texture='Texture' if self._gui.is_texture_node() else '',
                props=''.join(
                    ['{name}->{prop} = b_{tex}{name}_node.{prop}();'.format(
                        name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        tex='tex_' if self._gui.is_texture_node() else '') for prop in props]),
                texture_mapping='BL::TexMapping b_texture_mapping(b_tex_{name}_node.texture_mapping());'
                                'get_tex_mapping(&{name}->tex_mapping, b_texture_mapping);'.format(
                    name=code_generator_util.string_lower_underscored(
                        self._gui.get_node_name())) if self._gui.uses_texture_mapping() else '') \
                if len(props) > 0 or self._gui.uses_texture_mapping() else \
                'else if (b_node.is_a(&RNA_ShaderNode{Tex}{Name})) {{' \
                'node = new {Name}{Texture}Node();}}\n'.format(
                    Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                    Tex='Tex' if self._gui.is_texture_node() else '',
                    Texture='Texture' if self._gui.is_texture_node() else '')

            file_text = f.read()
            # Find start of function
            function_i = re.search(r'static ShaderNode \*add_node\(Scene \*scene,', file_text)

            # Find end of function
            if not function_i:
                raise Exception("Match not found")

            i = function_i.span()[1]
            while file_text[i] != '{':
                i += 1
            bracket_stack = 1
            while bracket_stack > 0:
                i += 1
                if file_text[i] == '{':
                    bracket_stack += 1
                elif file_text[i] == '}':
                    bracket_stack -= 1

            # Go back to last else if
            seen_brackets = 0
            while seen_brackets < 2:
                i -= 1
                if file_text[i] == '}':
                    seen_brackets += 1

            # Insert text into file
            file_text = file_text[:i + 2] + text + file_text[i + 2:]

            f.seek(0)
            f.write(file_text)
            f.truncate()
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_cycles_node(self):
        """nodes.cpp"""

        def format_default(item):
            if item['data-type'] == 'Enum':
                for i, option in enumerate(item['options']):
                    if option['name'] == item['default']:
                        return i + 1
                else:
                    raise Exception("Default not in options")
            elif item['data-type'] == 'Boolean':
                return 'true' if item['default'] else 'false'
            elif item['data-type'] == 'Float':
                return '{0}f'.format(item['default'])
            elif item['data-type'] == 'Int':
                return item['default']
            elif item['data-type'] == 'String':
                return 'ustring()'
            elif item['data-type'] == 'Vector' or item['data-type'] == 'RGBA':
                return 'make_float3({default})'.format(
                    default=code_generator_util.fill_socket_default(item['default'], 3))

        def is_first_vector_socket(socket):
            if socket['data-type'] != 'Vector':
                return False
            return socket == [sock for sock in sockets if sock['data-type'] == 'Vector'][0]

        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.cpp")
        with open(file_path, 'r+') as f:
            props = self._gui.get_props()
            sockets = self._gui.get_node_sockets()

            svm_node_manager = SVMCompilationManager(self._gui)

            socket_defs = []
            for prop in props:
                if prop['data-type'] == 'Enum':
                    socket_defs.append('static NodeEnum {name}_enum;'.format(
                        name=code_generator_util.string_lower_underscored(prop['name'])))
                    socket_defs.extend(['{prop}_enum.insert("{OPTION}", {i});'.format(
                        prop=prop['name'],
                        OPTION=code_generator_util.string_upper_underscored(option['name']),
                        i=i + 1) for i, option in enumerate(prop['options'])])
                    socket_defs.append('SOCKET_ENUM({prop}, "{Prop}", {prop}_enum, {default});\n\n'.format(
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        Prop=code_generator_util.string_capitalized_spaced(prop['name']),
                        default=format_default(prop)))
                else:
                    socket_defs.append('SOCKET_{TYPE}({prop}, "{Prop}", {default});'.format(
                        TYPE=prop['data-type'].upper(),
                        prop=code_generator_util.string_lower_underscored(prop['name']),
                        Prop=code_generator_util.string_capitalized_spaced(prop['name']),
                        default=format_default(prop)))
            socket_defs.append('\n\n')

            data_type_map = {'Int': 'INT', 'Float': 'FLOAT', 'Enum': 'ENUM', 'Vector': 'POINT', 'RGBA': 'COLOR',
                             'Shader': 'CLOSURE', 'String': 'STRING'}

            for socket in sockets:
                socket_defs.append('SOCKET_{TYPE}_{DATA_TYPE}({name}, "{Name}"{default}{texture_mapping});'.format(
                    TYPE=socket['type'][:-3].upper(),
                    DATA_TYPE=data_type_map[socket['data-type']],
                    name=code_generator_util.string_lower_underscored(socket['name']),
                    Name=code_generator_util.string_capitalized_spaced(socket['name']),
                    default=(', ' + format_default(socket)) if socket['type'] == 'Input' and socket[
                        'data-type'] != 'Shader' else '',
                    texture_mapping=', SocketType::LINK_TEXTURE_GENERATED' if self._gui.uses_texture_mapping() and
                                                                              socket['data-type'] == 'Vector' and
                                                                              is_first_vector_socket(socket) else ''))

            node = '/* {NodeName}{space}{Texture} */\n\n' \
                   'NODE_DEFINE({Name}{Texture}Node)' \
                   '{{' \
                   'NodeType *type = NodeType::add("{name}{texture}", create, NodeType::SHADER);\n\n' \
                   '{texture_mapping}' \
                   '{sockets}\n\n' \
                   'return type;' \
                   '}}\n\n' \
                   '{Name}{Texture}Node::{Name}{Texture}Node() : {Type}Node(node_type)' \
                   '{{' \
                   '}}\n\n' \
                   '{svm_func}' \
                   'void {Name}{Texture}Node::compile(OSLCompiler &compiler)' \
                   '{{' \
                   '{tex_mapping_comp_osl}' \
                   '{osl_params}' \
                   'compiler.add(this, "node_{name}{texture}");' \
                   '}}\n\n'.format(
                NodeName=code_generator_util.string_capitalized_spaced(self._gui.get_node_name()),
                space=' ' if self._gui.is_texture_node() else '',
                Texture='Texture' if self._gui.is_texture_node() else '',
                Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                name=code_generator_util.string_lower_underscored(self._gui.get_node_name()),
                texture='_texture' if self._gui.is_texture_node() else '',
                texture_mapping='TEXTURE_MAPPING_DEFINE({Name}{Texture}Node);\n\n'.format(
                    Name=code_generator_util.string_capitalized_no_space(self._gui.get_node_name()),
                    Texture='Texture' if self._gui.is_texture_node() else ''
                ) if self._gui.uses_texture_mapping() else '',
                sockets=''.join(socket_defs),
                Type=self._gui.get_node_type(),
                svm_func=svm_node_manager.generate_svm_compile_func(),
                tex_mapping_comp_osl='tex_mapping.compile(compiler);\n\n' if self._gui.uses_texture_mapping() else '',
                osl_params=''.join('compiler.parameter(this, "{prop}");'.format(prop=prop['name']) for prop in props if
                                   prop['data-type'] != 'String')
            )

            f.seek(0, SEEK_END)
            f.seek(f.tell() - 30, SEEK_SET)
            text = f.read()
            match = re.search('\n\n', text)

            if not match:
                raise Exception("Match not found")

            f.seek(f.tell() - 30 + match.end() + 3)
            f.write(node)

            f.write('CCL_NAMESPACE_END\n\n')
        code_generator_util.apply_clang_formatting(file_path, self._gui.get_source_path())

    def _add_to_node_menu(self):
        """nodeitems_builtins.py"""
        nodeitems_path = path.join(self._gui.get_source_path(), "release", "scripts", "startup",
                                   "nodeitems_builtins.py")
        with open(nodeitems_path, 'r+') as f:
            lines = f.readlines()
            cat_line_i = 0
            for i, line in enumerate(lines):
                if re.search('SH_NEW_' + self._gui.get_node_group().upper(), line):
                    cat_line_i = i
                    break
            else:
                print("Node Type Not Found")

            for i in range(cat_line_i, len(lines)):
                if re.search(']\)', lines[i]):
                    lines.insert(i, '        NodeItem("ShaderNode{0}{1}")\n'.format(
                        "Tex" if self._gui.is_texture_node() else "",
                        code_generator_util.string_capitalized_no_space(self._gui.get_node_name())))
                    if lines[i - 1][-2] != ',':
                        lines[i - 1] = lines[i - 1][:len(lines[i - 1]) - 1] + ',\n'
                    break
            else:
                print("End not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def _add_osl_shader(self):
        """"""
        node_name_underscored = code_generator_util.string_lower_underscored(self._gui.get_node_name())
        osl_path = path.join(self._gui.get_source_path(), "intern", "cycles", "kernel", "shaders",
                             "node_{name}{texture}.osl".format(
                                 name=node_name_underscored,
                                 texture='_texture' if self._gui.is_texture_node() else ''
                             ))
        with open(osl_path, "w") as osl_f:
            code_generator_util.write_license(osl_f)

            # Must include stdcycles for closure type definition
            if any(sock['data-type'] == 'Shader' for sock in self._gui.get_node_sockets()):
                osl_f.write('#include "stdcycles.h"\n\n')
            else:
                osl_f.write('#include "stdosl.h"\n\n')


            props = self._gui.get_props()
            sockets = self._gui.get_node_sockets()

            type_conversion = {"Boolean": "int", "String": "string", "Int": "int", "Float": "float", "Enum": "string",
                               "Vector": "point", "RGBA": "point", 'Shader': 'closure color'}

            out_socket_default = {"RGBA": "0.0", "Shader": "0", "Vector": "point(0.0, 0.0, 0.0)", "Float": "0.0"}

            function = "shader node_{name}{tex}({mapping}{props}{in_sockets}{out_sockets}){{}}\n".format(
                name=node_name_underscored,
                tex='_texture' if self._gui.is_texture_node() else '',
                mapping='int use_mapping = 0,matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                if self._gui.uses_texture_mapping() else '',
                props=''.join('{type} {name} = {default},'.format(
                    type=type_conversion[prop['data-type']],
                    name=code_generator_util.string_lower_underscored(prop['name']),
                    default='"{default}"'.format(default=prop['default']) if prop['data-type'] == 'Enum' else prop[
                        'default'])
                              for prop in props if prop['data-type'] != 'String'),
                in_sockets=''.join(['{type} {name} = {default},'.format(
                    type=type_conversion[socket['data-type']],
                    name=code_generator_util.string_capitalized_no_space(socket['name']),
                    default=socket['default'] if socket['data-type'] not in ['Vector', 'RGBA', 'Shader'] else
                    'point({0})'.format(socket['default'].replace(',', ', ')))
                    for socket in sockets if socket['type'] == 'Input']),
                out_sockets=','.join(
                    ['output {type} {name} = {default}'.format(
                        type=type_conversion[socket['data-type']],
                        name=code_generator_util.string_capitalized_no_space(socket['name']),
                        default=out_socket_default[socket['data-type']])
                        for socket in sockets if socket['type'] == 'Output']))

            osl_f.write(function)
        code_generator_util.apply_clang_formatting(osl_path, self._gui.get_source_path())

    def generate_node(self):
        self._add_osl_shader()
        self._add_to_node_menu()
        self._add_node_type_id()
        self._add_dna_node_type()
        self._add_node_drawing()
        self._add_cycles_class()
        self._add_node_register()
        self._add_rna_properties()
        self._add_shader_node_file()
        self._add_cycles_class_instance()
        self._add_node_definition()
        self._add_cycles_node()
        self._add_call_node_register()

        svm_manager = svm_code_generator.SVMCompilationManager(self._gui)
        svm_manager.add_svm_shader()
        svm_manager.add_register_svm()
        svm_manager.add_svm_types()

        glsl_manager = GLSLCodeManager(self._gui)
        glsl_manager.add_glsl_shader()

        cmake_manager = CMakeCodeManager(self._gui)
        cmake_manager.add_to_cmake()
