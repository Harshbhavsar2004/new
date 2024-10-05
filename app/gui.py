import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, 
    QTextEdit, QProgressBar, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog , QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap
from .scan_thread import AVScanThread
from .utils import WINDOW_TITLE, WINDOW_GEOMETRY

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def create_folders():
    desktop_path = get_desktop_path()
    target_folder = os.path.join(desktop_path, "Target Folder")
    infected_folder = os.path.join(desktop_path, "Infected Folder")

    os.makedirs(target_folder, exist_ok=True)
    os.makedirs(infected_folder, exist_ok=True)

    return target_folder, infected_folder

def copy_to_target_folder(source_dir, target_folder):
    if os.path.exists(source_dir):
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(target_folder, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

class AVScanApp(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.target_folder, self.infected_folder = create_folders()
        self.scan_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_GEOMETRY)
        
        # Set the window icon
        self.setWindowIcon(QIcon("logo.png"))  # Ensure the path to your logo is correct
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#2C3E50"))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 5px;
                height: 35px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
                color: #BDC3C7;
            }
            QLabel {
                font-size: 16px;
                color: #ECF0F1;
            }
            QTextEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #7F8C8D;
                border-radius: 5px;
            }
            QProgressBar {
                border: 2px solid #3498DB;
                border-radius: 5px;
                text-align: center;
                color: #ECF0F1;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                width: 10px;
                margin: 0.5px;
            }
            QTableWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #7F8C8D;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #3498DB;
                color: white;
                padding: 4px;
                border: 1px solid #7F8C8D;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.folder_label = QLabel("No folder selected", self)
        self.folder_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
        layout.addWidget(self.folder_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.folder_button = QPushButton("Select Folder", self)
        self.folder_button.setIcon(QIcon("folder_icon.png"))
        self.folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.folder_button)

        self.scan_button = QPushButton("Start Scan", self)
        self.scan_button.setIcon(QIcon("scan_icon.png"))
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setIcon(QIcon("cancel_icon.png"))
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        # Add a QTableWidget for displaying threats
        self.threat_table = QTableWidget(0, 3)
        self.threat_table.setHorizontalHeaderLabels(["Threat Type", "Threat Name", "File Path"])
        header = self.threat_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.threat_table)

        self.results = QTextEdit(self)
        self.results.setReadOnly(True)
        layout.addWidget(self.results)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"Selected Folder: {folder}")
        else:
            self.folder_label.setText("No folder selected")

    def start_scan(self):
        if self.folder_path:
            self.results.clear()
            self.threat_table.setRowCount(0)  # Clear the table
            self.results.append("Starting scan...")
            self.scan_button.setEnabled(False)
            self.folder_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setValue(0)

            # Copy files to the target folder
            copy_to_target_folder(self.folder_path, self.target_folder)

            self.scan_thread = AVScanThread(self.target_folder, self.infected_folder)
            self.scan_thread.progress.connect(self.update_progress)
            self.scan_thread.result.connect(self.update_results)
            self.scan_thread.error.connect(self.show_error)
            self.scan_thread.threat_found.connect(self.display_threat)
            self.scan_thread.finished.connect(self.scan_finished)
            self.scan_thread.start()
        else:
            QMessageBox.warning(self, "Error", "Please select a folder to scan.")

    def cancel_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
            self.results.append("Scan cancelled by user.")
            self.scan_finished()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_results(self, result):
        self.results.append(result)
        self.results.verticalScrollBar().setValue(self.results.verticalScrollBar().maximum())

    def show_error(self, error):
        QMessageBox.critical(self, "Error", error)
        self.results.append(f"Error: {error}")
        self.scan_finished()

    def scan_finished(self):
        self.scan_button.setEnabled(True)
        self.folder_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.results.append("Scan finished.")
        self.results.verticalScrollBar().setValue(self.results.verticalScrollBar().maximum())
        
        # Show a custom completion dialog
        self.show_completion_dialog()

    def show_completion_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Scan Completed")
        dialog.setFixedSize(400, 200)  # Set the desired width and height
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
                color: #ECF0F1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #ECF0F1;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 5px;
                height: 35px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        label = QLabel("The scan has been completed successfully.\nCheck the results for any detected threats.")
        layout.addWidget(label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def display_threat(self, file_path, threat_name, threat_type):
        # Add threat details to the table
        row_position = self.threat_table.rowCount()
        self.threat_table.insertRow(row_position)
        self.threat_table.setItem(row_position, 0, QTableWidgetItem(threat_type))
        self.threat_table.setItem(row_position, 1, QTableWidgetItem(threat_name))
        self.threat_table.setItem(row_position, 2, QTableWidgetItem(file_path))
        self.results.append(f"Threat found: {threat_name} in {file_path} (Type: {threat_type})")
        self.results.verticalScrollBar().setValue(self.results.verticalScrollBar().maximum())