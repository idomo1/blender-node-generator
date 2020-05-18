# Blender Node Generator
A tool for generating a new blender shading node
![](demo.gif)

## Running the Tool
To run the tool, download the repository and run main.py using a python interpreter.   
### Windows and Mac
Dependencies
- Python 3.8
### Linux
Dependencies
- Python 3.8
- Tkinter  

Linux's python installation doesn't come with Tkinter by default, so it needs to be installed manually.  
Instructions differ per distribution, if you are on a Debian based distro, tkinter can be installed with the following command:  
```
sudo apt-get install python3-tk
```

## Undoing Changes
There is currently no undo option in the tool.  
That is why it is important that you use version control so that you can undo any unwanted changes  
Using git, you can run the following command to undo any changes  
```
git reset --hard && git clean -f -d  
```
<b>Be careful you don't have any uncommitted changes you wish to keep!</b>

## Unsupported Use Cases
It's not possible for me to predict how all node variations will be implemented.  
The following use cases aren't fully support(i.e You won't be able to successfully build Blender after running the tool)  
  * Nodes with \> 2 Enum Properties
  * Nodes with string properties
  * Nodes with more than 12 properties + sockets
