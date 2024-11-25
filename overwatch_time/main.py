# overwatch_time/main.py

import sys
import os
import logging

from PyQt5 import QtWidgets

from .gui import MainWindow
from .utils import data_path

def main():
    """
    Main function to start the application.
    """
    # Setup logging
    LOG_FILE_PATH = data_path('MainProgram.log')

    # Ensure the data directory exists
    LOG_DIR = os.path.dirname(LOG_FILE_PATH)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(
        filename=LOG_FILE_PATH,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

