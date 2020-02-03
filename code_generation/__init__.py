from os import path, SEEK_END, SEEK_SET
import re
from collections import defaultdict

from . import SVMCodeGenerator, CodeGeneratorUtil


class CodeGenerator:
    """Generates code required for a new node"""

    def __init__(self, gui):
        self._gui = gui

    def _add_node_type_id(self):
        """BKE_node.h"""
        with open(path.join(self._gui.get_source_path(), "source", "blender", "blenderkernel", "BKE_node.h"),
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

    def _add_dna_node_type(self):
        """
        DNA_node_types.h
        """
        if CodeGeneratorUtil.uses_dna(self._gui.get_props(), self._gui.get_node_type()):
            dna_path = path.join(self._gui.get_source_path(), "source", "blender", "makesdna", "DNA_node_types.h")
            with open(dna_path, 'r+') as f:
                props = defaultdict(list)
                for prop in self._gui.get_props():
                    if prop['type'] == 'Enum' or prop['type'] == 'Boolean' or prop['type'] == 'Int':
                        props['int'].append(prop['name'])
                    elif prop['type'] == 'String':
                        props['char'].append("{name}[{size}]".format(name=prop['name'], size=prop['size']))
                    elif prop['type'] == 'Float':
                        props['float'].append(prop['name'])
                    else:
                        raise Exception("Invalid Property Type")

                props_definitions = "; ".join(
                    '{key} {names}'.format(key=key, names=", ".join(names)) for key, names in props.items()) + ";"

                struct = 'typedef struct NodeTex{name} {{NodeTexBase base; {props}{pad}}} NodeTex{name};\n\n'.format(
                    name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                    props=props_definitions,
                    pad=' char _pad[{size}];'.format(size=CodeGeneratorUtil.dna_padding_size(self._gui.get_props())) \
                        if CodeGeneratorUtil.dna_padding_size(self._gui.get_props()) != 0 else '')
                text = f.read()
                match = re.search('} NodeTex'[::-1], text[::-1])  # Reversed to find last occurrence
                if match:
                    i = len(text) - match.end()
                    for _ in range(i, len(text)):
                        if text[i] == '\n':
                            break
                        i += 1
                    else:
                        print("No newline found")
                    text = text[:i + 2] + struct + text[i + 2:]

                    f.seek(0)
                    f.write(text)
                    f.truncate()
                else:
                    print("No matches found")
            CodeGeneratorUtil.apply_clang_formatting(dna_path)

            # TODO - Add enums

    def _add_rna_properties(self):
        """rna_nodetree.c"""
        if self._gui.node_has_properties():
            file_path = path.join(self._gui.get_source_path(), "source", "blender", "makesrna", "intern",
                                  "rna_nodetree.c")
            with open(file_path, 'r+') as f:
                props = []
                s_custom_i = 1
                f_custom_i = 3
                uses_dna = CodeGeneratorUtil.uses_dna(self._gui.get_props(), self._gui.get_node_type())
                for prop in self._gui.get_props():
                    if not uses_dna:
                        if prop['type'] == "Enum" or prop['type'] == "Int":
                            custom_i = s_custom_i
                            s_custom_i += 1
                        elif prop['type'] == "Boolean":
                            custom_i = s_custom_i
                        elif prop['type'] == "Float":
                            custom_i = f_custom_i
                            f_custom_i += 1
                    if prop['type'] == "Enum":
                        enum_name = 'rna_enum_node_{tex}{name}_items'. \
                            format(tex='tex_' if self._gui.is_texture_node() else '',
                                   name=CodeGeneratorUtil.string_lower_underscored(prop['name']))

                    props.append('prop = RNA_def_property(srna, "{name}", PROP_{TYPE}, {SUBTYPE});'
                                 'RNA_def_property_{type}_sdna(prop, NULL, "{sdna}"{enum});'
                                 '{enum_items}'
                                 '{prop_range}'
                                 'RNA_def_property_ui_text(prop, "{Name}", "{desc}");'
                                 'RNA_def_property_update(prop, NC_NODE | NA_EDITED, "rna_ShaderNode_socket_update");'.
                        format(
                        name=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                        TYPE=CodeGeneratorUtil.string_upper_underscored(prop['type']),
                        SUBTYPE=prop['sub-type'],
                        type=CodeGeneratorUtil.string_lower_underscored(prop['type']),
                        sdna=CodeGeneratorUtil.string_lower_underscored(
                            prop['name'] if uses_dna else "custom{index}".format(index=custom_i)),
                        enum=', SHD_{NAME}_{PROP}'.format(
                            NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                            PROP=CodeGeneratorUtil.string_upper_underscored(prop['name']))
                        if prop['type'] == "Boolean" else '',
                        enum_items='RNA_def_property_enum_items(prop, {enum_name});'.format(enum_name=enum_name) if
                        prop['type'] == "Enum" else '',
                        prop_range='RNA_def_property_range(prop, {min}, {max});'.format(min=prop['min'],
                                                                                        max=prop['max']) if prop[
                                                                                                                'type'] == "Int" or
                                                                                                            prop[
                                                                                                                'type'] == "Float" else '',
                        Name=CodeGeneratorUtil.string_capitalized_spaced(prop['name']),
                        desc=""))

                func = 'static void def_sh_{tex}{name}(StructRNA *srna)\n' \
                       '{{\n' \
                       'PropertyRNA *prop;\n\n' \
                       '{sdna}' \
                       '{props}\n' \
                       '}}\n\n'.format(tex="tex_" if self._gui.is_texture_node() else '',
                                       name=self._gui.get_node_name().replace(" ", "_").lower(),
                                       sdna='RNA_def_struct_sdna_from(srna, "Node{Tex}{Name}", "storage");\ndef_sh_tex(srna);\n\n'. \
                                       format(Name=CodeGeneratorUtil.string_capitalized_no_space(
                                           self._gui.get_node_name()),
                                           Tex="Tex" if self._gui.is_texture_node() else "")
                                       if self._gui.is_texture_node() else '',
                                       props="\n\n".join(props))
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line == '/* -- Compositor Nodes ------------------------------------------------------ */\n':
                        break
                else:
                    raise Exception("Reached end of file without match")
                lines.insert(i, func)

                f.seek(0, SEEK_SET)
                f.writelines(lines)
                f.truncate()
            CodeGeneratorUtil.apply_clang_formatting(file_path)

    def _add_node_definition(self):
        """NOD_static_types.h"""
        with open("/".join((self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")),
                  "r") as f:
            lines = f.readlines()

            node_definition = 'DefNode(ShaderNode,     ' + \
                              'SH_NODE_' + "_".join(("TEX" if self._gui.is_texture_node() else "",
                                                     CodeGeneratorUtil.string_upper_underscored(
                                                         self._gui.get_node_name()))) + \
                              ',' + ('def_sh_' + CodeGeneratorUtil.string_lower_underscored(
                self._gui.get_node_name()) if self._gui.node_has_properties() else '0') + \
                              ', ' + (
                                  'Tex' if self._gui.is_texture_node() else '') + CodeGeneratorUtil.string_capitalized_no_space(
                self._gui.get_node_name()) + \
                              ', ' + CodeGeneratorUtil.string_capitalized_spaced(
                self._gui.get_node_name()) + ',  ""   ' + ")"
            print(node_definition)

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
                        if prop['type'] == "Enum":
                            name = '""'
                        elif prop['type'] == "String":
                            name = 'IFACE_("{name}")'.format(
                                name=CodeGeneratorUtil.string_capitalized_spaced(prop['name']))
                        prop_lines.append(
                            'uiItemR(layout, ptr, "{propname}", 0, {name}, ICON_NONE);'.format(propname=prop['name'],
                                                                                               name=name))

                    draw_props = ''.join(prop_lines)
                func = 'static void node_shader_buts_{name}(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)' \
                       '{{{props}}}\n\n'.format(
                    name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                    props=draw_props)
                lines = f.readlines()
                line_i = lines.index("static void node_shader_set_butfunc(bNodeType *ntype)\n") - 1

                lines.insert(line_i, func)

                case = [
                    "case SH_NODE_{tex}{name}:\n".format(tex="TEX_" if self._gui.is_texture_node() else "",
                                                         name=CodeGeneratorUtil.string_upper_underscored(
                                                             self._gui.get_node_name())),
                    "ntype->draw_buttons = node_shader_buts_{tex}{name};\n".format(
                        tex="tex_" if self._gui.is_texture_node() else "",
                        name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name())),
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
        CodeGeneratorUtil.apply_clang_formatting(drawnode_path)

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
                TYPE=sock['data-type'].upper(), Name=CodeGeneratorUtil.string_capitalized_spaced(sock['name']),
                input_count=1 if sock['type'] == 'Input' else 0,
                default=CodeGeneratorUtil.fill_socket_default(sock['default']), min=sock['min'] + 'f',
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
                name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                sockets="".join(sockets_in))
            out.append(in_sockets_text)

        if len(sockets_out) > 0:
            out_sockets_text = 'static bNodeSocketTemplate sh_node_{tex}{name}_out[] = {{{sockets}{{-1, 0, ""}},}};\n\n'.format(
                tex="tex_" if self._gui.is_texture_node() else "",
                name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
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
        uses_dna = CodeGeneratorUtil.uses_dna(self._gui.get_props(), self._gui.get_node_type())
        if uses_dna:
            struct = 'tex' if self._gui.is_texture_node() else 'attr'
            defaults = []
            for prop in props:
                if prop['type'] == 'Enum':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                        default='SHD_{NAME}_{PROP}'.format(
                            NAME=CodeGeneratorUtil.string_upper_underscored(
                                self._gui.get_node_name()),
                            PROP=CodeGeneratorUtil.string_upper_underscored(
                                prop['default']))))
                elif prop['type'] == 'Boolean' or prop['type'] == 'Int':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                        default=prop['default']))
                elif prop['type'] == 'Float':
                    defaults.append('{struct}->{prop} = {default};'.format(
                        struct=struct,
                        prop=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                        default='{default}f'.format(default=prop['default'])))
            prop_init = ''.join(defaults)
        else:  # Use custom
            defaults = []
            s_custom_i = 1
            f_custom_i = 3
            boolean_bit = 0
            for prop in props:
                if prop['type'] == 'Enum':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i,
                                                                          default='SHD_{NAME}_{PROP}'.format(
                                                                              NAME=CodeGeneratorUtil.string_upper_underscored(
                                                                                  self._gui.get_node_name()),
                                                                              PROP=CodeGeneratorUtil.string_upper_underscored(
                                                                                  prop['default']))))
                    s_custom_i += 1
                elif prop['type'] == 'Int':
                    defaults.append('node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    s_custom_i += 1
                elif prop['type'] == 'Boolean':
                    # Need to set bits if multiple bools
                    if len([prop for prop in props if prop['type'] == 'Boolean']) == 1:
                        defaults.append(
                            'node->custom{i} = {default};'.format(i=s_custom_i, default=prop['default']))
                    else:
                        # Set nth bit
                        defaults.append('node->custom{i} |= {default} << {boolean_bit};'.format(
                            i=s_custom_i,
                            default=int(prop['default']),
                            boolean_bit=boolean_bit))
                        boolean_bit += 1
                elif prop['type'] == 'Float':
                    defaults.append('node->custom{i} = {default}f;'.format(i=f_custom_i, default=prop['default']))
            prop_init = ''.join(defaults)

        init_func = 'static void node_shader_init_{tex}{name}(bNodeTree *UNUSED(ntree), bNode *node){{' \
                    '{get_storage}' \
                    '{texture_mapping}' \
                    '{prop_init}\n\n' \
                    '{set_storage}' \
                    '}}\n\n'.format(
            tex='tex_' if self._gui.is_texture_node() else '',
            name=CodeGeneratorUtil.string_lower_underscored(
                self._gui.get_node_name()),
            Tex='Tex' if self._gui.is_texture_node() else '',
            get_storage='Node{Tex}{Name} *{struct} = MEM_callocN(sizeof(Node{Tex}{Name}), "Node{Tex}{Name}");'.format(
                Tex='Tex' if self._gui.is_texture_node() else '',
                Name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                struct=struct) if uses_dna else '',
            Name=CodeGeneratorUtil.string_capitalized_no_space(
                self._gui.get_node_name()),
            texture_mapping='BKE_texture_mapping_default(&tex->base.tex_mapping, TEXMAP_TYPE_POINT);'
                            'BKE_texture_colormapping_default(&tex->base.color_mapping);'
            if self._gui.is_texture_node() else '',
            prop_init=prop_init,
            set_storage='node->storage = {struct};'.format(struct=struct) if uses_dna else '')
        return init_func

    def _generate_node_shader_gpu(self):
        """
        Generate node gpu function code
        :return: gpu function as text
        """
        props = self._gui.get_props()
        dropdowns = list(filter(lambda p: p['type'] == 'Enum', props))
        dropdown_count = len(dropdowns)
        uses_dna = CodeGeneratorUtil.uses_dna(props, self._gui.get_node_type())
        names = ''
        func_name = 'node_{tex}{name}'.format(tex='tex_' if self._gui.is_texture_node() else '',
                                              name=CodeGeneratorUtil.string_lower_underscored(
                                                  self._gui.get_node_name()))
        if dropdown_count == 1:
            prop = dropdowns[0]
            names = 'static const char *names[] = {{' \
                    '"",' \
                    '{funcs}' \
                    '}};\n\n'.format(funcs=''.join('"node_{tex}{name}_{option}",'.format(
                tex='tex_' if self._gui.is_texture_node() else '',
                name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                option=CodeGeneratorUtil.string_lower_underscored(option)) for option in prop['options']))
            func_name = 'names[{struct}->{name}]'.format(
                struct='tex' if self._gui.is_texture_node() else 'attr',
                name=CodeGeneratorUtil.string_lower_underscored(
                    dropdowns[0]['name'])) if uses_dna else 'names[node->custom1]'
        elif dropdown_count == 2:
            names = 'static const char *names[][{count}] = {{' \
                    '{funcs}' \
                    '}};\n\n'.format(count=len(dropdowns[0]['options']),
                                     funcs=''.join(['[SHD_{NAME}_{OPTION}] = '
                                                    '{{"",{func_names}}},'.format(
                                         NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                         OPTION=CodeGeneratorUtil.string_upper_underscored(option1),
                                         func_names=''.join('"node_{name}_{option1}_{option2}",'.format(
                                             name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                                             option1=option1, option2=option2)
                                                            for option2 in dropdowns[1]['options']))
                                         for option1 in dropdowns[0]['options']]))
            func_name = 'names[{struct}->{drop1}][{struct}->{drop2}]'.format(
                struct='tex' if self._gui.is_texture_node() else 'attr',
                drop1=CodeGeneratorUtil.string_lower_underscored(dropdowns[0]['name']),
                drop2=CodeGeneratorUtil.string_lower_underscored(
                    dropdowns[1]['name'])) if uses_dna else 'names[node->custom1][node->custom2]'
        elif dropdown_count > 2:
            names = '/* GLSL function names to be implemented here */\n\n'

        # Props + Other params
        type_map = {'Int': 'int', 'Boolean': 'bool', 'Float': 'float', 'String': ''}
        retrieved_props = []
        if uses_dna:
            struct = 'tex' if self._gui.is_texture_node() else 'attr'
            for prop in props:
                prop_name = CodeGeneratorUtil.string_lower_underscored(prop['name'])
                if prop['type'] == 'Boolean':
                    retrieved_props.append('float {name} = ({struct}->{name}) ? 1.0f : 0.0f;'.format(
                        name=prop_name,
                        struct=struct))
                elif prop['type'] != 'String' and prop['type'] != 'Enum':
                    retrieved_props.append('float {name} = {struct}->{name};'.format(
                        name=prop_name,
                        struct=struct))
        else:
            struct = 'tex' if self._gui.is_texture_node() else 'attr'
            s_custom_i = 1
            f_custom_i = 3
            boolean_bit = 0
            for prop in props:
                prop_name = CodeGeneratorUtil.string_lower_underscored(prop['name'])
                if prop['type'] == 'Boolean':
                    # Need to get individual bits if multiple bools
                    if len([prop for prop in props if prop['type'] == 'Boolean']) > 1:
                        retrieved_props.append(
                            'float {name} = ({struct}->custom{i}) ? 1.0f : 0.0f;'.format(name=prop_name,
                                                                                         struct=struct,
                                                                                         i=s_custom_i))
                    else:
                        retrieved_props.append(
                            'float {name} = (({struct}->custom{i} >> {boolean_bit} & 1) ? 1.0f : 0.0f;'.format(
                                name=prop_name,
                                struct=struct,
                                i=s_custom_i,
                                boolean_bit=boolean_bit))
                        boolean_bit += 1
                elif prop['type'] == 'Float':
                    retrieved_props.append('float {name} = node->custom{i};'.format(name=prop_name,
                                                                                    struct=struct,
                                                                                    i=f_custom_i))
                    f_custom_i += 1
                elif prop['type'] == 'Int':
                    retrieved_props.append('float {name} = node->custom{i};'.format(name=prop_name,
                                                                                    struct=struct,
                                                                                    i=s_custom_i))
                    s_custom_i += 1
        other_params = ', ' + ', '.join(
            'GPU_constant(&{prop})'.format(prop=CodeGeneratorUtil.string_lower_underscored(prop['name'])) for
            prop in list(filter(lambda p: p['type'] != 'Enum' and p['type'] != 'String', props))) \
            if len(props) - dropdown_count > 0 else ''

        assertions = []
        custom_i = 1
        for prop in dropdowns:
            if CodeGeneratorUtil.uses_dna(props, self._gui.get_node_type()):
                assertions.append('BLI_assert({struct}->{prop} >= 0 && {struct}->{prop} < {option_count});'.format(
                    struct=struct, prop=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                    option_count=len(prop['options']) + 1))
            else:
                assertions.append('BLI_assert(node->custom{i} >= 0 && node->custom{i} < {option_count});'.format(
                    i=custom_i, option_count=len(prop['options']) + 1
                ))
                custom_i += 1

        if len(retrieved_props) > 0:
            retrieved_props.append('\n\n')

        if len(assertions) > 0:
            assertions.append('\n\n')

        dna = '{get_struct}' \
              '{get_props}' \
              '{assertions}'.format(
            get_struct='Node{Tex}{Name} *{struct} = (Node{Tex}{Name} *)node->storage;'.format(
                Tex='Tex' if self._gui.is_texture_node() else '',
                Name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                struct=struct) if len(props) - dropdown_count > 0 else '',
            get_props=''.join(retrieved_props),
            assertions=''.join(assertions))

        gpu_text = 'static int node_shader_gpu_{tex}{name}(GPUMaterial *mat,' \
                   ' bNode *node, ' \
                   'bNodeExecData *UNUSED(execdata), ' \
                   'GPUNodeStack *in, ' \
                   'GPUNodeStack *out)' \
                   '{{' \
                   '{texture_mapping}' \
                   '{func_names}' \
                   '{dna}' \
                   'return GPU_stack_link(mat, node, {func_name}, in, out{other_params});' \
                   '}}\n\n'.format(
            tex='tex_' if self._gui.is_texture_node() else '',
            name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
            texture_mapping='node_shader_gpu_default_tex_coord(mat, node, &in[0].link);node_shader_gpu_tex_mapping(mat, node, in, out);\n\n'
            if self._gui.is_texture_node() else '',
            func_names=names,
            dna=dna,
            func_name=func_name,
            other_params=other_params)
        return gpu_text

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
                Name = CodeGeneratorUtil.string_capitalized_no_space(map['socket-name'])
                socket_get = 'bNodeSocket *{type}{Name}Sock = nodeFindSocket(node, SOCK_{TYPE}, "{Name}");'.format(
                    type=type,
                    Name=Name,
                    TYPE=map['socket-type'].upper())
                if map['socket-type'] == 'in':
                    in_sockets.append(socket_get)
                else:
                    out_sockets.append(socket_get)

                constraints = []
                avail_count = sum(avail for prop, avail in map['prop-avail'])
                invert_avail = avail_count / len(map['prop-avail']) < 0.5
                if CodeGeneratorUtil.uses_dna(props, self._gui.get_node_type()):
                    for prop, avail in map['prop-avail']:
                        prop_name, value = prop.split('=')
                        is_enum = not (value == 'False' or value == 'True')
                        if not invert_avail and not avail:
                            constraints.append('{struct}->{prop} != {value}'.format(
                                struct=struct,
                                prop=CodeGeneratorUtil.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                    OPTION=CodeGeneratorUtil.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                        elif invert_avail and avail:
                            constraints.append('{struct}->{prop} == {value}'.format(
                                struct=struct,
                                prop=CodeGeneratorUtil.string_lower_underscored(prop_name),
                                value='SHD_{NAME}_{OPTION}'.format(
                                    NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                    OPTION=CodeGeneratorUtil.string_upper_underscored(value))
                                if is_enum else int(value == 'True')))
                else:
                    bool_count = len(list(filter(lambda p: p['type'] == 'Boolean', props)))
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
                                    prop=CodeGeneratorUtil.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                        OPTION=CodeGeneratorUtil.string_upper_underscored(value))
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
                                    prop=CodeGeneratorUtil.string_lower_underscored(prop_name),
                                    value='SHD_{NAME}_{OPTION}'.format(
                                        NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                        OPTION=CodeGeneratorUtil.string_upper_underscored(value))
                                    if is_enum else int(value == 'True')))
                socket_availability.append('nodeSetSocketAvailability({socket}, {constraints});'.format(
                    socket='{type}{Name}Sock'.format(type=type, Name=Name),
                    constraints=' || '.join(constraints) if invert_avail else ' && '.join(constraints)))

        if len(in_sockets) > 0:
            in_sockets.append('\n\n')
        if len(out_sockets) > 0:
            out_sockets.append('\n\n')
        get_struct = 'Node{Tex}{Name} *{struct} = (Node{Tex}{Name} *)node->storage;\n\n'.format(
            Tex='Tex' if self._gui.is_texture_node() else '',
            Name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
            struct='tex' if self._gui.is_texture_node() else 'attr')

        socket_availability_func = 'static void node_shader_update_{tex}{name}(bNodeTree *UNUSED(ntree), bNode *node)' \
                                   '{{' \
                                   '{in_sockets}' \
                                   '{out_sockets}' \
                                   '{struct}' \
                                   '{availability}' \
                                   '}}\n\n'.format(
            tex='tex_' if self._gui.is_texture_node() else '',
            name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
            in_sockets=''.join(in_sockets),
            out_sockets=''.join(out_sockets),
            struct=get_struct if CodeGeneratorUtil.uses_dna(props, self._gui.get_node_type()) else '',
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
                        'node_type_gpu(&ntype, node_shader_gpu_{tex}{name});' \
                        '{update}\n\n' \
                        'nodeRegisterType(&ntype);' \
                        '}}\n'.format(tex='tex_' if self._gui.is_texture_node() else '',
                                      name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                                      TEX='TEX_' if self._gui.is_texture_node() else '',
                                      NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()),
                                      Name=CodeGeneratorUtil.string_capitalized_spaced(self._gui.get_node_name()),
                                      CLASS=self._gui.get_node_group().upper(),
                                      init='node_type_init(&ntype, node_shader_init_{tex}{name});'.format(
                                          tex='tex_' if self._gui.is_texture_node() else '',
                                          name=CodeGeneratorUtil.string_lower_underscored(
                                              self._gui.get_node_name())) if self._gui.node_has_properties() else '',
                                      storage='node_type_storage(&ntype, "Node{Tex}{Name}", node_free_standard_storage, node_copy_standard_storage);'.format(
                                          Tex='Tex' if self._gui.is_texture_node() else '',
                                          Name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name())
                                      )
                                      if CodeGeneratorUtil.uses_dna(
                                          self._gui.get_props(),
                                          self._gui.get_node_type()) else 'node_type_storage(&ntype, "", NULL, NULL);',
                                      Tex='Tex' if self._gui.is_texture_node() else '',
                                      update='node_type_update(&ntype, node_shader_update_{tex}{name});'.format(
                                          tex='tex_' if self._gui.is_texture_node() else '',
                                          name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()))
                                      if self._gui.socket_availability_changes() else '')
        return register_text

    def _add_shader_node_file(self):
        """node_shader_*.c"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "shader", "nodes",
                              "node_shader_{tex}{name}.c".format(
                                  tex="tex_" if self._gui.is_texture_node() else "",
                                  name=CodeGeneratorUtil.string_lower_underscored(
                                      self._gui.get_node_name())))
        with open(file_path, "w") as f:
            CodeGeneratorUtil.write_license(f)

            file_lines = ['', '#include "../node_shader_util.h"\n\n', '/**************** {NAME} ****************/\n\n'.
                format(NAME=CodeGeneratorUtil.string_upper_underscored(self._gui.get_node_name()))]

            file_lines.append(self._generate_node_shader_sockets())

            file_lines.append(self._generate_node_shader_init())

            file_lines.append(self._generate_node_shader_gpu())

            file_lines.append(self._generate_node_shader_socket_availability())

            file_lines.append(self._generate_node_shader_register())

            f.writelines(file_lines)

        CodeGeneratorUtil.apply_clang_formatting(file_path)

    def _add_node_register(self):
        """NOD_shader.h"""
        file_path = path.join(self._gui.get_source_path(), "source", "blender", "nodes", "NOD_shader.h")
        with open(file_path, 'r+') as f:

            func = 'void register_node_type_sh_{tex}{name}(void);\n'. \
                format(tex="tex_" if self._gui.is_texture_node() else '',
                       name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()))

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

    def _add_cycles_class(self):
        """nodes.h"""
        file_path = path.join(self._gui.get_source_path(), "intern", "cycles", "render", "nodes.h")
        with open(file_path, 'r+') as f:
            props = defaultdict(list)
            types_convert = {"Boolean": "bool", "Int": "int", "Float": "float", "Enum": "int", "Vector": "float3",
                             "RGBA": "float3", "String": "ustring"}
            for socket in list(filter(lambda s: s['type'] == 'Input', self._gui.get_node_sockets())):
                props[types_convert[socket['data-type']]].append(socket['name'])

            for prop in self._gui.get_props():
                if prop['type'] != "String":
                    props[types_convert[prop['type']]].append(prop['name'])
                else:
                    props['char'].append('{name}[{size}]'.format(name=prop['name'], size=prop['size']))

            props_string = "".join(
                '{type} {names};'.format(type=type, names=", ".join(names)) for type, names in props.items())

            node = "class {name}{tex}Node : public {type}Node {{" \
                   "public:" \
                   "SHADER_NODE_CLASS({name}Node)" \
                   "{node_group}" \
                   "{props}" \
                   "}};".format(name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
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
        CodeGeneratorUtil.apply_clang_formatting(file_path)

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
                Name=CodeGeneratorUtil.string_capitalized_no_space(
                    self._gui.get_node_name()),
                tex='tex_' if self._gui.is_texture_node() else '',
                name=CodeGeneratorUtil.string_lower_underscored(
                    self._gui.get_node_name()),
                Texture='Texture' if self._gui.is_texture_node() else '',
                props=''.join(
                    ['{name}->{prop} = b_{tex}{name}_node.{prop}();'.format(
                        name=CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name()),
                        prop=prop['name'],
                        tex='tex_' if self._gui.is_texture_node() else '') for prop in props]),
                texture_mapping='BL::TexMapping b_texture_mapping(b_tex_{name}_node.texture_mapping());'
                                'get_tex_mapping(&{name}->tex_mapping, b_texture_mapping);'.format(
                    name=CodeGeneratorUtil.string_lower_underscored(
                        self._gui.get_node_name())) if self._gui.is_texture_node() else '') \
                if len(props) > 0 or self._gui.is_texture_node() else \
                'else if (b_node.is_a(&RNA_ShaderNode{Name})) {{' \
                'node = new {Name}Node();}}\n'.format(
                    Name=CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()))

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
        CodeGeneratorUtil.apply_clang_formatting(file_path)

    def _add_cycles_node(self):
        """nodes.cpp"""
        pass

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
                    lines.insert(i, '        NodeItem("ShaderNode{0}{1}"{2})\n'.format(
                        "Tex" if self._gui.is_texture_node() else "",
                        CodeGeneratorUtil.string_capitalized_no_space(self._gui.get_node_name()),
                        (', poll={0}'.format(self._gui.get_poll()) if self._gui.get_poll() is not None else '')))
                    lines[i - 1] = lines[i - 1][:len(lines[i - 1]) - 1] + ',\n'
                    break
            else:
                print("End not found")

            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def _add_osl_shader(self):
        """"""
        node_name_underscored = CodeGeneratorUtil.string_lower_underscored(self._gui.get_node_name())
        osl_path = path.join(self._gui.get_source_path(), "intern", "cycles", "kernel", "shaders",
                             "node_" + node_name_underscored + ".osl")
        with open(osl_path, "w+") as osl_f:
            CodeGeneratorUtil.write_license(osl_f)
            osl_f.write('#include "stdosl.h"\n\n')

            props = self._gui.get_props()
            sockets = self._gui.get_node_sockets()

            type_conversion = {"Boolean": "int", "String": "string", "Int": "int", "Float": "float", "Enum": "string"}

            function = "shader node_{name}{tex}({mapping}{props}{in_sockets}{out_sockets}){{}}".format(
                name=node_name_underscored,
                tex='_texture' if self._gui.is_texture_node() else '',
                mapping='int use_mapping = 0,matrix mapping = matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),'
                if self._gui.is_texture_node() else '',
                props=''.join('{type} {name} = {default},'.format(
                    type=type_conversion[prop['type']],
                    name=CodeGeneratorUtil.string_lower_underscored(prop['name']),
                    default='"{default}"'.format(default=prop['default']) if prop['type'] == 'Enum' else prop[
                        'default'])
                              for prop in props if prop['type'] != 'String'),
                in_sockets=''.join(['{type} {name} = {default},'.format(type=type_conversion[socket['data-type']],
                                                                        name=socket['name'],
                                                                        default=socket['default'])
                                    for socket in sockets if socket['type'] == 'Input']),
                out_sockets=','.join(
                    ['output {type} {name} = {default}'.format(type=type_conversion[socket['data-type']],
                                                               name=socket['name'],
                                                               default=socket['default'])
                     for socket in sockets if socket['type'] == 'Output']))

            osl_f.write(function)
        CodeGeneratorUtil.apply_clang_formatting(osl_path)

    def _add_svm_shader(self):
        """"""
        pass

    def _add_glsl_shader(self):
        """"""
        pass

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
