from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os

from .node_config import NodeConfig


class GUI:
    """
    Handles the GUI for entering data
    code_generator is a class which accepts the gui in the constructor
    """

    def __init__(self, code_generator):
        self._window_title = 'Blender Node Generator'
        self._window_size = '1450x500'

        self.CodeGenerator = code_generator

    def _display_cancel_generate_node_message(self):
        messagebox.showinfo('Canceled', 'Node was not generated')

    def _display_pre_generation_message(self):
        """Message  displayed before code generation"""
        proceed = messagebox.askokcancel(
            title='File Changes',
            message='This will modify your files, '
                    'make sure you are using a version control system so you can undo changes')
        if proceed:
            self._display_pre_generation_warnings()

    def _display_pre_generation_warnings(self):
        """Warnings related to the users input"""
        if any(item['data-type'] == 'String' for item in self.get_props()):
            proceed = messagebox.askyesno('Input Warning', "String type props aren't fully supported\n"
                                                           "You will need to do your own implementation for handling this input in\n"
                                                           "'blender_shader.cpp'\n"
                                                           "Do you want to proceed?")
            if not proceed:
                self._display_cancel_generate_node_message()
                return

        if len(self.get_node_sockets() + self.get_props()) > 12:
            proceed = messagebox.askyesno('Input Warning', "More than 12 properties + sockets isn't fully supported\n"
                                                           "You will need to implement the svm compile function in\n "
                                                           "'node.cpp'"
                                                           "And the svm shader"
                                                           "Do you want to proceed?")
            if not proceed:
                self._display_cancel_generate_node_message()
                return

        if len([prop for prop in self.get_props() if prop['data-type'] == 'Enum']) > 2:
            proceed = messagebox.askyesno('Input Warning', "More than 2 enums isn't fully supported\n"
                                                           "You will need to implement the GLSL related functions in\n"
                                                           "'node_shader_(your_node_name).h'\n"
                                                           "'gpu_shader_material_(your_node_name).glsl'\n"
                                                           "Do you want to proceed?")
            if not proceed:
                self._display_cancel_generate_node_message()
                return

        self.generate_node()

    def _save_config(self):
        config = NodeConfig(self)
        config.save_config()

    def _load_config(self):
        config = NodeConfig(self)
        config.load_config()

    def serialize(self):
        return [self._general_GUI.serialize(),
                self._socket_GUI.serialize(),
                self._prop_GUI.serialize(),
                self._socket_avail_GUI.serialize()]

    def deserialize(self, data):
        self._general_GUI.deserialize(data[0])
        self._socket_GUI.deserialize(data[1])
        self._prop_GUI.deserialize(data[2])
        self._socket_avail_GUI.deserialize(data[3])     # Important to do last, reliant on socket/prop GUI

    def display(self):
        """Main driver to display the menu"""
        self.window = Tk()

        self.window.title(self._window_title)
        self.window.geometry(self._window_size)

        # Top Menu
        menubar = Menu(self.window)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Save', command=self._save_config)
        filemenu.add_command(label='Load', command=self._load_config)
        menubar.add_cascade(label='File', menu=filemenu)
        self.window.config(menu=menubar)

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
        self.generate_button = Button(self.window, text='Generate', width=25,
                                      command=self._display_pre_generation_message)
        self.generate_button.pack()

        self.window.mainloop()

    def _is_input_valid(self):
        return self._general_GUI.is_input_valid() and \
               self._prop_GUI.is_input_valid() and \
               self._socket_GUI.is_input_valid() and \
               self._socket_avail_GUI.is_input_valid()

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
        return len(list(filter(lambda p: p.get()['data-type'] == 'Boolean', self._prop_GUI.get_props()))) > 0

    def get_node_sockets(self):
        return self._socket_GUI.get_sockets()

    def get_props(self):
        return self._prop_GUI.get_props()

    def get_socket_availability_maps(self):
        return self._socket_avail_GUI.get_maps()

    def is_texture_node(self):
        return self.get_node_type() == 'Texture'

    def uses_texture_mapping(self):
        # Will probably be exposed in GUI eventually
        return self.is_texture_node() and len([socket for socket in self._socket_GUI.get_sockets() if
                                               socket['type'] == 'Input' and socket['data-type'] == 'Vector']) > 0

    def socket_availability_changes(self):
        """Returns whether the socket availability of the node changes based on
        the nodes properties values"""
        for map in self._socket_avail_GUI.get_maps():
            for prop, avail in map['prop-avail']:
                if not avail:
                    return True
        return False

    def type_suffix_abbreviated(self):
        """Type suffix but abbreviated"""
        if self.get_node_type() == 'Texture':
            return 'tex'
        elif self.get_node_type() in ['Bsdf', 'BsdfBase']:
            return 'bsdf'
        else:
            return ''

    def type_suffix(self):
        """Type related suffix which is appended to type definitions"""
        if self.get_node_type() == 'Texture':
            return 'texture'
        elif self.get_node_type() in ['Bsdf', 'BsdfBase']:
            return 'bsdf'
        else:
            return ''

    def generate_node(self):
        if self._is_input_valid():
            code_generator = self.CodeGenerator(self)
            try:
                code_generator.generate_node()
                messagebox.showinfo('Done', 'Node has been generated')
            except Exception as e:
                messagebox.showerror('Error',
                                     '{error_type}: {error_message}\n\nIf you believe this is a problem with the program,'
                                     ' please report it\nhttps://github.com/idomo1/blender-node-generator/issues'.format(
                                         error_type=type(e),
                                         error_message=e
                                     ))


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

    def _group_level_display(self):
        Label(self._window, text='Node Group Level').grid(row=self._row_i)
        self._group_level_input = Combobox(self._window)
        self._group_level_input['values'] = [i for i in range(4)]
        self._group_level_input.grid(row=self._row_i, column=1)
        self._group_level_input.current(0)
        self._row_i += 1

    def _help_info_display(self):
        """Display help info for the current tab"""
        w = Toplevel()
        w.title('Help')
        Message(w, width=5000,
                text="General info which doesn't fall into the other categories\n"
                     "Node Name - Name of the node separated by spaces. "
                     "Don't worry about adding a 'texture' suffix, "
                     "the program will do that for you if you choose a texture node\n"
                     "Node Group - The menu the node will show under\n"
                     "Node Type - The class the nodes cycles class will inherit from\n"
                     "Source Path - Absolute path to blender source code root directory\n"
                     "Node Group Level - Used by SVM for selective node compilation,\n"
                     " look at 'svm.h' to get an idea where your node should be\n"
                     "\n\nIf you are unsure, look at a similar nodes implementation").grid()

    def _help_button_display(self):
        """Button to display help info"""
        Button(self._window, text='Help', command=self._help_info_display).place(anchor='nw', x=300, y=0)

    def display(self):
        self._name_input_display()
        self._group_input_display()
        self._type_input_display()
        self._blender_path_input_display()
        self._group_level_display()
        self._help_button_display()

    def get_node_name(self):
        return self._name_input.get()

    def get_node_type(self):
        return self._type_input.get()

    def get_node_group(self):
        return self._group_input.get()

    def get_source_path(self):
        return self._path_input.get()

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
        if self.get_node_type() == 'Texture' and self.get_node_group_level() not in ['0', '2']:
            messagebox.showerror('Bad Input', 'Texture node must have a node group level of 0 or 2')
            return False
        if not os.path.isdir(self.get_source_path()):
            messagebox.showerror('Bad Input', '{0} is not a valid path'.format(self.get_source_path()))
            return False
        if self.get_node_type() == 'Texture':
            character_limit = 10
        elif self.get_node_type() in ['Bsdf', 'BsdfBase']:
            character_limit = 14
        else:
            character_limit = 17
        if len(node_name) > character_limit:  # Greater than 17 characters causes writing NOD_static_types.h to timeout
            messagebox.showerror('Bad Input', '{type} node name must be less than {limit} characters long'.format(
                type=self.get_node_type(),
                limit=character_limit))
            return False
        return True

    def serialize(self):
        """Return a serialized version of the GUI inputs"""
        return {'name': self.get_node_name(),
                'type': self.get_node_type(),
                'group': self.get_node_group(),
                'group-level': self.get_node_group_level(),
                'path': self.get_source_path()}

    def deserialize(self, data):
        """Reconstruct GUI state from serialized object"""
        self._name_input.delete(0, END)
        self._name_input.insert(0, data['name'])
        self._type_input.delete(0, END)
        self._type_input.insert(0, data['type'])
        self._group_input.delete(0, END)
        self._group_input.insert(0, data['group'])
        self._group_level_input.delete(0, END)
        self._group_level_input.insert(0, data['group-level'])
        self._path_input.delete(0, END)
        self._path_input.insert(0, data['path'])


class SocketDefinitionsGUI:
    """GUI for entering input and output sockets for the node"""

    def __init__(self, tab):
        self.window = tab
        self._row_i = 0
        self._ios = []

    def _add_node_socket(self):
        io = RemovableSocketDefinitionInput(self.window, 'IO')
        self._ios.append(io)
        io.grid(row=self._row_i)
        self._row_i += 1

    def _help_info_display(self):
        """Display help info for the current tab"""
        w = Toplevel()
        w.title('Help')
        Message(w, width=5000,
                text="Where you can add node sockets\n"
                     "IO - Whether the socket is an input or output\n"
                     "Type - The data type of the socket\n"
                     "Sub-Type - Affects the display of the input entry e.g. adds units\n"
                     "Flag - Optional flag\n"
                     "Name - Socket name separated by spaces\n"
                     "Min - Minimum value of the socket. Make sure units are appropriate e.g float 0.0, int 0\n"
                     "for vector inputs, if the default is 0.0 for all components, 0.0 is fine, "
                     "otherwise comma separated list\n"
                     "Max - Maximum value of the socket. Same as above\n"
                     "Default - Default value. Same as above. For output sockets, just leave it at 0.0\n").grid()

    def _help_button_display(self):
        """Button to display help info"""
        Button(self.window, text='Help', command=self._help_info_display).place(anchor='nw', x=300, y=0)

    def display(self):
        Button(self.window, text='Add I/O', command=self._add_node_socket).grid(row=self._row_i)
        self._row_i += 1
        self._help_button_display()

    def _sort_sockets(self, sockets):
        """Sorts sockets"""
        order = {'Input': 0, 'Output': 1}
        sockets.sort(key=lambda s: order[s['type']])
        return sockets

    def get_sockets(self):
        return self._sort_sockets(list(filter(lambda p: p is not None, map(lambda p: p.get(), self._ios))))

    def _is_socket_input_valid(self, socket):
        if socket['data-type'] == 'Float':
            try:
                float(socket['min'])
                float(socket['max'])
                if socket['type'] == 'Input':
                    float(socket['default'])
                return True
            except:
                return False
        elif socket['data-type'] == 'Int':
            try:
                int(socket['min'])
                int(socket['max'])
                if socket['type'] == 'Input':
                    int(socket['default'])
                return True
            except:
                return False
        elif socket['data-type'] in ['Vector', 'Shader', 'RGBA']:
            keys = ['min', 'max']
            if socket['type'] == 'Input':
                keys.append('default')
            for key in keys:
                for comp in socket[key].split(','):
                    try:
                        float(comp)
                        return True
                    except:
                        return False
        elif socket['data-type'] == 'String':
            return True

    def is_input_valid(self):
        if any(socket['name'] == '' for socket in self.get_sockets()):
            messagebox.showerror('Bad Input', 'One or more socket names missing')
            return False
        if any(not self._is_socket_input_valid(socket) for socket in self.get_sockets()):
            messagebox.showerror('Bad Input', 'One or more sockets has invalid input formatting')
            return False
        return True

    def serialize(self):
        """Return a serialized version of the GUI inputs"""
        return self.get_sockets()

    def deserialize(self, data):
        """Reconstruct GUI state from serialized object"""
        for el in self._ios:
            el.destroy()
        self._ios = [RemovableSocketDefinitionInput(self.window, 'IO') for _ in data]
        for socket, serialized_socket in zip(self._ios, data):
            socket.deserialize(serialized_socket)
            socket.grid(row=self._row_i)
            self._row_i += 1


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
        self._socket_selection['values'] = [socket['name'] for socket in self._IO_GUI.get_sockets()]

    def _remove_deleted_sockets(self):
        """Remove sockets which have been deleted"""
        for socket in list(self._maps.keys()):
            if not list(filter(lambda s: s['name'] == socket, self._IO_GUI.get_sockets())):
                del self._maps[socket]

    def _display_mapping(self, map_key):
        self._remove_existing_menu()
        if len(self._maps[map_key]) == 0:
            Label(self.window, text='No props').grid(row=self._row_i)

        for prop in self._maps[map_key]:
            Label(self.window, text=prop).grid(row=self._row_i)
            Checkbutton(self.window, var=self._maps[map_key][prop]).grid(row=self._row_i, column=1)
            self._row_i += 1

    def _remove_deleted_props(self, selected_socket=None):
        props = self._props_GUI.get_props()
        if selected_socket is None:
            selected_socket = self._socket_selection.get()
        # If there has been user input
        if selected_socket:
            for key in list(self._maps[selected_socket].keys()):
                for prop in props:
                    if prop['data-type'] == 'Boolean':
                        if key == prop['name'] + '=True' or key == prop['name'] + '=False':
                            break
                    elif prop['data-type'] == 'Enum':
                        if key in [prop['name'] + '=' + option['name'] for option in prop['options']]:
                            break
                else:
                    del self._maps[selected_socket][key]

    def _update_props(self):
        """Update for changes in props"""
        selected_socket = self._socket_selection.get()
        for prop in self._props_GUI.get_props():
            if prop['data-type'] == 'Boolean':
                if prop['name'] + '=True' not in self._maps[selected_socket]:
                    var = BooleanVar()
                    var.set(True)
                    self._maps[selected_socket][prop['name'] + '=True'] = var
                if prop['name'] + '=False' not in self._maps[selected_socket]:
                    var = BooleanVar()
                    var.set(True)
                    self._maps[selected_socket][prop['name'] + '=False'] = var
            elif prop['data-type'] == 'Enum':
                for option in prop['options']:
                    prop_option_name = prop['name'] + '=' + option['name']
                    if prop_option_name not in self._maps[selected_socket]:
                        var = BooleanVar()
                        var.set(True)
                        self._maps[selected_socket][prop_option_name] = var

    def _on_selected(self, event=None, selected_socket=None):
        props = self._props_GUI.get_props()
        # If new socket(s) added
        if selected_socket is None:
            selected_socket = self._socket_selection.get()
        if selected_socket not in self._maps:
            options = []
            for prop in props:
                if prop['data-type'] == 'Boolean':
                    options.append(prop['name'] + '=True')
                    options.append(prop['name'] + '=False')
                elif prop['data-type'] == 'Enum':
                    options.extend([(prop['name'] + '=' + option['name']) for option in prop['options']])
            vars = [BooleanVar() for _ in range(len(options))]

            if len(options) == 0:
                self._maps[selected_socket] = {}

            for var in vars:
                var.set(True)
                self._maps[selected_socket] = dict()
            for i, option in enumerate(options):
                self._maps[selected_socket][option] = vars[i]
        else:
            self._update_props()
        self._remove_deleted_props(selected_socket)
        self._display_mapping(selected_socket)

    def _help_info_display(self):
        """Display help info for the current tab"""
        w = Toplevel()
        w.title('Help')
        Message(w, width=5000,
                text="When each socket is enabled/visible based on prop values\n"
                     "Ticked means the socket is visible when the prop is this value\n"
                     "Refresh if you change socket info\n").grid()

    def _help_button_display(self):
        """Button to display help info"""
        Button(self.window, text='Help', command=self._help_info_display).place(anchor='nw', x=300, y=0)

    def display(self):
        Button(self.window, text='Refresh', command=self._update_options).grid(row=self._row_i)
        self._row_i += 1
        self._socket_selection = Combobox(self.window)
        self._update_options()
        self._socket_selection.bind('<<ComboboxSelected>>', self._on_selected)
        self._socket_selection.grid(row=self._row_i)
        self._row_i += 1
        self._help_button_display()

    def get_maps(self):
        self._remove_deleted_props()
        sockets = self._IO_GUI.get_sockets()
        return [{'socket-name': socket_name,
                 'socket-type': 'in' if next(socket for socket in sockets if socket['name'] == socket_name)
                                        ['type'] == 'Input' else 'out',
                 'prop-avail': [(prop, value.get()) for prop, value in self._maps[socket_name].items()]}
                for socket_name in self._maps.keys()]

    def is_input_valid(self):
        return True

    def serialize(self):
        """Return a serialized version of the GUI inputs"""
        serialized = {}
        for socket in self._maps.keys():
            serialized[socket] = [(prop, value.get()) for prop, value in self._maps[socket].items()]
        return serialized

    def deserialize(self, data):
        self._maps = {}
        self._update_options()
        # self._remove_deleted_props()
        # self._update_props()
        for socket in data:
            self._on_selected(selected_socket=socket)
        for socket, avail in self._maps.items():
            for prop, serialized in zip(avail, data[socket]):
                self._maps[socket][prop].set(serialized[1])


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

    def _help_info_display(self):
        """Display help info for the current tab"""
        w = Toplevel()
        w.title('Help')
        Message(w, width=5000,
                text="Where you can add properties\n"
                     "All: Type - Prop data type\n"
                     "All: Sub-Type - Affects input display e.g adds units\n"
                     "All: Name - Prop name separated by spaces\n"
                     "All: Default - Default value. Make sure the value matches the data type. e.g float 0.0, int 0\n"
                     "Float/Int: Min - Minimum value. Same as above\n"
                     "Float/Int: Max - Maximum value. Same as above\n"
                     "String: Size - The amount of characters - 1 that can fit in the string. Make a multiple of 2\n"
                     "Enum: Add Option - Add an option to the enum\n"
                     "Enum Option: Name - Name of the option separated by spaces\n"
                     "Enum Option: Description - Short one line description of the option").grid()

    def _help_button_display(self):
        """Button to display help info"""
        Button(self._window, text='Help', command=self._help_info_display).place(anchor='nw', x=100, y=0)

    def display(self):
        Button(self._window, text="Add Property", command=self._add_property).grid(row=self._row_i)
        self._row_i += 1
        self._help_button_display()

    def is_input_valid(self):
        # TODO
        return True

    def _sort_props(self, props):
        """Sorts props by type order required for constructing rna props"""
        type_value = {"Enum": 0, "Boolean": 2, "Int": 1, "Float": 3, "String": 4}
        props.sort(key=lambda p: type_value[p['data-type']])
        return props

    def get_props(self):
        props = [prop.get() for prop in self._props if prop.get() is not None]
        return self._sort_props(props)

    def serialize(self):
        return {'props': self.get_props()}

    def deserialize(self, data):
        for el in self._props:
            el.destroy()
        self._row_i = 0
        self._props = [PropertyInput(self._window, self._row_i) for _ in data['props']]
        for prop, serialized_prop in zip(self._props, data['props']):
            prop.deserialize(serialized_prop)
            prop.grid(row=self._row_i)
            self._row_i += 1


class PropertyInput(Frame):
    """Input data required for a property"""

    def __init__(self, window, row_i):
        super().__init__(window)

        self._enum_options = []

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
        Label(self, text='Sub-Type').grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        self.sub_type = Combobox(self)
        self.sub_type['values'] = ['PROP_NONE', 'PROP_FILEPATH', 'PROP_DIRPATH', 'PROP_FILENAME', 'PROP_BYTESTRING',
                                   'PROP_PASSWORD', 'PROP_PIXEL',
                                   'PROP_UNSIGNED', 'PROP_PERCENTAGE', 'PROP_FACTOR', 'PROP_ANGLE', 'PROP_TIME',
                                   'PROP_DISTANCE', 'PROP_DISTANCE_CAMERA',
                                   'PROP_COLOR', 'PROP_TRANSLATION', 'PROP_DIRECTION', 'PROP_VELOCITY',
                                   'PROP_ACCELERATION',
                                   'PROP_MATRIX', 'PROP_EULER',
                                   'PROP_QUATERNION', 'PROP_AXISANGLE', 'PROP_XYZ', 'PROP_XYZ_LENGTH',
                                   'PROP_COLOR_GAMMA',
                                   'PROP_COORDS', 'PROP_LAYER',
                                   'PROP_LAYER_MEMBER', 'PROP_POWER']
        self.sub_type.current(0)
        self.sub_type.grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        # Name
        Label(self, text="Name").grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        self.name = Entry(self)
        self.name.grid(row=self._row_i, column=self.col_i)
        self.col_i += 1

        self._type_options_display()

    def _clear_type_inputs(self):
        """Clears existing type specific input components"""
        for item in self.type_components:
            item.destroy()
        self.type_components.clear()
        self._enum_options.clear()

    def _add_option(self):
        self._enum_options.append(OptionInput(self))
        self._enum_options[-1].grid()

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
            default_label = Label(self, text="Default")
            default_label.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_label)
            self.col_i += 1
            default_entry = Entry(self)
            default_entry.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(default_entry)
            self.col_i += 1

            add_option_button = Button(self, text="Add Option", command=self._add_option)
            add_option_button.grid(row=self._row_i, column=self.col_i)
            self.type_components.append(add_option_button)
            self.col_i += 1


        else:
            raise Exception("Invalid Property Type")

        button = Button(self, text="Remove", command=self.destroy)
        button.grid(row=self._row_i, column=self.col_i)
        self.type_components.append(button)
        self.col_i += 1

    def get(self):
        if self.winfo_exists():
            prop = {'data-type': self.children['!combobox'].get(),
                    'sub-type': self.children['!combobox2'].get(),
                    'name': self.children['!entry'].get().lower()}
            type = self.type.get()
            if type == "Boolean":
                prop['default'] = int(self.default.get())
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
                prop['default'] = self.type_components[1].get()
                prop['options'] = [option.get() for option in self._enum_options if option.winfo_exists()]
            else:
                raise Exception("Invalid Property Type")
            return prop

    def deserialize(self, data):
        self.type.current(self.type['values'].index(data['data-type']))
        self.sub_type.current(self.sub_type['values'].index(data['sub-type']))
        self.name.delete(0, END)
        self.name.insert(0, data['name'])
        self._clear_type_inputs()
        self._type_options_display()

        data_type = self.type.get()
        if data_type == 'Boolean':
            self.default.set(data['default'])
        elif data_type in ['Int', 'Float']:
            self.type_components[1].delete(0, END)
            self.type_components[1].insert(0, data['min'])
            self.type_components[3].delete(0, END)
            self.type_components[3].insert(0, data['max'])
            self.type_components[5].delete(0, END)
            self.type_components[5].insert(0, data['default'])
        elif data_type == 'String':
            self.type_components[1].delete(0, END)
            self.type_components[1].insert(0, data['size'])
        elif data_type == 'Enum':
            self.type_components[1].delete(0, END)
            self.type_components[1].insert(0, data['default'])
            for el in self._enum_options:
                el.destroy()
            self._enum_options = [OptionInput(self) for _ in data['options']]
            for opt, serialized_opt in zip(self._enum_options, data['options']):
                opt.deserialize(serialized_opt)
                opt.grid()


class RemovableSocketDefinitionInput(Frame):
    """Node IO Template"""

    def __init__(self, window, label):
        super().__init__(window)

        self._type_components = []  # Holds type specific input elements

        self.col_i = 0

        Label(self, text=label).grid(row=0, column=self.col_i)
        self.col_i += 1
        self._type = Combobox(self)
        self._type['values'] = ["Input", "Output"]
        self._type.bind("<<ComboboxSelected>>", self._type_options_display)
        self._type.current(0)
        self._type.grid(row=0, column=self.col_i)
        self.col_i += 1

        Label(self, text='Type').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._data_type = Combobox(self)
        self._data_type['values'] = ["Float", "Vector", "RGBA", "Shader", "String"]
        self._data_type.bind("<<ComboboxSelected>>", self._type_options_display)
        self._data_type.current(0)
        self._data_type.grid(row=0, column=self.col_i)
        self.col_i += 1

        Label(self, text='Sub-type').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._sub_type = Combobox(self)
        self._sub_type['values'] = ['PROP_NONE', 'PROP_FILEPATH', 'PROP_DIRPATH', 'PROP_FILENAME', 'PROP_BYTESTRING',
                                    'PROP_PASSWORD', 'PROP_PIXEL',
                                    'PROP_UNSIGNED', 'PROP_PERCENTAGE', 'PROP_FACTOR', 'PROP_ANGLE', 'PROP_TIME',
                                    'PROP_DISTANCE', 'PROP_DISTANCE_CAMERA',
                                    'PROP_COLOR', 'PROP_TRANSLATION', 'PROP_DIRECTION', 'PROP_VELOCITY',
                                    'PROP_ACCELERATION',
                                    'PROP_MATRIX', 'PROP_EULER',
                                    'PROP_QUATERNION', 'PROP_AXISANGLE', 'PROP_XYZ', 'PROP_XYZ_LENGTH',
                                    'PROP_COLOR_GAMMA',
                                    'PROP_COORDS', 'PROP_LAYER',
                                    'PROP_LAYER_MEMBER', 'PROP_POWER']
        self._sub_type.current(0)
        self._sub_type.grid(row=0, column=self.col_i)
        self.col_i += 1

        Label(self, text='Flag').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._flag = Combobox(self)
        self._flag['values'] = ["None", "SOCK_HIDE_VALUE", "SOCK_NO_INTERNAL_LINK"]
        self._flag.current(0)
        self._flag.grid(row=0, column=self.col_i)
        self.col_i += 1

        Label(self, text='Name').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._name = Entry(self)
        self._name.grid(row=0, column=self.col_i)
        self.col_i += 1

        self._type_options_display()

    def _type_options_display(self, event=None):
        """Type specific inputs"""
        self._clear_type_inputs()
        type = self._data_type.get()
        if type in ['Float', 'Int', 'Shader', 'Vector', 'RGBA']:
            label = Label(self, text='Min')
            label.grid(row=0, column=self.col_i)
            self.col_i += 1
            min = Entry(self)
            min.insert(0, "0.0")
            min.grid(row=0, column=self.col_i)
            self.col_i += 1
            self._type_components.extend([label, min])

            label = Label(self, text='Max')
            label.grid(row=0, column=self.col_i)
            self.col_i += 1
            max = Entry(self)
            max.insert(0, '1.0')
            max.grid(row=0, column=self.col_i)
            self.col_i += 1
            self._type_components.extend([label, max])

            if self._type.get() == 'Input':
                label = Label(self, text='Default')
                label.grid(row=0, column=self.col_i)
                self.col_i += 1
                default = Entry(self)
                if type == 'Float':
                    default.insert(0, '0.0')
                elif type == 'Int':
                    default.insert(0, '0')
                else:
                    default.insert(0, '0.0,0.0,0.0')
                default.grid(row=0, column=self.col_i)
                self.col_i += 1
                self._type_components.extend([label, default])

        button = Button(self, text='Remove', command=self.destroy)
        button.grid(row=0, column=self.col_i)
        self.col_i += 1
        self._type_components.append(button)

    def _clear_type_inputs(self):
        """Clears existing type specific input components"""
        for item in self._type_components:
            item.destroy()
        self._type_components.clear()

    def get(self):
        """Returns None if the input has been destroyed"""
        if not self.winfo_exists():
            return None

        socket = {'type': self.children['!combobox'].get(), 'name': self.children['!entry'].get(),
                  'data-type': self.children['!combobox2'].get(),
                  'sub-type': self.children['!combobox3'].get(),
                  'flag': self.children['!combobox4'].get()}
        if socket['data-type'] != 'String':
            socket['min'] = self._type_components[1].get()
            socket['max'] = self._type_components[3].get()
            if socket['type'] == 'Input':
                socket['default'] = self._type_components[5].get()
        return socket

    def deserialize(self, data):
        """Reconstruct GUI state from serialized object"""
        self._type.current(self._type['values'].index(data['type']))
        self._data_type.current(self._data_type['values'].index(data['data-type']))
        self._sub_type.current(self._sub_type['values'].index(data['sub-type']))
        self._flag.current(self._flag['values'].index(data['flag']))
        self._name.delete(0, END)
        self._name.insert(0, data['name'])
        self._type_options_display()

        data_type = self._data_type.get()
        if data_type in ['Float', 'Int', 'Shader', 'Vector', 'RGBA']:
            # Relies on all type inputs having delete/insert methods, keep in mind when changing inputs
            for input, serialized_input in zip([comp for comp in self._type_components if type(comp) not in [Label, Button]],
                                               [data[key] for key in data if
                                                key not in ['type', 'data-type', 'sub-type', 'flag', 'name']]):
                input.delete(0, END)
                input.insert(0, serialized_input)


class OptionInput(Frame):
    """An input for an enum option"""

    def __init__(self, window):
        super().__init__(window)

        col_i = 0
        Label(self, text='Name').grid(row=0, column=col_i)
        col_i += 1
        self._name = Entry(self)
        self._name.grid(row=0, column=col_i)
        col_i += 1

        Label(self, text='Description').grid(row=0, column=col_i)
        col_i += 1
        self._description = Entry(self)
        self._description.grid(row=0, column=col_i)
        col_i += 1

        Button(self, text='Remove', command=self.destroy).grid(row=0, column=col_i)

    def get(self):
        return {"name": self._name.get(),
                "desc": self._description.get()}

    def deserialize(self, data):
        self._name.delete(0, END)
        self._name.insert(0, data['name'])
        self._description.delete(0, END)
        self._description.insert(0, data['desc'])
