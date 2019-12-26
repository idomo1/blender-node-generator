"""
A script which generates code for a basic blender node
Confirmed to work with Blender 2.8
"""

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import ttk
import copy
from pprint import pprint


class GUI:
    """Handles the GUI for entering data"""
    def __init__(self):
        self._window_title = 'Blender Node Generator'
        self._window_size = '1200x500'

    def display(self):
        """Main driver to display the menu"""
        self.window = Tk()

        self.window.title(self._window_title)
        self.window.geometry(self._window_size)

        tab_control = ttk.Notebook(self.window)

        # General Tab
        general_tab = ttk.Frame(tab_control)
        tab_control.add(general_tab, text='General')
        tab_control.pack(expand=1, fill='both')
        self._general_GUI = GeneralGUI(general_tab)
        self._general_GUI.display()

        # Dropdown Tab 1
        dropdown_tab1 = ttk.Frame(tab_control)
        tab_control.add(dropdown_tab1, text='Dropdown 1')
        tab_control.pack(expand=1, fill='both')
        self._dropdown_GUI1 = DropdownGUI(dropdown_tab1)
        self._dropdown_GUI1.display()

        # Dropdown Tab 2
        dropdown_tab2 = ttk.Frame(tab_control)
        tab_control.add(dropdown_tab2, text='Dropdown 2')
        tab_control.pack(expand=1, fill='both')
        self._dropdown_GUI2 = DropdownGUI(dropdown_tab2)
        self._dropdown_GUI2.display()

        # CheckBox Tab
        check_box_tab = ttk.Frame(tab_control)
        tab_control.add(check_box_tab, text='Check Boxes')
        tab_control.pack(expand=1, fill='both')
        self._check_box_GUI = CheckBoxGUI(check_box_tab)
        self._check_box_GUI.display()

        # Sockets Tab
        sockets_tab = ttk.Frame(tab_control)
        tab_control.add(sockets_tab, text='Socket Definitions')
        tab_control.pack(expand=1, fill='both')
        self._socket_GUI = SocketDefinitionsGUI(sockets_tab)
        self._socket_GUI.display()

        # Socket Availability Tab
        socket_tab = ttk.Frame(tab_control)
        tab_control.add(socket_tab, text='Socket Availability')
        tab_control.pack(expand=1, fill='both')
        self._socket_avail_GUI = SocketAvailabilityGUI(socket_tab, self._dropdown_GUI1, self._dropdown_GUI2, self._socket_GUI)
        self._socket_avail_GUI.display()

        # Generate Button
        self.generate_button = Button(self.window, text='Generate', width=25, command=self.generate_node)
        self.generate_button.pack()

        self.window.mainloop()

    def _is_input_valid(self):
        return self._general_GUI.is_input_valid() and \
               self._dropdown_GUI1.is_input_valid() and \
               self._check_box_GUI.is_input_valid()

    def get_source_path(self):
        return self._general_GUI.get_source_path()

    def get_node_name(self):
        return self._general_GUI.get_node_name()

    def get_node_type(self):
        return self._general_GUI.get_node_type()

    def node_has_properties(self):
        return len(self._dropdown_GUI1.get_dropdown_properties()) > 0 and len(self._dropdown_GUI2.get_dropdown_properties()) > 0

    def node_has_check_box(self):
        return len(self._check_box_GUI.get_check_box_properties()) > 0

    def generate_node(self):
        if self._is_input_valid():
            print(self._general_GUI.get_node_name())
            print(self._general_GUI.get_node_type())
            print(self._general_GUI.get_source_path())

            print(self._check_box_GUI.get_check_box_properties())

            print(self._dropdown_GUI1.get_dropdown_properties())
            print(self._socket_GUI.get_io())
            print(self._socket_avail_GUI.get_maps())

            code_generator = CodeGenerator(self)
            code_generator.generate_node()

            messagebox.showinfo('Done', 'Node has been generated')


class GeneralGUI:
    def __init__(self, tab):
        self._row_i = 0 # Counts the rows which have been filled, methods are responsible for incrementing this value
        self._window = tab
        self._node_types = ['Input', 'Output', 'Shader', 'Texture', 'Color', 'Vector', 'Converter', 'Script', 'Group',
                            'Layout']

    def _name_input_display(self):
        """Input for the name of the new node"""
        Label(self._window, text='Node Name', pad=5).grid(row=self._row_i)
        self._name_input = Entry(self._window)
        self._name_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _type_input_display(self):
        """Input for the type of the new node"""
        Label(self._window, text='Node Type', pad=3).grid(row=self._row_i)
        self._type_input = Combobox(self._window)
        self._type_input['values'] = self._node_types
        self._type_input.current(2)
        self._type_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _blender_path_input_display(self):
        """Path to the root directory of the blender source files"""
        Label(self._window, text='Blender Source Path', pad=3).grid(row=self._row_i)
        self._path_input = Entry(self._window)
        self._path_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def display(self):
        self._name_input_display()
        self._type_input_display()
        self._blender_path_input_display()

    def get_node_name(self):
        return self._name_input.get()

    def get_node_type(self):
        return self._type_input.get()

    def get_source_path(self):
        return self._path_input.get()

    def is_input_valid(self):
        node_name = self.get_node_name().lower()
        if node_name is "":
            messagebox.showerror('Bad Input', 'Node name must be provided')
            return False
        if ord(node_name[0]) < 97 or ord(node_name[0]) > 122:
            messagebox.showerror('Bad Input', 'Node name first character must be a letter or _')
            return False
        if self.get_node_type() not in self._node_types:
            messagebox.showerror('Bad Input', 'Invalid node type')
            return False
        return True


class DropdownGUI:
    """GUI for configuring a nodes dropdown menus"""
    def __init__(self, tab):
        self._row_i = 0  # Counts the rows which have been filled, methods are responsible for incrementing this value
        self.window = tab
        self._enabled = IntVar()
        self._properties = []

    def _add_dropdown_property(self):
        """Adds a new dropdown property"""
        property = RemovableTextInput(self.window, 'Property')
        self._properties.append(property)
        self._properties[-1].grid(row=self._row_i)
        self._row_i += 1

    def _toggle_enabled(self):
        self._add_property_button['state'] = DISABLED if str(self._add_property_button['state']) == 'normal' else NORMAL
        for component in self._properties:
            component.toggle_enabled()

    def _dropdown_properties_display(self):
        Label(self.window, text='Enabled').grid(row=self._row_i)
        Checkbutton(self.window, variable=self._enabled, command=self._toggle_enabled).grid(row=self._row_i, column=1)
        self._row_i += 1

        self._add_property_button = Button(self.window, text='Add Property', command=self._add_dropdown_property)
        self._add_property_button.grid(row=self._row_i, column=1)
        self._row_i += 1

    def display(self):
        self._dropdown_properties_display()
        self._toggle_enabled()  # Initially disabled

    def get_dropdown_properties(self):
        return list(filter(lambda p: p is not None, map(lambda p: p.get_input(), self._properties)))

    def is_input_valid(self):
        return True


class CheckBoxGUI:
    """GUI for configuring a nodes check boxes"""
    def __init__(self, tab):
        self._row_i = 0  # Counts the rows which have been filled, methods are responsible for incrementing this value
        self.window = tab
        self._check_box_menus = []
        self._default_values = []

    def _check_box_input_display(self):
        """Input for check box properties"""
        frame = Frame(self.window, pad=5)

        name_label = Label(frame, text='Checkbox Label')
        name_label.grid(row=self._row_i)
        name_input = Entry(frame)
        name_input.grid(row=self._row_i, column=1)

        value_label = Label(frame, text='Default Value')
        value_label.grid(row=self._row_i, column=2)

        self._default_values.append(IntVar())
        default_value = Checkbutton(frame, var=self._default_values[-1])
        default_value.grid(row=self._row_i, column=3)

        frame.grid(column=0)
        return frame

    def _update_check_box_menus(self, event):
        """Adds windows to enter options based on the no. of check boxes required"""
        for check_box in self._check_box_menus:
            check_box.destroy()
        self._default_values.clear()
        self._check_box_menus = [self._check_box_input_display() for _ in range(int(self._count_input.get()))]

    def _check_box_count_display(self):
        """Input for the no. of check box's the new node needs"""
        self._count_input = Combobox(self.window)
        self._count_input['values'] = [i for i in range(15)]
        self._count_input.current(0)
        self._count_input.bind("<<ComboboxSelected>>", self._update_check_box_menus)
        Label(self.window, text='Node Dropdown Count', pad=3).grid(row=self._row_i)
        self._row_i += 1
        self._count_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def display(self):
        self._check_box_count_display()

    def get_check_box_count(self):
        return int(self._count_input.get())

    def get_check_box_properties(self):
        check_box_properties = [{} for _ in range(self.get_check_box_count())]
        for i, check_box in enumerate(self._check_box_menus):
            check_box_properties[i]["name"] = check_box.children['!entry'].get()
            check_box_properties[i]["default"] = self._default_values[i].get()

        return check_box_properties

    def is_input_valid(self):
        count = self.get_check_box_count()
        if count < 0 or count > 15:
            messagebox.showerror('Bad Input', 'Check box count must be between 0-15')
            return False
        return True


class SocketDefinitionsGUI:
    """GUI for entering input and output sockets for the node"""
    def __init__(self, tab):
        self.window = tab
        self._row_i = 0
        self._ios = []

    def _add_node_io(self):
        io = RemovableSocketDefinitionInput(self.window, 'IO')
        self._ios.append(io)
        io.grid(row=self._row_i)
        self._row_i += 1

    def display(self):
        Button(self.window, text='Add I/O', command=self._add_node_io).grid(row=self._row_i)
        self._row_i += 1

    def get_io(self):
        return list(filter(lambda p: p is not None, map(lambda p: p.get_input(), self._ios)))


class SocketAvailabilityGUI:
    """Socket availability"""
    def __init__(self, tab, dropdown_GUI1, dropdown_GUI2, IO_GUI):
        self._row_i = 0
        self.window = tab
        self._maps = {}
        self._dropdown1_GUI = dropdown_GUI1
        self._dropdown2_GUI = dropdown_GUI2
        self._IO_GUI = IO_GUI

    def _remove_existing_menu(self):
        """Removes the existing menu for the selected menu item"""
        for element in list(self.window.children.keys()):
            if type(self.window.children[element]) == Checkbutton or type(self.window.children[element]) == Label:
                self.window.children[element].destroy()

    def _update_options(self, event=None):
        """For when dropdown options are changed"""
        self._dropdown['values'] = self._dropdown1_GUI.get_dropdown_properties() + self._dropdown2_GUI.get_dropdown_properties()

    def _display_mapping(self, map_key):
        self._remove_existing_menu()
        for socket in self._maps[map_key]:
            Label(self.window, text=socket).grid(row=self._row_i)
            Checkbutton(self.window, var=self._maps[map_key][socket]).grid(row=self._row_i, column=1)
            self._row_i += 1

    def _remove_deleted_sockets(self):
        sockets = self._IO_GUI.get_io()
        for key in list(self._maps[self._dropdown.get()].keys()):
            for socket in sockets:
                if type(socket) is dict:
                    if key == socket['name']:
                        break
                else:
                    if key == socket:
                        break
            else:
                del self._maps[self._dropdown.get()][key]

    def _on_selected(self, event):
        sockets = self._IO_GUI.get_io()
        if self._dropdown.get() not in self._maps:
            vars = [BooleanVar() for _ in range(len(sockets))]
            for var in vars:
                var.set(True)
                self._maps[self._dropdown.get()] = dict()
            for i, socket in enumerate(sockets):
                self._maps[self._dropdown.get()][socket if type(socket) is not dict else socket['name']] = vars[i]
        else:
            for socket in sockets:
                if type(socket) is dict and socket['name'] not in self._maps[self._dropdown.get()]:
                    var = BooleanVar()
                    var.set(True)
                    self._maps[self._dropdown.get()][socket['name']] = var
                elif type(socket) is not dict and socket not in self._maps[self._dropdown.get()]:
                    var = BooleanVar()
                    var.set(True)
                    self._maps[self._dropdown.get()][socket] = var
        self._remove_deleted_sockets()
        self._display_mapping(self._dropdown.get())

    def display(self):
        Button(self.window, text='Refresh', command=self._update_options).grid(row=self._row_i)
        self._row_i += 1
        self._dropdown = Combobox(self.window)
        self._dropdown['values'] = self._dropdown1_GUI.get_dropdown_properties()
        self._dropdown.bind('<<ComboboxSelected>>', self._on_selected)
        self._dropdown.grid(row=self._row_i)
        self._row_i += 1

    def get_map(self, name):
        self._remove_deleted_sockets()
        return copy.deepcopy(self._maps[name])

    def get_maps(self):
        self._remove_deleted_sockets()
        return {dropdown: {socket: value.get() for socket, value in self._maps[dropdown].items()} for dropdown in self._maps}


class RemovableTextInput(Frame):
    """A text entry component which is removable through a button input"""

    def __init__(self, window, label):
        super().__init__(window)
        Label(self, text=label).grid(row=0, column=0)
        Entry(self).grid(row=0, column=1)
        Button(self, text='Remove', command=self.destroy).grid(row=0, column=2)

    def toggle_enabled(self):
        for component in self.children.values():
            component['state'] = DISABLED if str(component['state']) == 'normal' else NORMAL

    def get_input(self):
        return self.children['!entry'].get() if '!entry' in self.children else None


class RemovableSocketDefinitionInput(Frame):
    """Node IO Template"""
    def __init__(self, window, label):
        super().__init__(window)

        col_i = 0

        Label(self, text=label).grid(row=0, column=col_i)
        col_i += 1
        type = Combobox(self)
        type['values'] = ["Input", "Output"]
        type.current(0)
        type.grid(row=0, column = col_i)
        col_i += 1

        Label(self, text='type').grid(row=0, column=col_i)
        col_i += 1
        data_type = Combobox(self)
        data_type['values'] = ["float", "vector", "color", "slider", "int"]
        data_type.current(0)
        data_type.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Name').grid(row=0, column=col_i)
        col_i += 1
        name = Entry(self)
        name.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Min').grid(row=0, column=col_i)
        col_i += 1
        min = Entry(self)
        min.insert(0, "-1.0")
        min.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Max').grid(row=0, column=col_i)
        col_i += 1
        max = Entry(self)
        max.insert(0, '1.0')
        max.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='default').grid(row=0, column=col_i)
        col_i += 1
        default = Entry(self)
        default.insert(0, '0.0')
        default.grid(row=0, column=col_i)
        col_i += 1

        Button(self, text='Remove', command=self.destroy).grid(row=0, column=col_i)
        col_i += 1

    def get_input(self):
        """Returns None if the input has been destroyed"""
        return {'type' : self.children['!combobox'].get(), 'name' : self.children['!entry'].get(), 'data_type' : self.children['!combobox2'].get(),
                'min' : self.children['!entry2'].get(), 'max' : self.children['!entry3'].get(),
                'default' : self.children['!entry4'].get()} if self.winfo_exists() else None


class CodeGenerator:
    """Generates code required for a new node"""
    def __init__(self, GUI):
        self._gui = GUI

    def _add_node_type_ID(self):
        """BKE_node.h"""
        with open("/".join((self._gui.get_source_path(), "source", "blender", "blenderkernel", "BKE_node.h")), "r") as f:
            last = 707
            name_underscored = "_".join(self._gui.get_node_name().split(" "))
            line = "#define SH_NODE_" + ("TEX_" if self._gui.get_node_type() == "Texture" else "") + name_underscored.upper() + " " + str(last+1)
            print(line)

    def _add_DNA_node_type(self):
        """
        DNA_node_types.h
        For texture nodes
        """
        pass

    def _add_rna_properties(self):
        """rna_nodetree.c"""
        pass

    def _add_node_definition(self):
        """NOD_static_types.h"""
        with open("/".join((self._gui.get_source_path(), "source", "blender", "nodes", "NOD_static_types.h")), "r") as f:
            lines = f.readlines()

            node_name_underscored = self._gui.get_node_name().replace(" ", "_")

            node_definition = 'DefNode(ShaderNode,     ' + \
                              'SH_NODE_' + "_".join(("TEX" if self._gui.get_node_type() == "Texture" else "", node_name_underscored.upper())) + \
                              ',' + ('def_sh_' + node_name_underscored.lower() if self._gui.node_has_properties() else '0') + \
                              ', ' + ('Tex' if self._gui.get_node_type() == "Texture" else '') + self._gui.get_node_name().replace(" ", "") + \
                              ', ' + " ".join(map(lambda word: word.capitalize(), self._gui.get_node_name().split(" "))) + ',  ""   ' + ")"
            print(node_definition)

    def _add_node_drawing(self):
        """drawnode.c"""
        if self._gui.node_has_properties() or self._gui.node_has_check_box():
            pass

    def _add_shader_node_file(self):
        """node_shader_*.c"""
        pass

    def _add_node_register(self):
        """NOD_shader.h"""
        pass

    def _add_cycles_class(self):
        """nodes.h"""
        pass

    def _add_cycles_class_instance(self):
        """blender_shader.cpp"""
        pass

    def _add_cycles_node(self):
        """nodes.cpp"""
        pass

    def _add_to_node_menu(self):
        """nodeitems_builtins.py"""
        pass

    def _add_osl_shader(self):
        """"""
        node_name_underscored = self._gui.get_node_name().replace(" ", "_").lower()
        with open("/".join((self._gui.get_source_path(), "intern", "cycles", "kernel", "shaders", "node_" + node_name_underscored)), "w+") as f:
            f.write()

    def _add_kvm_shader(self):
        """"""
        pass

    def _add_glsl_shader(self):
        """"""
        pass

    def generate_node(self):
        self._add_node_definition()


if __name__ == "__main__":
    menu = GUI()
    menu.display()
