- Author: Aaron Sierra

# Requirements

- python 3

# Directions

Install python 3 if you havent already.

Before running the script, run pythonInstall.ps1 to install the required python packages.
This is just a list of "pip install" commands.

You only need to run pythonInstall one per update to the script. If you run it
once, you should be good to go until the next update to the script.

To run the script, run the following command:
python .\SayreTimeScript.py

# How to add images

Import a png image in the images folder. The size does not matter, the program will
auto resize any image so long as it is a png.


# Command for my reference:
pyinstaller --onefile --icon=OverwatchTime.ico OverwatchTime.py

# TODO:
create a VM and test out the 3 use cases:
- Download and run the installer fresh
- Run the exe after there is an update and update it from the exe itself
- run the installer when there is no need to run it

- Made changes to the readme to test the EXE
