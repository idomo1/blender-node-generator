from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import traceback
from node_types.prop_enum import EnumProp

from node_types.socket_vector import VectorSocket


from gui.general_gui import GeneralGUI
from gui.properties_gui import PropertiesGUI
from gui.sockets_gui import SocketDefinitionsGUI

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
        if len(self.get_node_sockets() + self.get_props()) > 12:
            proceed = messagebox.askyesno('Input Warning', "More than 12 properties + sockets isn't fully supported\n"
                                                           "You will need to implement the svm compile function in\n "
                                                           "'node.cpp'"
                                                           "And the svm shader"
                                                           "Do you want to proceed?")
            if not proceed:
                self._display_cancel_generate_node_message()
                return

        if len([prop for prop in self.get_props() if isinstance(prop['data-type'], EnumProp)]) > 2:
            proceed = messagebox.askyesno('Input Warning', "More than 2 enums isn't fully supported\n"
                                                           "You will need to implement the GLSL related functions in\n"
                                                           "'node_shader_(your_node_name).h'\n"
                                                           "'gpu_shader_material_(your_node_name).glsl'\n"
                                                           "Do you want to proceed?")
            if not proceed:
                self._display_cancel_generate_node_message()
                return

        self.generate_node()

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

        # Generate Button
        self.generate_button = Button(self.window, text='Generate', width=25,
                                      command=self._display_pre_generation_message)
        self.generate_button.pack()

        self.window.mainloop()

    def get_source_path(self):
        return self._general_GUI.get_source_path()

    def get_node_name(self):
        return self._general_GUI.get_node_name()

    def get_node_type(self):
        return self._general_GUI.get_node_type()

    def get_node_group(self):
        return self._general_GUI.get_node_group()

    def node_has_properties(self):
        return len(self._prop_GUI.get_props()) > 0

    def node_has_check_box(self):
        return len(list(filter(lambda p: p.get()['data-type'] == 'Bool', self._prop_GUI.get_props()))) > 0

    def get_node_sockets(self):
        return self._socket_GUI.get_sockets()

    def get_props(self):
        return self._prop_GUI.get_props()

    def is_texture_node(self):
        return self.get_node_type() == 'Texture'

    def uses_texture_mapping(self):
        # Will probably be exposed in GUI eventually
        return self.is_texture_node() and len([socket for socket in self._socket_GUI.get_sockets() if
                                               socket['type'] == 'Input' and isinstance(socket['data-type'], VectorSocket)]) > 0

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
        code_generator = self.CodeGenerator(self)
        try:
            code_generator.generate_node()
            messagebox.showinfo('Done', 'Node has been generated')
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror('Error',
                                 '{error_type}: {error_message}\n\nIf you believe this is a problem with the program,'
                                 ' please report it\nhttps://github.com/idomo1/blender-node-generator/issues'.format(
                                     error_type=type(e),
                                     error_message=e,
                                 ))


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
