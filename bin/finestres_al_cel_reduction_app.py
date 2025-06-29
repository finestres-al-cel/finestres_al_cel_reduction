"""Planet orbits app"""
import sys

from PyQt6.QtWidgets import QApplication

from finestres_al_cel_reduction.app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
