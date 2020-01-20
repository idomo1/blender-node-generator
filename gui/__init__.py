from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import copy


class GUI:
    """
    Handles the GUI for entering data
    code_generator is a class which accepts the gui in the constructor
    """

    def __init__(self, code_generator):
        self._window_title = 'Blender Node Generator'
        self._window_size = '1200x500'

        self.CodeGenerator = code_generator

    def display(self):
        """Main driver to display the menu"""
        self.window = Tk()

        self.window.title(self._window_title)
        self.window.geometry(self._window_size)

        tab_control = Notebook(self.window)

        # General Tab
        general_tab = Frame(tab_control)
        tab_control.add(general_tab, text='General')
        tab_control.pack(expand=1, fill='both')
        self._general_GUI = GeneralGUI(general_tab)
        self._general_GUI.display()

        # Property Tab
        prop_tab = Frame(tab_control)
        tab_control.add(prop_tab, text='Properties')
        tab_control.pack(expand=1, fill='both')
        self._prop_GUI = PropertiesGUI(prop_tab)
        self._prop_GUI.display()

        # Sockets Tab
        sockets_tab = Frame(tab_control)
        tab_control.add(sockets_tab, text='Socket Definitions')
        tab_control.pack(expand=1, fill='both')
        self._socket_GUI = SocketDefinitionsGUI(sockets_tab)
        self._socket_GUI.display()

        # Socket Availability Tab
        socket_tab = Frame(tab_control)
        tab_control.add(socket_tab, text='Socket Availability')
        tab_control.pack(expand=1, fill='both')
        self._socket_avail_GUI = SocketAvailabilityGUI(socket_tab, self._prop_GUI, self._socket_GUI)
        self._socket_avail_GUI.display()

        # Generate Button
        self.generate_button = Button(self.window, text='Generate', width=25, command=self.generate_node)
        self.generate_button.pack()

        self.window.mainloop()

    def _is_input_valid(self):
        return self._general_GUI.is_input_valid() and \
               self._prop_GUI.is_input_valid()

    def get_source_path(self):
        return self._general_GUI.get_source_path()

    def get_node_name(self):
        return self._general_GUI.get_node_name()

    def get_node_type(self):
        return self._general_GUI.get_node_type()

    def get_node_group(self):
        return self._general_GUI.get_node_group()

    def get_node_group_level(self):
        return self._general_GUI.get_node_group_level()

    def node_has_properties(self):
        return len(self._prop_GUI.get_props()) > 0

    def node_has_check_box(self):
        return len(list(filter(lambda p: p.get()['type'] == 'Boolean', self._prop_GUI.get_props()))) > 0

    def get_node_sockets(self):
        return self._socket_GUI.get_io()

    def get_poll(self):
        return self._general_GUI.get_poll()

    def get_props(self):
        return self._prop_GUI.get_props()

    def is_texture_node(self):
        return self.get_node_type() == 'Texture'

    def generate_node(self):
        if self._is_input_valid():
            code_generator = self.CodeGenerator(self)
            code_generator.generate_node()

            messagebox.showinfo('Done', 'Node has been generated')


class GeneralGUI:
    def __init__(self, tab):
        self._row_i = 0  # Counts the rows which have been filled, methods are responsible for incrementing this value
        self._window = tab
        self._node_groups = ['Input', 'Output', 'Shader', 'Texture', 'OP_Color', 'OP_Vector', 'Converter', 'Script',
                             'Group', 'Layout']
        self._node_types = ['Shader', 'Texture', 'Curves', 'Bsdf', 'BsdfBase', 'ImageSlotTexture', 'Volume']
        self._poll_enabled = BooleanVar()

    def _name_input_display(self):
        """Input for the name of the new node"""
        Label(self._window, text='Node Name', pad=5).grid(row=self._row_i)
        self._name_input = Entry(self._window)
        self._name_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _group_input_display(self):
        """Input for the menu which the node will appear under"""
        Label(self._window, text='Node Group', pad=3).grid(row=self._row_i)
        self._group_input = Combobox(self._window)
        self._group_input['values'] = self._node_groups
        self._group_input.current(2)
        self._group_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _type_input_display(self):
        """Input for the nodes parent class"""
        Label(self._window, text='Node Type', pad=3).grid(row=self._row_i)
        self._type_input = Combobox(self._window)
        self._type_input['values'] = self._node_types
        self._type_input.current(0)
        self._type_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _blender_path_input_display(self):
        """Path to the root directory of the blender source files"""
        Label(self._window, text='Blender Source Path', pad=3).grid(row=self._row_i)
        self._path_input = Entry(self._window)
        self._path_input.grid(row=self._row_i, column=1)
        self._row_i += 1

    def _toggle_enabled(self):
        self._poll_input['state'] = DISABLED if str(self._poll_input['state']) == 'normal' else NORMAL

    def _poll_input_display(self):
        Label(self._window, text='Poll Enabled').grid(row=self._row_i)
        Checkbutton(self._window, var=self._poll_enabled, command=self._toggle_enabled).grid(row=self._row_i, column=1)
        self._poll_input = Entry(self._window)
        self._poll_input.grid(row=self._row_i, column=2)
        self._row_i += 1

    def _group_level_display(self):
        Label(self._window, text='Node Group Level').grid(row=self._row_i)
        self._group_level_input = Combobox(self._window)
        self._group_level_input['values'] = [i for i in range(4)]
        self._group_level_input.grid(row=self._row_i, column=1)
        self._group_level_input.current(0)
        self._row_i += 1

    def display(self):
        self._name_input_display()
        self._group_input_display()
        self._type_input_display()
        self._blender_path_input_display()
        self._poll_input_display()
        self._group_level_display()
        self._toggle_enabled()

    def get_node_name(self):
        return self._name_input.get()

    def get_node_type(self):
        return self._type_input.get()

    def get_node_group(self):
        return self._group_input.get()

    def get_source_path(self):
        return self._path_input.get()

    def get_poll(self):
        return self._poll_input.get() if self._poll_enabled.get() else None

    def get_node_group_level(self):
        return self._group_level_input.get()

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
        return list(filter(lambda p: p is not None, map(lambda p: p.get(), self._ios)))


class SocketAvailabilityGUI:
    """Socket availability"""

    def __init__(self, tab, props_GUI, IO_GUI):
        self._row_i = 0
        self.window = tab
        self._maps = {}
        self._props_GUI = props_GUI
        self._IO_GUI = IO_GUI

    def _remove_existing_menu(self):
        """Removes the existing menu for the selected menu item"""
        for element in list(self.window.children.keys()):
            if type(self.window.children[element]) == Checkbutton or type(self.window.children[element]) == Label:
                self.window.children[element].destroy()

    def _update_options(self, event=None):
        """For when dropdown options are changed"""
        values = []
        for prop in self._props_GUI.get_props():
            if prop['type'] == "Enum":
                values += prop['options']
            elif prop['type'] == "Boolean":
                values.append(prop['name'] + ":True")
                values.append(prop['name'] + ":False")
        self._dropdown['values'] = values

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
                if key == socket['name']:
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
                self._maps[self._dropdown.get()][socket['name']] = vars[i]
        else:
            for socket in sockets:
                if socket['name'] not in self._maps[self._dropdown.get()]:
                    var = BooleanVar()
                    var.set(True)
                    self._maps[self._dropdown.get()][socket['name']] = var
        self._remove_deleted_sockets()
        self._display_mapping(self._dropdown.get())

    def display(self):
        Button(self.window, text='Refresh', command=self._update_options).grid(row=self._row_i)
        self._row_i += 1
        self._dropdown = Combobox(self.window)
        self._update_options()
        self._dropdown.bind('<<ComboboxSelected>>', self._on_selected)
        self._dropdown.grid(row=self._row_i)
        self._row_i += 1

    def get_map(self, name):
        self._remove_deleted_sockets()
        return copy.deepcopy(self._maps[name])

    def get_maps(self):
        self._remove_deleted_sockets()
        return {dropdown: {socket: value.get() for socket, value in self._maps[dropdown].items()} for dropdown in
                self._maps}


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

    def get(self):
        return self.children['!entry'].get() if '!entry' in self.children else None


class PropertiesGUI:
    def __init__(self, tab):
        self._window = tab
        self._row_i = 0
        self._props = []

    def _add_property(self):
        prop = PropertyInput(self._window, self._row_i)
        prop.grid(row=self._row_i, pady=5)
        self._row_i += 1
        self._props.append(prop)

    def display(self):
        Button(self._window, text="Add Property", command=self._add_property).grid(row=self._row_i)
        self._row_i += 1

    def is_input_valid(self):
        # TODO
        return True

    def _sort_props(self, props):
        """Sorts props by type order required for constructing rna props"""
        type_value = {"Enum": 0, "Boolean": 1, "Int": 0, "Float": 2, "String": 3}
        props.sort(key=lambda p: type_value[p['type']])
        return props

    def get_props(self):
        props = [prop.get() for prop in self._props if prop is not None]
        return self._sort_props(props)


class PropertyInput(Frame):
    """Input data required for a property"""

    def __init__(self, window, row_i):
        super().__init__(window)
        self._row_i = row_i

        self.type_components = []  # Holds type specific GUI components

        self.col_i = 0
        # Type
        Label(self, text="Type").grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        self.type = Combobox(self)
        self.type['values'] = ['Boolean', 'Int', 'Float', 'String', 'Enum']
        self.type.bind("<<ComboboxSelected>>", self._type_options_display)
        self.type.current(4)
        self.type.grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        # Sub-Type
        sub_type = Combobox(self)
        sub_type['values'] = ['PROP_NONE', 'PROP_FILEPATH', 'PROP_DIRPATH', 'PROP_FILENAME', 'PROP_BYTESTRING',
                              'PROP_PASSWORD', 'PROP_PIXEL',
                              'PROP_UNSIGNED', 'PROP_PERCENTAGE', 'PROP_FACTOR', 'PROP_ANGLE', 'PROP_TIME',
                              'PROP_DISTANCE', 'PROP_DISTANCE_CAMERA',
                              'PROP_COLOR', 'PROP_TRANSLATION', 'PROP_DIRECTION', 'PROP_VELOCITY', 'PROP_ACCELERATION',
                              'PROP_MATRIX', 'PROP_EULER',
                              'PROP_QUATERNION', 'PROP_AXISANGLE', 'PROP_XYZ', 'PROP_XYZ_LENGTH', 'PROP_COLOR_GAMMA',
                              'PROP_COORDS', 'PROP_LAYER',
                              'PROP_LAYER_MEMBER', 'PROP_POWER']
        sub_type.current(0)
        sub_type.grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        # Name
        Label(self, text="Name").grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        Entry(self).grid(row=self._row_i, column=self.col_i)
        self.col_i += 1

        self._type_options_display()

    def _clear_type_inputs(self):
        """Clears existing type specific input components"""
        for item in self.type_components:
            item.destroy()
        self.type_components.clear()

    def _type_options_display(self, event=None):
        """Display type specific inputs"""
        self._clear_type_inputs()
        type = self.type.get()

        if type == "Boolean":
            self.default = BooleanVar()
            label = Label(self, text="Default Value")
            label.grid(row=self._row_i, column=self.col_i)
            self.col_i += 1
            self.type_components.append(label)
            entry = Checkbutton(self, variable=self.default)
            entry.grid(row=self._row_i, column=self.col_i)
            self.col_i += 1
            self.type_components.append(entry)
        elif type == "Int" or type == "Float":
            min_label = Label(self, text="Min")
            min_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(min_label)
            self.col_i += 1

            min_entry = Entry(self)
            min_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(min_entry)
            self.col_i += 1

            max_label = Label(self, text="Max")
            max_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(max_label)
            self.col_i += 1

            max_entry = Entry(self)
            max_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(max_entry)
            self.col_i += 1

            default_label = Label(self, text="Default")
            default_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_label)
            self.col_i += 1

            default_entry = Entry(self)
            default_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_entry)
            self.col_i += 1
        elif type == "String":
            label = Label(self, text="Size")
            label.grid(row=self._row_i, column=self.col_i)
            self.col_i += 1
            self.type_components.append(label)

            entry = Entry(self)
            entry.grid(row=self._row_i, column=self.col_i)
            self.col_i += 1
            self.type_components.append(entry)
        elif type == "Enum":
            options_label = Label(self, text="Options")
            options_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(options_label)
            self.col_i += 1
            options_entry = Entry(self)
            options_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(options_entry)
            self.col_i += 1

            default_label = Label(self, text="Default")
            default_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_label)
            self.col_i += 1
            default_entry = Entry(self)
            default_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_entry)
            self.col_i += 1
        else:
            raise Exception("Invalid Property Type")

        button = Button(self, text="Remove", command=self.destroy)
        button.grid(row=self._row_i, column=self.col_i)
        self.type_components.append(button)
        self.col_i += 1

    def get(self):
        if self.winfo_exists():
            prop = {'type': self.children['!combobox'].get(),
                    'sub-type': self.children['!combobox2'].get(),
                    'name': self.children['!entry'].get().lower()}
            type = self.type.get()
            if type == "Boolean":
                prop['default'] = 0 if self.default.get() == "False" else 1
            elif type == "Int":
                prop['min'] = int(self.type_components[1].get())
                prop['max'] = int(self.type_components[3].get())
                prop['default'] = int(self.type_components[5].get())
            elif type == "Float":
                prop['min'] = float(self.type_components[1].get())
                prop['max'] = float(self.type_components[3].get())
                prop['default'] = float(self.type_components[5].get())
            elif type == "String":
                prop['size'] = int(self.type_components[1].get())
                prop['default'] = '""'
            elif type == "Enum":
                prop['options'] = self.type_components[1].get().replace(', ', ',').split(',')
                prop['default'] = self.type_components[3].get()
            else:
                raise Exception("Invalid Property Type")
            return prop


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
        type.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Type').grid(row=0, column=col_i)
        col_i += 1
        data_type = Combobox(self)
        data_type['values'] = ["Float", "Vector", "RGBA", "Shader", "Boolean", "Int", "String"]
        data_type.current(0)
        data_type.grid(row=0, column=col_i)
        col_i += 1

        sub_type = Combobox(self)
        sub_type['values'] = ['PROP_NONE', 'PROP_FILEPATH', 'PROP_DIRPATH', 'PROP_FILENAME', 'PROP_BYTESTRING',
                              'PROP_PASSWORD', 'PROP_PIXEL',
                              'PROP_UNSIGNED', 'PROP_PERCENTAGE', 'PROP_FACTOR', 'PROP_ANGLE', 'PROP_TIME',
                              'PROP_DISTANCE', 'PROP_DISTANCE_CAMERA',
                              'PROP_COLOR', 'PROP_TRANSLATION', 'PROP_DIRECTION', 'PROP_VELOCITY', 'PROP_ACCELERATION',
                              'PROP_MATRIX', 'PROP_EULER',
                              'PROP_QUATERNION', 'PROP_AXISANGLE', 'PROP_XYZ', 'PROP_XYZ_LENGTH', 'PROP_COLOR_GAMMA',
                              'PROP_COORDS', 'PROP_LAYER',
                              'PROP_LAYER_MEMBER', 'PROP_POWER']
        sub_type.current(0)
        sub_type.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Flag').grid(row=0, column=col_i)
        col_i += 1
        flag = Combobox(self)
        flag['values'] = ["None", "SOCK_HIDE_VALUE", "SOCK_NO_INTERNAL_LINK"]
        flag.current(0)
        flag.grid(row=0, column=col_i)
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

    def get(self):
        """Returns None if the input has been destroyed"""
        return {'type': self.children['!combobox'].get(), 'name': self.children['!entry'].get(),
                'data_type': self.children['!combobox2'].get(),
                'sub-type': self.children['!combobox3'].get(),
                'flag': self.children['!combobox4'].get(),
                'min': self.children['!entry2'].get(), 'max': self.children['!entry3'].get(),
                'default': self.children['!entry4'].get()} if self.winfo_exists() else None
