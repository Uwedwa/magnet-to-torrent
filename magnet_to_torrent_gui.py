import sys
import os
import subprocess
import threading
import tempfile
import time
import shutil
import re
import zipfile
import urllib.request
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                           QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, 
                           QProgressBar, QWidget, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject, Qt

class ResourceExtractor:
    @staticmethod
    def get_aria2c_path():

        if getattr(sys, 'frozen', False):

            app_dir = os.path.dirname(sys.executable)
        else:

            app_dir = os.path.dirname(os.path.abspath(__file__))

        resources_dir = os.path.join(app_dir, "resources")
        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)

        system = platform.system().lower()
        if system == "windows":
            aria2c_name = "aria2c.exe"
        else:
            aria2c_name = "aria2c"

        aria2c_path = os.path.join(resources_dir, aria2c_name)

        if os.path.exists(aria2c_path):
            return aria2c_path

        try:
            if system == "windows":

                download_url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip"
                zip_path = os.path.join(resources_dir, "aria2c.zip")
                urllib.request.urlretrieve(download_url, zip_path)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith("aria2c.exe"):
                            zip_ref.extract(file, resources_dir)
                            extracted_path = os.path.join(resources_dir, file)

                            shutil.move(extracted_path, aria2c_path)

                            extracted_dir = os.path.dirname(extracted_path)
                            if os.path.exists(extracted_dir) and extracted_dir != resources_dir:
                                shutil.rmtree(extracted_dir)
                            break

                if os.path.exists(zip_path):
                    os.remove(zip_path)

            else:

                return None

            if os.path.exists(aria2c_path):
                return aria2c_path

        except Exception as e:
            print(f"Error extracting aria2c: {str(e)}")
            return None

        return None

class WorkerSignals(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class ConversionWorker(threading.Thread):
    def __init__(self, magnet, output_path):
        super().__init__()
        self.magnet = magnet
        self.output_path = output_path
        self.signals = WorkerSignals()
        self.process = None
        self.running = True
        self.temp_dir = tempfile.mkdtemp()

    def run(self):
        try:

            aria2c_path = ResourceExtractor.get_aria2c_path()
            if not aria2c_path:
                self.signals.error.emit("Could not find or download aria2c. Please check your internet connection.")
                return

            name = "download"
            if "dn=" in self.magnet:
                match = re.search(r"dn=([^&]+)", self.magnet)
                if match:
                    name = match.group(1).replace("+", " ")

            output_dir = os.path.dirname(os.path.abspath(self.output_path))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            cmd = [
                aria2c_path,
                "--dir=" + self.temp_dir,
                "--bt-metadata-only=true",
                "--bt-save-metadata=true",
                "--follow-torrent=mem",
                self.magnet
            ]

            self.signals.progress.emit("Starting aria2c to download metadata...")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    if self.process:
                        self.process.terminate()
                    break

                line = line.strip()
                self.signals.progress.emit(line)

                if "Download complete" in line:
                    self.signals.progress.emit("Metadata download complete. Finding torrent file...")
                    break

            if not self.running:
                return

            self.process.wait()

            if self.process.returncode != 0:
                self.signals.error.emit(f"aria2c process failed with return code {self.process.returncode}")
                return

            torrent_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.torrent')]
            if not torrent_files:
                self.signals.error.emit("No torrent file was created. The magnet link may be invalid.")
                return

            torrent_path = os.path.join(self.temp_dir, torrent_files[0])

            output_path = self.output_path
            if os.path.isdir(output_path):
                output_path = os.path.join(output_path, f"{name}.torrent")

            self.signals.progress.emit(f"Saving torrent to {output_path}...")
            shutil.copy2(torrent_path, output_path)

            self.signals.finished.emit(output_path)

        except Exception as e:
            self.signals.error.emit(str(e))

        finally:

            try:
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
            except:
                pass

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
            except:
                pass

class MagnetToTorrentApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Magnet to Torrent Converter")
        self.setMinimumSize(600, 250)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        instructions = QLabel("Convert magnet links to .torrent files")
        instructions.setStyleSheet("font-weight: bold; font-size: 14px;")

        magnet_layout = QVBoxLayout()
        magnet_label = QLabel("Magnet URL:")
        self.magnet_input = QLineEdit()
        self.magnet_input.setPlaceholderText("Enter magnet link here (starting with 'magnet:')")
        magnet_layout.addWidget(magnet_label)
        magnet_layout.addWidget(self.magnet_input)

        output_layout = QHBoxLayout()
        output_label = QLabel("Save to:")
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Select where to save the .torrent file")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(browse_button)

        self.progress_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_conversion)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white;")
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(instructions)
        main_layout.addSpacing(10)
        main_layout.addLayout(magnet_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(output_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.worker = None

        self.setup_aria2c()

    def setup_aria2c(self):

        self.progress_label.setText("Setting up required components...")
        aria2c_path = ResourceExtractor.get_aria2c_path()
        if aria2c_path:
            self.progress_label.setText("Ready")
        else:
            self.progress_label.setText("Failed to set up required components")
            self.convert_button.setEnabled(False)

    def browse_output(self):
        file_dialog = QFileDialog()
        options = QFileDialog.Options()

        initial_filename = ""

        magnet = self.magnet_input.text().strip()
        if magnet and "dn=" in magnet:
            try:
                match = re.search(r"dn=([^&]+)", magnet)
                if match:
                    initial_filename = match.group(1).replace("+", " ") + ".torrent"
            except:
                pass

        file_path, _ = file_dialog.getSaveFileName(
            self, "Save Torrent File", initial_filename, "Torrent Files (*.torrent)", options=options
        )
        if file_path:
            if not file_path.endswith(".torrent"):
                file_path += ".torrent"
            self.output_input.setText(file_path)

    def start_conversion(self):

        aria2c_path = ResourceExtractor.get_aria2c_path()
        if not aria2c_path:
            QMessageBox.critical(self, "Error", "Could not set up aria2c. Please check your internet connection.")
            return

        magnet = self.magnet_input.text().strip()
        output_path = self.output_input.text().strip()

        if not magnet:
            QMessageBox.warning(self, "Input Error", "Please enter a magnet URL")
            return

        if not magnet.startswith("magnet:"):
            QMessageBox.warning(self, "Input Error", "Invalid magnet URL format")
            return

        if not output_path:

            options = QFileDialog.Options()
            initial_filename = ""
            if "dn=" in magnet:
                try:
                    match = re.search(r"dn=([^&]+)", magnet)
                    if match:
                        initial_filename = match.group(1).replace("+", " ") + ".torrent"
                except:
                    pass

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Torrent File", initial_filename, "Torrent Files (*.torrent)", options=options
            )
            if not file_path:
                return

            if not file_path.endswith(".torrent"):
                file_path += ".torrent"

            output_path = file_path
            self.output_input.setText(output_path)

        output_dir = os.path.dirname(os.path.abspath(output_path))
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create output directory: {str(e)}")
                return

        self.progress_bar.show()
        self.progress_label.setText("Starting conversion...")
        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.worker = ConversionWorker(magnet, output_path)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.conversion_complete)
        self.worker.signals.error.connect(self.conversion_failed)
        self.worker.start()

    def cancel_conversion(self):
        if self.worker:
            self.worker.stop()
            self.progress_label.setText("Conversion cancelled")
            self.progress_bar.hide()
            self.convert_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def update_progress(self, message):
        self.progress_label.setText(message)

    def conversion_complete(self, output_path):
        self.progress_bar.hide()
        self.progress_label.setText(f"Torrent saved to: {output_path}")
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.information(self, "Success", f"Torrent file created successfully at:\n{output_path}")

    def conversion_failed(self, error_message):
        self.progress_bar.hide()
        self.progress_label.setText(f"Error: {error_message}")
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.critical(self, "Error", f"Conversion failed: {error_message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MagnetToTorrentApp()
    window.show()
    sys.exit(app.exec_())