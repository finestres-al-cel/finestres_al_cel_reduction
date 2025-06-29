""" Functions to load Actions"""
import os

from PyQt6.QtGui import QAction, QIcon, QPainter, QPixmap

from finestres_al_cel_reduction.app.environment import (
    BUTTONS_PATH, ICON_SIZE,
    get_background_color
)

def createIconWithBackground(icon_path, bg_color):
    """Create an icon with a visible background"""
    pixmap = QPixmap(ICON_SIZE, ICON_SIZE)
    pixmap.fill(bg_color)  # Fill the background with the specified color

    painter = QPainter(pixmap)
    icon = QPixmap(icon_path)
    icon = icon.scaled(ICON_SIZE - 4, ICON_SIZE - 4)  # Scale the icon to fit within the background
    painter.drawPixmap(2, 2, icon)  # Draw the icon with padding
    painter.end()

    return QIcon(pixmap)

def loadCalibrationMenuActions(window):
    """Load calibration menu actions

    Arguments
    ---------
    window: MainWindow
    Window where the actions will act

    Returns
    -------
    menuAction: list of QAction
    List of actions in the file menu
    """
    menuActions = []

    set_calibration_option = QAction(
        "&Set Calibration",
        window)
    set_calibration_option.setStatusTip("Set Calibration")
    set_calibration_option.triggered.connect(window.setCalibration)
    menuActions.append(set_calibration_option)

    calibrate_option = QAction(
        "&Calibrate All",
        window)
    calibrate_option.setStatusTip("Calibrate All")
    calibrate_option.triggered.connect(window.calibrateAll)
    menuActions.append(calibrate_option)

    return menuActions

def loadFileMenuActions(window):
    """Load file menu actions

    Arguments
    ---------
    window: MainWindow
    Window where the actions will act

    Returns
    -------
    menuAction: list of QAction
    List of actions in the file menu
    """
    menuActions = []

    load_spectrum_option = QAction(
        createIconWithBackground(
            os.path.join(BUTTONS_PATH, "open_file.png"),
            get_background_color(window.palette()),
        ),
        "&Load File(s)",
        window)
    load_spectrum_option.setStatusTip("Load File(s)")
    load_spectrum_option.triggered.connect(window.openFile)
    menuActions.append(load_spectrum_option)

    return menuActions

def loadStackMenuActions(window):
    """Load stack menu actions

    Arguments
    ---------
    window: MainWindow
    Window where the actions will act

    Returns
    -------
    menuAction: list of QAction
    List of actions in the file menu
    """
    menuActions = []

    stack_option = QAction(
        "&Stack",
        window)
    stack_option.setStatusTip("Stack")
    stack_option.triggered.connect(window.stackFiles)
    menuActions.append(stack_option)

    color_stack_option = QAction(
        "&Color Stack",
        window)
    color_stack_option.setStatusTip("Color Stack")
    color_stack_option.triggered.connect(window.colorStack)
    menuActions.append(color_stack_option)

    return menuActions