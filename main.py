from PySide6.QtWidgets import QApplication
from ui.login import LoginWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
