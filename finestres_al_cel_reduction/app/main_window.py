"""planet_orbits main window"""
import os

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QStatusBar,
    QToolBar,
)

from finestres_al_cel_reduction.app.environment import (
    HEIGHT, ICON_SIZE, MENU_FONT_SIZE, SUB_WINDOW_SIZE, 
    TITLE_FONT_SIZE, WIDTH, 
    get_colors,
)
from finestres_al_cel_reduction.app.error_dialog import ErrorDialog
from finestres_al_cel_reduction.app.fits_file_view import FitsFileView
from finestres_al_cel_reduction.app.load_actions import (
    loadCalibrationMenuActions, loadFileMenuActions,
    loadStackMenuActions, 
)
from finestres_al_cel_reduction.app.set_calibration_dialog import SetCalibrationDialog
from finestres_al_cel_reduction.app.success_dialog import SuccessDialog
from finestres_al_cel_reduction.app.stack_dialog import StackDialog
from finestres_al_cel_reduction.app.warning_dialog import WarningDialog

from finestres_al_cel_reduction.fits_file import FitsFile

class MainWindow(QMainWindow):
    """Main Window

    Methods
    -------
    (see QMainWindow)
    __init__
    _createToolBar
    _createMenuBar
    _createStatusBar
    _loadActions

    Attributes
    ----------
    (see QMainWindow)

    centralWidget: QtWidget
    Central widget
    """
    def __init__(self):
        """Initialize class instance """
        super().__init__()

        self.setGeometry(0, 0, WIDTH, HEIGHT)

        self.mdiArea = QMdiArea()
        self.setCentralWidget(self.mdiArea)

        #self.centralWidget = QLabel("Welcome. Open file to start.")
        # Dynamically setup color scheme
        #palette = self.palette()
        #background_color, text_color = get_colors(palette)
        #self.centralWidget.setStyleSheet(
        #    f"background-color: {background_color}; "
        #    f"color: {text_color}; "
        #    f" font-size: {TITLE_FONT_SIZE}px; ")
        #self.centralWidget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.setCentralWidget(self.centralWidget)
        
        # Load actions
        self.fileActions = loadFileMenuActions(self)
        self.calibrateActions = loadCalibrationMenuActions(self)
        self.stackActions = loadStackMenuActions(self)

        # Create menues
        self._createToolBar()
        self._createStatusBar()
        self._createMenuBar()

        # define variables
        self.files = []
        self.master_darks = {}
        self.master_flats = {}
        self.stack = {}

    def _createToolBar(self):
        """Create tool bars"""
        fileToolBar = QToolBar("File toolbar")
        #fileToolBar.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        fileToolBar.setFont(QFont("", MENU_FONT_SIZE))
        for menuAction in self.fileActions:
            fileToolBar.addAction(menuAction)
            fileToolBar.addSeparator()
        self.addToolBar(fileToolBar)

    def _createMenuBar(self):
        """Create menu bars"""
        menu = self.menuBar()

        fileMenu = menu.addMenu("&File")
        for menuAction in self.fileActions:
            fileMenu.addAction(menuAction)
            fileMenu.addSeparator()

        calibrateMenu = menu.addMenu("&Calibration")
        for menuAction in self.calibrateActions:
            calibrateMenu.addAction(menuAction)
            calibrateMenu.addSeparator()

        stackMenu = menu.addMenu("&Stack")
        for menuAction in self.stackActions:
            stackMenu.addAction(menuAction)
            stackMenu.addSeparator()

    def _createStatusBar(self):
        """Create status bar"""
        self.setStatusBar(QStatusBar(self))

    @pyqtSlot()
    def calibrateAll(self):
        """Set calibration for all file views"""
        if len(self.master_darks) == 0 or len(self.master_flats) == 0:
            errorDialog = ErrorDialog(
                "Error: No master dark or flat frames found. "
                "Please set calibration frames before calibrating files.")
            errorDialog.exec()
            return

        for file in self.files:
            if file.type == "IMAGE":
                # Calibrate the file with the master dark and flat frames
                dark_list = self.master_darks.get(file.exposure_time, None)
                if dark_list is None:
                    dark = None
                    warningDialog = WarningDialog(
                        f"Warning: No master dark found for {file.exposure_time}s exposure time.\n"
                        "Calibration will proceed without dark subtraction.")
                    warningDialog.exec()
                    if warningDialog.result() == QDialog.DialogCode.Rejected:
                        return
                    
                else:
                    dark = dark_list[0]
                flat_list = self.master_flats.get(file.filter, None)
                if flat_list is None:
                    flat = None
                    warningDialog = WarningDialog(
                        f"Warning: No master flat found for filter {file.filter}.\n"
                        "Calibration will proceed without flat division.")
                    warningDialog.exec()
                    if warningDialog.result() == QDialog.DialogCode.Rejected:
                        return
                else:
                    flat = flat_list[0]
                try:
                    file.calibrate(dark=dark, flat=flat)
                except Exception as e:
                    errorDialog = ErrorDialog(f"Error calibrating {file.title}: {str(e)}")
                    errorDialog.exec()

        # Update all FitsFileView plots
        for subwindow in self.mdiArea.subWindowList():
            widget = subwindow.widget()
            if isinstance(widget, FitsFileView):
                widget.updatePlot()

    def closeEvent(self, event):
        """Ensure all subwindows are closed when main window closes."""
        if hasattr(self, "mdiArea"):
            self.mdiArea.closeAllSubWindows()
        super().closeEvent(event)

    @pyqtSlot()
    def colorStack(self):
        """Stack files"""
        pass

    @pyqtSlot()
    def openFile(self):
        """Open dialog to select and open file"""
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Open File (s)",
            "${HOME}",
            "Fits (*.fits *.fit *.fits.gz);; CSV (*.csv);; Data (*dat);; Text (*txt);; All files (*)",
        )

        if filenames:
            for filename in filenames:
                # fits files
                if filename.endswith(".fits") or filename.endswith(".fit") or filename.endswith(".fits.gz"):
                    try:
                        file = FitsFile(filename)
                    
                    except Exception as e:
                        # Show error dialog
                        errorDialog = ErrorDialog(str(e))
                        errorDialog.exec()
                        raise e
                    
                    self.files.append(file)
                    if file.type == "IMAGE":
                        # load image view
                        fileView = FitsFileView(file)

                        # display in subwindow
                        subWindow = QMdiSubWindow()
                        subWindow.setWidget(fileView)
                        subWindow.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                        subWindow.setWindowTitle(file.title)
            
                        subWindow.setFixedSize(SUB_WINDOW_SIZE, SUB_WINDOW_SIZE)

                        self.mdiArea.addSubWindow(subWindow)
                        subWindow.show()

                # TODO: add other file types
        
    @pyqtSlot()
    def setCalibration(self):
        """Set calibration for the current file view"""
        set_calibration_window = SetCalibrationDialog()
        if set_calibration_window.exec() == QDialog.DialogCode.Accepted:
            self.master_darks = set_calibration_window.master_darks
            self.master_flats = set_calibration_window.master_flats
            
            if len(self.master_darks) > 0 and len(self.master_flats) > 0:
                # Show success dialog
                successDialog = SuccessDialog("Calibration set successfully.")
                successDialog.exec()
            else:
                errorDialog = ErrorDialog(
                    "Error: No master dark or flat frames found. "
                    "Please set calibration frames before calibrating files.")
                errorDialog.exec()
                return
    
    @pyqtSlot()
    def stackFiles(self):
        """Stack images to improve SNR"""
        stack_window = StackDialog(self.files)
        if stack_window.exec() == QDialog.DialogCode.Accepted:
            self.stack = stack_window.stack

            for file in self.stack.values():
                fileView = FitsFileView(file)

                # display in subwindow
                subWindow = QMdiSubWindow()
                subWindow.setWidget(fileView)
                subWindow.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                subWindow.setWindowTitle(file.title)
    
                subWindow.setFixedSize(SUB_WINDOW_SIZE, SUB_WINDOW_SIZE)

                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()
