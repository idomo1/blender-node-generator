"""
A script which generates code for a basic blender node
Confirmed to work with Blender 2.8
"""

from gui import GUI
from code_generation import CodeGenerator

if __name__ == "__main__":
    menu = GUI(CodeGenerator)
    menu.display()
