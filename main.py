import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt5.QtWidgets import QApplication
from app.gui import AVScanApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AVScanApp()
    window.show()
    sys.exit(app.exec_())