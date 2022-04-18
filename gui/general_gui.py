from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os

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
                     "\n\nIf you are unsure, look at a similar nodes implementation").grid()

    def _help_button_display(self):
        """Button to display help info"""
        Button(self._window, text='Help', command=self._help_info_display).place(anchor='nw', x=300, y=0)

    def display(self):
        self._name_input_display()
        self._group_input_display()
        self._type_input_display()
        self._blender_path_input_display()
        self._help_button_display()

    def get_node_name(self):
        return self._name_input.get()

    def get_node_type(self):
        return self._type_input.get()

    def get_node_group(self):
        return self._group_input.get()

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
