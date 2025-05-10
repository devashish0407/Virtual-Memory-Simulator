# gui/main_window.py
from PyQt5.QtWidgets import QMainWindow
from .widgets import VirtualMemoryWidgets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Virtual Memory Management Simulator")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget and set it
        self.central_widget = VirtualMemoryWidgets()
        self.setCentralWidget(self.central_widget)
