from tkinter import *
from tkinter.ttk import *

from node_types.prop_bool import BoolProp
from node_types.prop_enum import EnumProp
from node_types.prop_int import IntProp

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
                text="Properties are node inputs which aren't exposed as a socket\n"
                     "All: Type - Prop data type\n"
                     "All: Sub-Type - Affects input display e.g adds units\n"
                     "All: Name - Prop name separated by spaces\n"
                     "All: Default - Default value. e.g 0\n"
                     "Int: Min - Minimum value. Same as above\n"
                     "Int: Max - Maximum value. Same as above\n"
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

    def _sort_props(self, props):
        """Sorts props by type order required for constructing rna props"""
        type_value = {"Enum": 0, "Boolean": 2, "Int": 1}
        props.sort(key=lambda p: type_value[p['data-type'].type_name])
        return props

    def get_props(self):
        props = [prop.get() for prop in self._props if prop.get() is not None]
        return self._sort_props(props)


class PropertyInput(Frame):
    """Input data required for a property"""

    def __init__(self, window, row_i):
        super().__init__(window)

        self._enum_options = []

        self._row_i = row_i

        self.type_components = []  # Holds type specific GUI components

        data_types = [EnumProp(), BoolProp(), IntProp()]

        self.col_i = 0
        # Type
        Label(self, text="Type").grid(row=self._row_i, column=self.col_i)
        self.col_i += 1
        self.type = Combobox(self)
        self.type['values'] = [prop.type_name for prop in data_types]
        self.type.bind("<<ComboboxSelected>>", self._type_options_display)
        self.type.current(0)
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
        elif type == "Int":
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
            raise Exception("Invalid Property Type: {}".format(type))

        button = Button(self, text="Remove", command=self.destroy)
        button.grid(row=self._row_i, column=self.col_i)
        self.type_components.append(button)
        self.col_i += 1

    def get(self):
        map = {'Boolean': BoolProp(), 'Enum': EnumProp(), 'Int': IntProp()}
        if self.winfo_exists():
            prop = {'data-type': map[self.children['!combobox'].get()],
                    'sub-type': self.children['!combobox2'].get(),
                    'name': self.children['!entry'].get().lower()}
            type = self.type.get()
            if type == "Boolean":
                prop['default'] = int(self.default.get())
            elif type == "Int":
                prop['min'] = int(self.type_components[1].get())
                prop['max'] = int(self.type_components[3].get())
                prop['default'] = int(self.type_components[5].get())
            elif type == "Enum":
                prop['default'] = self.type_components[1].get()
                prop['options'] = [option.get() for option in self._enum_options if option.winfo_exists()]
            else:
                raise Exception("Invalid Property Type")
            return prop


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
