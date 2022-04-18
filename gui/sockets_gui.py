from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from node_types.socket_float import FloatSocket
from node_types.socket_vector import VectorSocket
from node_types.socket_color import ColorSocket
from gui.checklistcombobox import ChecklistCombobox

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
                     "Flag - Optional flags\n"
                     "Name - Socket name separated by spaces\n"
                     "Min - Minimum value of the socket. Make sure units are appropriate e.g float 0.0f, int 0\n"
                     "for vector inputs, if the default is 0.0f for all components, 0.0f is fine, "
                     "otherwise comma separated list\n"
                     "Max - Maximum value of the socket. Same as above\n"
                     "Default - Default value. Same as above.\n").grid()

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

class RemovableSocketDefinitionInput(Frame):
    """Node IO Template"""

    def __init__(self, window, label):
        super().__init__(window)

        socket_types = [FloatSocket(), VectorSocket(), ColorSocket()]

        self._type_components = []  # Holds type specific input elements

        self.col_i = 0

        Label(self, text=label).grid(row=0, column=self.col_i)
        self.col_i += 1
        self._type = Combobox(self, width=8)
        self._type['values'] = ["Input", "Output"]
        self._type.bind("<<ComboboxSelected>>", self._type_options_display)
        self._type.current(0)
        self._type.grid(row=0, column=self.col_i)
        self.col_i += 1

        Label(self, text='Type').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._data_type = Combobox(self, width=10)
        self._data_type['values'] = [type.type_name for type in socket_types]
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

        Label(self, text='Flags').grid(row=0, column=self.col_i)
        self.col_i += 1
        self._flags = ChecklistCombobox(self, values=['hide_label', 'hide_value', 'multi_input', 'no_muted_links', 'is_attribute_name', 'is_default_link_socket', 'supports_field', 'implicit_field', 'field_source', 'dependent_field'])
        self._flags.grid(row=0,column=self.col_i)
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
        socket_type = self._get_socket_type()
        if self._type.get() == 'Input':
            if socket_type.has_min():
                label = Label(self, text='Min')
                label.grid(row=0, column=self.col_i)
                self.col_i += 1
                min = Entry(self)
                min.insert(0, socket_type.default_min)
                min.grid(row=0, column=self.col_i)
                self.col_i += 1
                self._type_components.extend([label, min])
            if socket_type.has_max():
                label = Label(self, text='Max')
                label.grid(row=0, column=self.col_i)
                self.col_i += 1
                max = Entry(self)
                max.insert(0, socket_type.default_max)
                max.grid(row=0, column=self.col_i)
                self.col_i += 1
                self._type_components.extend([label, max])
            if socket_type.has_default() and self._type.get() == 'Input':
                label = Label(self, text='Default')
                label.grid(row=0, column=self.col_i)
                self.col_i += 1
                default = Entry(self)
                default.insert(0, socket_type.default_default)
                default.grid(row=0, column=self.col_i)
                self.col_i += 1
                self._type_components.extend([label, default])

        button = Button(self, text='Remove', command=self.destroy)
        button.grid(row=0, column=self.col_i)
        self.col_i += 1
        self._type_components.append(button)
    
    def _get_socket_type(self):
        map = {'Float': FloatSocket(), 'Vector': VectorSocket(), 'Color': ColorSocket()}
        return map[self._data_type.get()]

    def _clear_type_inputs(self):
        """Clears existing type specific input components"""
        for item in self._type_components:
            item.destroy()
        self._type_components.clear()

    def get(self):
        """Returns None if the input has been destroyed"""
        if not self.winfo_exists():
            return None

        socket = {'type': self._type.get(), 'name': self._name.get(),
                  'data-type': self._get_socket_type(),
                  'sub-type': self._sub_type.get(),
                  'flags': self._flags.get()}
        if socket['type'] == 'Input':
            if socket['data-type'].has_min():
                socket['min'] = self._type_components[1].get()
            if socket['data-type'].has_max():
                index = 1
                if (socket['data-type'].has_min()):
                    index += 2
                socket['max'] = self._type_components[index].get()
            if socket['data-type'].has_default() and socket['type'] == 'Input':
                index = 1
                if socket['data-type'].has_min():
                    index += 2
                if socket['data-type'].has_max():
                    index += 2
                socket['default'] = self._type_components[index].get()
        return socket
