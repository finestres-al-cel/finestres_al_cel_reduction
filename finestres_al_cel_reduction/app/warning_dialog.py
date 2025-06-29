"""Error Dialog """
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QVBoxLayout
)

class WarningDialog(QDialog):
    """ Class to define the dialog to report warnings

    Methods
    -------
    (see QDialog)
    __init__

    Arguments
    ---------
    (see QDialog)
    """
    def __init__(self, message):
        """Initialize instance

        Arguments
        ---------
        message: str
        Error message
        """
        super().__init__()

        self.setWindowTitle("Warning")

        # Skip and Cancel buttons
        QButtons = QDialogButtonBox.StandardButton.Ignore | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QButtons)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ignore).setText("Skip")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.handle_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def handle_button(self, button):
        """Handle button clicks in the dialog."""
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole or role == QDialogButtonBox.ButtonRole.DestructiveRole:
            self.accept()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()