import json
from tkinter import filedialog


class NodeConfig:
    def __init__(self, gui):
        self._gui = gui

    def save_config(self):
        file_path = filedialog.asksaveasfilename()
        if not file_path:
            return
        with open(file_path, 'w') as f:
            data = self._gui.serialize()
            print(data)
            json.dump(data, f)

    def load_config(self):
        f = filedialog.askopenfile()
        if not f:
            return
        data = json.load(f)
        self._gui.deserialize(data)
