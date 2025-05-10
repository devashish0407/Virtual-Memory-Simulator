# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow  # Importing MainWindow from 'gui'

def main():
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create the main window and display it
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
