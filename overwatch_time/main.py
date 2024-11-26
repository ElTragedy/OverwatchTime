# overwatch_time/main.py

import sys
import os

from PyQt5 import QtWidgets

from .gui import MainWindow
from .update_checker import check_for_update

def ensure_directory_exists(path):
    """
    Ensure the directory for a given path exists. If not, create it.

    Parameters:
        path (str): The path to the directory or file.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Handle PyInstaller's frozen state for paths
if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Current working directory: {current_dir}")


def main():
    """
    Main function to start the application.
    """
    check_for_update()

    # Start the PyQt application
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        raise e

if __name__ == "__main__":
    main()
