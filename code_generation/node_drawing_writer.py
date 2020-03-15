from os import path

from . import code_generator_util


class NodeDrawingWriter:
    """Write code related to drawing of the node"""
    def __init__(self, gui):
        self._source_path = gui.get_source_path()
        self._node_has_properties = gui.node_has_properties()
        self._props = gui.get_props()
        self._type_suffix_abbreviated = gui.type_suffix_abbreviated()
        self._node_name = gui.get_node_name()

    def write_node_drawing(self):
        """drawnode.c"""
        drawnode_path = path.join(self._source_path, "source", "blender", "editors", "space_node",
                                  "drawnode.c")
        with open(drawnode_path, "r+") as f:
            if self._node_has_properties:
                draw_props = ''
                if self._node_has_properties:
                    prop_lines = []
                    for prop in self._props:
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
                func = 'static void node_shader_buts_{suff}{name}(uiLayout *layout, bContext *UNUSED(C), PointerRNA *ptr)' \
                       '{{{props}}}\n\n'.format(
                    suff='{suff}_'.format(
                        suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                    name=code_generator_util.string_lower_underscored(self._node_name),
                    props=draw_props)
                lines = f.readlines()
                line_i = lines.index("static void node_shader_set_butfunc(bNodeType *ntype)\n") - 1

                lines.insert(line_i, func)

                case = [
                    "case SH_NODE_{SUFF}{name}:\n".format(SUFF="{SUFF}_".format(
                        SUFF=self._type_suffix_abbreviated.upper()) if self._type_suffix_abbreviated else '',
                                                          name=code_generator_util.string_upper_underscored(
                                                              self._node_name)),
                    "ntype->draw_buttons = node_shader_buts_{tex}{name};\n".format(
                        tex="{suff}_".format(
                            suff=self._type_suffix_abbreviated) if self._type_suffix_abbreviated else '',
                        name=code_generator_util.string_lower_underscored(self._node_name)),
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
        code_generator_util.apply_clang_formatting(drawnode_path, self._source_path)
