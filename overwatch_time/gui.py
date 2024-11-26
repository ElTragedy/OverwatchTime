# overwatch_time/gui.py

import os
import random
import datetime

from PyQt5 import QtWidgets, QtGui, QtCore

from .time_tracker import TimeTracker
from .utils import resource_path, format_duration

class MainWindow(QtWidgets.QMainWindow):
    """
    Main window of the application.
    """

    def __init__(self):
        super().__init__()

        # Initialize TimeTracker
        self.time_tracker = TimeTracker()

        self.setWindowTitle("Overwatch Time Script")
        self.setWindowIcon(QtGui.QIcon(os.path.join(resource_path('images'), 'download.ico')))

        # Screen size and window positioning
        self.center_window(500, 300)

        # Central widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Display random image
        self.display_random_image()

        # Create UI elements
        self.create_buttons()
        self.create_summary_label()

        # Initialize the app
        self.initialize_app()

        # Update weekly summary
        self.update_weekly_summary()

    def center_window(self, width, height):
        """
        Center the window on the screen.

        Parameters:
            width (int): Window width.
            height (int): Window height.
        """
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def display_random_image(self):
        """
        Display a random image from the images directory.
        """
        IMAGE_DIR = resource_path('images')
        png_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')]
        if png_files:
            random_png = random.choice(png_files)
            image_path = os.path.join(IMAGE_DIR, random_png)
            pixmap = QtGui.QPixmap(image_path)
            pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(label)

    def create_buttons(self):
        """
        Create Clock In and Clock Out buttons.
        """
        # Clock In button
        self.clock_in_button = QtWidgets.QPushButton("Clock In")
        self.clock_in_button.clicked.connect(self.gui_clock_in)
        self.layout.addWidget(self.clock_in_button)

        # Clock Out button
        self.clock_out_button = QtWidgets.QPushButton("Clock Out")
        self.clock_out_button.clicked.connect(self.gui_clock_out)
        self.layout.addWidget(self.clock_out_button)

    def create_summary_label(self):
        """
        Create the summary label to display total tracked time.
        """
        self.summary_label = QtWidgets.QLabel("Total seconds tracked this week: 0")
        self.layout.addWidget(self.summary_label)

    def gui_clock_in(self):
        """
        Handle the Clock In button click event.
        """
        if self.time_tracker.is_clocked_in():
            QtWidgets.QMessageBox.critical(self, "Error", "You are already clocked in, please clock out before trying to clock in again.")
        else:
            try:
                self.time_tracker.clock_in()
                QtWidgets.QMessageBox.information(self, "Clock In", f"Clocked in at {self.time_tracker.start_time}")
                self.clock_in_button.setEnabled(False)
                self.clock_out_button.setEnabled(True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to clock in: {e}")

    def gui_clock_out(self):
        """
        Handle the Clock Out button click event.
        """
        if not self.time_tracker.is_clocked_in():
            QtWidgets.QMessageBox.critical(self, "Error", "You must clock in first!")
        else:
            try:
                duration = self.time_tracker.clock_out()
                formatted_duration = format_duration(duration.total_seconds())
                QtWidgets.QMessageBox.information(self, "Clock Out", f"Clocked out after {formatted_duration}")
                self.update_weekly_summary()
                self.clock_in_button.setEnabled(True)
                self.clock_out_button.setEnabled(False)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to clock out: {e}")

    def update_weekly_summary(self):
        """
        Update the weekly summary label with total tracked time.
        """
        current_year, current_week, _ = datetime.datetime.now().isocalendar()
        total_seconds = self.time_tracker.weekly_summary(current_year, current_week)
        if total_seconds > 0:
            formatted_time = format_duration(total_seconds)
            self.summary_label.setText(f"Total time put in this week: {formatted_time}")
        else:
            self.summary_label.setText("No data available for this week.")

    def initialize_app(self):
        """
        Initialize the application state based on clock-in status.
        """
        if self.time_tracker.is_clocked_in():
            self.time_tracker.get_start_time()
            self.clock_in_button.setEnabled(False)
            self.clock_out_button.setEnabled(True)
            QtWidgets.QMessageBox.information(self, "Welcome Back", "You were clocked in. Please clock out when done.")
        else:
            self.clock_in_button.setEnabled(True)
            self.clock_out_button.setEnabled(False)

    def on_closing(self):
        """
        Actions to perform when the application is closing.
        """
        if self.time_tracker.is_clocked_in():
            with open(self.time_tracker.CLOCK_IN_STATUS_PATH, 'w') as file:
                file.write('True\n')
                file.write(str(datetime.datetime.now()))

    def closeEvent(self, event):
        """
        Override the closeEvent to include custom on_closing logic.
        """
        self.on_closing()
        event.accept()

