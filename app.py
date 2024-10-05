import sys
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, 
    QTextEdit, QProgressBar, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class AVScanThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.is_running = True
        self.progress_value = 0

    def run(self):
        try:
            # Use MpCmdRun.exe for scanning
            defender_command = f'"%ProgramFiles%\\Windows Defender\\MpCmdRun.exe" -Scan -ScanType 3 -File "{self.folder}"'
            
            process = subprocess.Popen(defender_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            
            while self.is_running:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.result.emit(output.strip())
                    # Update progress (this is an estimation, as Windows Defender doesn't provide direct progress)
                    self.progress_value = min(self.progress_value + 1, 100)
                    self.progress.emit(self.progress_value)
                
                time.sleep(0.1)  # Small delay to prevent high CPU usage

            rc = process.poll()
            if rc == 0:
                self.result.emit("Scan completed successfully.")
            else:
                error_output = process.stderr.read()
                self.error.emit(f"Scan failed with return code {rc}. Error: {error_output}")
        
        except Exception as e:
            self.error.emit(f"An error occurred: {str(e)}")

    def stop(self):
        self.is_running = False

class AVScanApp(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.scan_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Windows Defender Antivirus Scanner")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.folder_label = QLabel("No folder selected", self)
        layout.addWidget(self.folder_label)

        button_layout = QHBoxLayout()
        self.folder_button = QPushButton("Select Folder", self)
        self.folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.folder_button)

        self.scan_button = QPushButton("Start Scan", self)
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)

        self.cancel_button = QPushButton("Cancel Scan", self)
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

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
            self.results.append("Starting scan...")
            self.scan_button.setEnabled(False)
            self.folder_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setValue(0)  # Reset progress bar

            self.scan_thread = AVScanThread(self.folder_path)
            self.scan_thread.progress.connect(self.update_progress)
            self.scan_thread.result.connect(self.update_results)
            self.scan_thread.error.connect(self.show_error)
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

    def show_error(self, error):
        QMessageBox.critical(self, "Error", error)
        self.scan_finished()

    def scan_finished(self):
        self.scan_button.setEnabled(True)
        self.folder_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AVScanApp()
    window.show()
    sys.exit(app.exec_())
