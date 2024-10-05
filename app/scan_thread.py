import subprocess
import time
import logging
import re
from PyQt5.QtCore import QThread, pyqtSignal
import os
import shutil

# Set up logging
logging.basicConfig(filename='av_scan_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AVScanThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    threat_found = pyqtSignal(str, str, str)  # file_path, threat_name, threat_type
    error = pyqtSignal(str)

    def __init__(self, folder, infected_folder):
        super().__init__()
        self.folder = folder
        self.infected_folder = infected_folder
        self.is_running = True
        self.progress_value = 0

    def run(self):
        try:
            logging.debug("Scan thread started")

            mpcmdrun_path = os.path.join(os.environ.get('ProgramFiles'), 'Windows Defender', 'MpCmdRun.exe')
            if not os.path.exists(mpcmdrun_path):
                error_msg = f"MpCmdRun.exe not found at {mpcmdrun_path}"
                self.error.emit(error_msg)
                logging.error(error_msg)
                return

            command = f'"{mpcmdrun_path}" -Scan -ScanType 3 -File "{self.folder}" -DisableRemediation'
            
            self.result.emit(f"Starting scan with command: {command}")
            logging.info(f"Starting scan with command: {command}")
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            
            full_output = ""
            while self.is_running:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    full_output += output
                    self.result.emit(output.strip())
                    logging.debug(f"Received output: {output.strip()}")
                    self.progress_value = min(self.progress_value + 1, 100)
                    self.progress.emit(self.progress_value)
                
                time.sleep(0.1)

            rc = process.poll()
            if rc == 0 or rc == 2:  # 0: No threats, 2: Threats found
                self.result.emit("Scan completed.")
                self.parse_full_output(full_output)
            else:
                error_output = process.stderr.read()
                error_msg = f"Scan failed with unexpected return code {rc}. Error: {error_output}"
                self.error.emit(error_msg)
                logging.error(error_msg)
            
            self.result.emit(f"Full output: {full_output}")
            logging.debug(f"Full output: {full_output}")
        
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.error.emit(error_msg)
            logging.error(error_msg)

    def stop(self):
        self.is_running = False
        logging.info("Scan thread stop requested")

    def parse_full_output(self, full_output):
        # Adjust the pattern to match each file entry in the threat list
        pattern = r"Threat\s+:\s+(.*)\nResources\s+:\s+(\d+) total\n(?:\s+file\s+:\s+(.*)\n)+"
        matches = re.finditer(pattern, full_output, re.MULTILINE)
        for match in matches:
            threat_name = match.group(1)
            file_paths = re.findall(r"file\s+:\s+(.*)", match.group(0))
            for file_path in file_paths:
                threat_type = "Malware"  # Default type, adjust if more specific information is available
                self.threat_found.emit(file_path, threat_name, threat_type)
                self.result.emit(f"Threat found: {threat_name} in {file_path} (Type: {threat_type})")
                self.move_infected_file(file_path, threat_name)

    def move_infected_file(self, file_path, threat_name):
        try:
            if os.path.exists(file_path):
                dest_path = os.path.join(self.infected_folder, os.path.basename(file_path))
                shutil.move(file_path, dest_path)
                self.log_infected_file(dest_path, threat_name)
                logging.info(f"Moved infected file {file_path} to {dest_path}")
            else:
                logging.warning(f"File {file_path} does not exist and cannot be moved.")
        except Exception as e:
            logging.error(f"Failed to move infected file {file_path}: {str(e)}")

    def log_infected_file(self, file_path, threat_name):
        log_file = os.path.join(self.infected_folder, "infected_files_log.txt")
        with open(log_file, "a") as f:
            f.write(f"{file_path} - {threat_name}\n")