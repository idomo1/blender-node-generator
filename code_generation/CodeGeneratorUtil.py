from os import path, pardir
import shutil
import subprocess


def write_license(fd):
    """Appends Blender license info to the file specified by the given file descriptor"""
    with open(path.join(path.dirname(__file__), pardir, "templates", "license.txt"), 'r') as license_f:
        shutil.copyfileobj(license_f, fd)


def apply_clang_formatting(file_path):
    """
    Applies clang formatting to the given file. Requires clang installation http://releases.llvm.org/download.html
    """
    subprocess.call(['clang-format', file_path, '-i'])


def uses_dna(props, node_type):
    """Whether the node requires an DNA struct
        DNA struct is required if props can't fit in shorts custom1/2 and floats custom3/4"""
    if node_type == "Texture":
        return True
    float_count = 0
    enum_count = 0
    bool_count = 0
    int_count = 0
    for prop in props:
        if prop['type'] == "Float":
            float_count += 1
        elif prop['type'] == "Enum":
            enum_count += 1
        elif prop['type'] == "Boolean":
            bool_count += 1
        elif prop['type'] == "Int":
            int_count += 1
        elif prop['type'] == "String":
            return True
    if enum_count > 2 or float_count > 2 or bool_count > 16 or int_count > 2:
        return True
    if enum_count + int_count > 2 or (enum_count + int_count == 2 and bool_count > 0):
        return True
    return False


def dna_padding_size(props):
    """Returns the padding size the dna struct requires
        Requires a padding member if the bytes size of the properties is not a multiple of 8"""
    byte_total = 0
    for prop in props:
        if prop["type"] == "String":
            byte_total += 2 * prop['size']
        else:
            byte_total += 4
    return (8 - byte_total % 8) if byte_total % 8 != 0 else 0


def string_lower_underscored(string):
    return string.replace(" ", "_").lower()


def string_upper_underscored(string):
    return string.replace(" ", "_").upper()


def string_capitalized_underscored(string):
    return "_".join(map(lambda s: s.capitalize(), string.split()))


def _string_capitalized_generic(string, delimiter):
    return delimiter.join(map(lambda s: s.capitalize(), string.split(" ")))


def string_capitalized_no_space(string):
    return _string_capitalized_generic(string, "")


def string_capitalized_spaced(string):
    return _string_capitalized_generic(string, " ")


def fill_socket_default(socket_defaults, count=4):
    """Fills unused socket defaults"""
    defaults = socket_defaults.split(',')
    if len(defaults) > 4:
        raise Exception("Socket has more than four defaults")
    filled_defaults = list(map(lambda d: d + 'f', defaults))
    filled_defaults.extend(['0.0f' for _ in range(count - len(defaults))])
    return ', '.join(filled_defaults)
