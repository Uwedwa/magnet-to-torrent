import sys,os,subprocess,threading,tempfile,time,shutil,re,zipfile,urllib.request,platform
from PyQt5.QtWidgets import QApplication,QMainWindow,QLabel,QLineEdit,QPushButton,QVBoxLayout,QHBoxLayout,QFileDialog,QProgressBar,QWidget,QMessageBox,QFrame,QSplitter
from PyQt5.QtCore import pyqtSignal,QObject,Qt,QByteArray
from PyQt5.QtGui import QIcon,QPixmap,QPainter,QFont,QColor,QPalette
from PyQt5.QtSvg import QSvgRenderer
class IconManager:
	@staticmethod
	def download_icon(url,resources_dir):
		icon_path=os.path.join(resources_dir,'icon.svg')
		try:urllib.request.urlretrieve(url,icon_path);return icon_path
		except Exception as e:print(f"Error downloading icon: {str(e)}");return None
	@staticmethod
	def get_application_icon(custom_path=None):
		if getattr(sys,'frozen',False):app_dir=os.path.dirname(sys.executable)
		else:app_dir=os.path.dirname(os.path.abspath(__file__))
		resources_dir=os.path.join(app_dir,'resources')
		if not os.path.exists(resources_dir):os.makedirs(resources_dir)
		if custom_path and os.path.exists(custom_path):icon_path=custom_path
		else:
			icon_path=os.path.join(resources_dir,'icon.svg')
			if not os.path.exists(icon_path):
				icon_url='https://raw.githubusercontent.com/Uwedwa/magnet-to-torrent/refs/heads/main/icon.svg';icon_path=IconManager.download_icon(icon_url,resources_dir)
				if not icon_path:return QIcon()
		return IconManager.svg_to_icon(icon_path)
	@staticmethod
	def svg_to_icon(svg_path):
		if not os.path.exists(svg_path):return QIcon()
		icon=QIcon();renderer=QSvgRenderer(svg_path)
		for size in[16,24,32,48,64,128]:pixmap=QPixmap(size,size);pixmap.fill(Qt.transparent);painter=QPainter(pixmap);renderer.render(painter);painter.end();icon.addPixmap(pixmap)
		return icon
class ResourceExtractor:
	@staticmethod
	def get_aria2c_path():
		if getattr(sys,'frozen',False):app_dir=os.path.dirname(sys.executable)
		else:app_dir=os.path.dirname(os.path.abspath(__file__))
		resources_dir=os.path.join(app_dir,'resources')
		if not os.path.exists(resources_dir):os.makedirs(resources_dir)
		system=platform.system().lower()
		if system=='windows':aria2c_name='aria2c.exe'
		else:aria2c_name='aria2c'
		aria2c_path=os.path.join(resources_dir,aria2c_name)
		if os.path.exists(aria2c_path):return aria2c_path
		try:
			if system=='windows':
				download_url='https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip';zip_path=os.path.join(resources_dir,'aria2c.zip');urllib.request.urlretrieve(download_url,zip_path)
				with zipfile.ZipFile(zip_path,'r')as zip_ref:
					for file in zip_ref.namelist():
						if file.endswith('aria2c.exe'):
							zip_ref.extract(file,resources_dir);extracted_path=os.path.join(resources_dir,file);shutil.move(extracted_path,aria2c_path);extracted_dir=os.path.dirname(extracted_path)
							if os.path.exists(extracted_dir)and extracted_dir!=resources_dir:shutil.rmtree(extracted_dir)
							break
				if os.path.exists(zip_path):os.remove(zip_path)
			else:return None
			if os.path.exists(aria2c_path):return aria2c_path
		except Exception as e:print(f"Error extracting aria2c: {str(e)}");return None
		return None
class WorkerSignals(QObject):progress=pyqtSignal(str);finished=pyqtSignal(str);error=pyqtSignal(str)
class ConversionWorker(threading.Thread):
	def __init__(self,magnet,output_path):super().__init__();self.magnet=magnet;self.output_path=output_path;self.signals=WorkerSignals();self.process=None;self.running=True;self.temp_dir=tempfile.mkdtemp()
	def run(self):
		try:
			aria2c_path=ResourceExtractor.get_aria2c_path()
			if not aria2c_path:self.signals.error.emit('Could not find or download aria2c. Please check your internet connection.');return
			name='download'
			if'dn='in self.magnet:
				match=re.search('dn=([^&]+)',self.magnet)
				if match:name=match.group(1).replace('+',' ')
			output_dir=os.path.dirname(os.path.abspath(self.output_path))
			if not os.path.exists(output_dir):os.makedirs(output_dir)
			cmd=[aria2c_path,'--dir='+self.temp_dir,'--bt-metadata-only=true','--bt-save-metadata=true','--follow-torrent=mem',self.magnet];self.signals.progress.emit('Starting aria2c to download metadata...');self.process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,universal_newlines=True)
			for line in iter(self.process.stdout.readline,''):
				if not self.running:
					if self.process:self.process.terminate()
					break
				line=line.strip();self.signals.progress.emit(line)
				if'Download complete'in line:self.signals.progress.emit('Metadata download complete. Finding torrent file...');break
			if not self.running:return
			self.process.wait()
			if self.process.returncode!=0:self.signals.error.emit(f"aria2c process failed with return code {self.process.returncode}");return
			torrent_files=[f for f in os.listdir(self.temp_dir)if f.endswith('.torrent')]
			if not torrent_files:self.signals.error.emit('No torrent file was created. The magnet link may be invalid.');return
			torrent_path=os.path.join(self.temp_dir,torrent_files[0]);output_path=self.output_path
			if os.path.isdir(output_path):output_path=os.path.join(output_path,f"{name}.torrent")
			self.signals.progress.emit(f"Saving torrent to {output_path}...");shutil.copy2(torrent_path,output_path);self.signals.finished.emit(output_path)
		except Exception as e:self.signals.error.emit(str(e))
		finally:
			try:
				if os.path.exists(self.temp_dir):shutil.rmtree(self.temp_dir)
			except:pass
	def stop(self):
		self.running=False
		if self.process:
			try:self.process.terminate()
			except:pass
class AppStyles:
	@staticmethod
	def setup_styles(app):font=QFont('Segoe UI',9);app.setFont(font);stylesheet='\n        QMainWindow {\n            background-color: \n        }\n        QWidget {\n            background-color: \n        }\n        QLabel {\n            color: \n            font-weight: normal;\n        }\n        QLabel\n            font-size: 16px;\n            font-weight: bold;\n            color: \n            padding: 5px;\n        }\n        QLineEdit {\n            border: 1px solid \n            border-radius: 4px;\n            padding: 6px;\n            background-color: white;\n        }\n        QLineEdit:focus {\n            border: 1px solid \n        }\n        QPushButton {\n            background-color: \n            color: white;\n            border: none;\n            border-radius: 4px;\n            padding: 6px 12px;\n            font-weight: bold;\n        }\n        QPushButton:hover {\n            background-color: \n        }\n        QPushButton:pressed {\n            background-color: \n        }\n        QPushButton:disabled {\n            background-color: \n            color: \n        }\n        QPushButton\n            background-color: \n            font-size: 12px;\n            padding: 8px 16px;\n        }\n        QPushButton\n            background-color: \n        }\n        QPushButton\n            background-color: \n            font-size: 12px;\n            padding: 8px 16px;\n        }\n        QPushButton\n            background-color: \n        }\n        QProgressBar {\n            border: 1px solid \n            border-radius: 4px;\n            text-align: center;\n            background-color: white;\n        }\n        QProgressBar::chunk {\n            background-color: \n        }\n        QFrame\n            background-color: white;\n            border-radius: 8px;\n            border: 1px solid \n        }\n        QLabel\n            font-weight: bold;\n            color: \n            font-size: 12px;\n        }\n        ';app.setStyleSheet(stylesheet)
	@staticmethod
	def create_section_frame(title,layout=None):
		frame=QFrame();frame.setObjectName('SectionFrame');frame.setStyleSheet('QFrame#SectionFrame { border: 1px solid #e0e0e0; border-radius: 8px; background-color: white; }');main_layout=QVBoxLayout(frame);main_layout.setContentsMargins(15,15,15,15)
		if title:title_label=QLabel(title);title_label.setObjectName('SectionTitle');main_layout.addWidget(title_label)
		if layout:main_layout.addLayout(layout)
		return frame
class MagnetToTorrentApp(QMainWindow):
	def __init__(self):
		super().__init__();self.setWindowTitle('Magnet to Torrent Converter');self.setMinimumSize(400,200)
		try:self.app_icon=IconManager.get_application_icon();self.setWindowIcon(self.app_icon)
		except Exception as e:print(f"Failed to set icon: {str(e)}");self.app_icon=QIcon()
		main_widget=QWidget();main_layout=QVBoxLayout(main_widget);main_layout.setContentsMargins(20,20,20,20);main_layout.setSpacing(15);header_layout=QHBoxLayout();icon_size=32;icon_label=QLabel()
		if not self.app_icon.isNull():pixmap=self.app_icon.pixmap(icon_size,icon_size);icon_label.setPixmap(pixmap)
		icon_label.setFixedSize(icon_size,icon_size);title_label=QLabel('Magnet to Torrent Converter');title_label.setObjectName('HeaderLabel');header_layout.addWidget(icon_label);header_layout.addWidget(title_label);header_layout.addStretch();main_layout.addLayout(header_layout);description=QLabel('Convert magnet links to .torrent files easily');description.setAlignment(Qt.AlignCenter);main_layout.addWidget(description);magnet_layout=QVBoxLayout();magnet_label=QLabel('Magnet URL:');self.magnet_input=QLineEdit();self.magnet_input.setPlaceholderText("Enter magnet link here (starting with 'magnet:')");magnet_layout.addWidget(magnet_label);magnet_layout.addWidget(self.magnet_input);magnet_section=AppStyles.create_section_frame('MAGNET LINK',magnet_layout);main_layout.addWidget(magnet_section);output_layout=QVBoxLayout();output_label=QLabel('Save to:');output_input_layout=QHBoxLayout();self.output_input=QLineEdit();self.output_input.setPlaceholderText('Select where to save the .torrent file');browse_button=QPushButton('Browse');browse_button.clicked.connect(self.browse_output);output_input_layout.addWidget(self.output_input);output_input_layout.addWidget(browse_button);output_layout.addWidget(output_label);output_layout.addLayout(output_input_layout);output_section=AppStyles.create_section_frame('OUTPUT LOCATION',output_layout);main_layout.addWidget(output_section);progress_layout=QVBoxLayout();self.progress_label=QLabel('Ready');self.progress_bar=QProgressBar();self.progress_bar.setRange(0,0);self.progress_bar.hide();progress_layout.addWidget(self.progress_label);progress_layout.addWidget(self.progress_bar);progress_section=AppStyles.create_section_frame('STATUS',progress_layout);main_layout.addWidget(progress_section);button_layout=QHBoxLayout();button_layout.addStretch();self.convert_button=QPushButton('Convert');self.convert_button.setObjectName('ConvertButton');self.convert_button.clicked.connect(self.start_conversion);self.convert_button.setMinimumWidth(120);self.cancel_button=QPushButton('Cancel');self.cancel_button.setObjectName('CancelButton');self.cancel_button.clicked.connect(self.cancel_conversion);self.cancel_button.setEnabled(False);self.cancel_button.setMinimumWidth(120);button_layout.addWidget(self.convert_button);button_layout.addWidget(self.cancel_button);button_layout.addStretch();main_layout.addLayout(button_layout);main_layout.addStretch();self.setCentralWidget(main_widget);self.worker=None;self.setup_aria2c()
	def setup_aria2c(self):
		self.progress_label.setText('Setting up required components...');aria2c_path=ResourceExtractor.get_aria2c_path()
		if aria2c_path:self.progress_label.setText('Ready')
		else:self.progress_label.setText('Failed to set up required components');self.convert_button.setEnabled(False)
	def browse_icon(self):
		file_dialog=QFileDialog();options=QFileDialog.Options();file_path,_=file_dialog.getOpenFileName(self,'Select SVG Icon','','SVG Files (*.svg)',options=options)
		if file_path:self.icon_input.setText(file_path)
	def apply_custom_icon(self):
		icon_path=self.icon_input.text().strip()
		if not icon_path:QMessageBox.warning(self,'Icon Error','Please select an SVG icon file');return
		if not os.path.exists(icon_path):QMessageBox.warning(self,'Icon Error','Selected file does not exist');return
		if not icon_path.lower().endswith('.svg'):QMessageBox.warning(self,'Icon Error','Only SVG files are supported');return
		try:
			self.app_icon=IconManager.svg_to_icon(icon_path);self.setWindowIcon(self.app_icon);header_layout=self.findChild(QWidget,'header_layout')
			if header_layout:
				icon_label=header_layout.itemAt(0).widget()
				if icon_label:pixmap=self.app_icon.pixmap(32,32);icon_label.setPixmap(pixmap)
			if getattr(sys,'frozen',False):app_dir=os.path.dirname(sys.executable)
			else:app_dir=os.path.dirname(os.path.abspath(__file__))
			resources_dir=os.path.join(app_dir,'resources')
			if not os.path.exists(resources_dir):os.makedirs(resources_dir)
			destination=os.path.join(resources_dir,'icon.svg');shutil.copy2(icon_path,destination);QApplication.setWindowIcon(self.app_icon);QMessageBox.information(self,'Success','Custom icon applied successfully')
		except Exception as e:QMessageBox.critical(self,'Error',f"Failed to apply custom icon: {str(e)}")
	def browse_output(self):
		file_dialog=QFileDialog();options=QFileDialog.Options();initial_filename='';magnet=self.magnet_input.text().strip()
		if magnet and'dn='in magnet:
			try:
				match=re.search('dn=([^&]+)',magnet)
				if match:initial_filename=match.group(1).replace('+',' ')+'.torrent'
			except:pass
		file_path,_=file_dialog.getSaveFileName(self,'Save Torrent File',initial_filename,'Torrent Files (*.torrent)',options=options)
		if file_path:
			if not file_path.endswith('.torrent'):file_path+='.torrent'
			self.output_input.setText(file_path)
	def start_conversion(self):
		aria2c_path=ResourceExtractor.get_aria2c_path()
		if not aria2c_path:QMessageBox.critical(self,'Error','Could not set up aria2c. Please check your internet connection.');return
		magnet=self.magnet_input.text().strip();output_path=self.output_input.text().strip()
		if not magnet:QMessageBox.warning(self,'Input Error','Please enter a magnet URL');return
		if not magnet.startswith('magnet:'):QMessageBox.warning(self,'Input Error','Invalid magnet URL format');return
		if not output_path:
			options=QFileDialog.Options();initial_filename=''
			if'dn='in magnet:
				try:
					match=re.search('dn=([^&]+)',magnet)
					if match:initial_filename=match.group(1).replace('+',' ')+'.torrent'
				except:pass
			file_path,_=QFileDialog.getSaveFileName(self,'Save Torrent File',initial_filename,'Torrent Files (*.torrent)',options=options)
			if not file_path:return
			if not file_path.endswith('.torrent'):file_path+='.torrent'
			output_path=file_path;self.output_input.setText(output_path)
		output_dir=os.path.dirname(os.path.abspath(output_path))
		if not os.path.exists(output_dir):
			try:os.makedirs(output_dir)
			except Exception as e:QMessageBox.critical(self,'Error',f"Cannot create output directory: {str(e)}");return
		self.progress_bar.show();self.progress_label.setText('Starting conversion...');self.convert_button.setEnabled(False);self.cancel_button.setEnabled(True);self.worker=ConversionWorker(magnet,output_path);self.worker.signals.progress.connect(self.update_progress);self.worker.signals.finished.connect(self.conversion_complete);self.worker.signals.error.connect(self.conversion_failed);self.worker.start()
	def cancel_conversion(self):
		if self.worker:self.worker.stop();self.progress_label.setText('Conversion cancelled');self.progress_bar.hide();self.convert_button.setEnabled(True);self.cancel_button.setEnabled(False)
	def update_progress(self,message):self.progress_label.setText(message)
	def conversion_complete(self,output_path):self.progress_bar.hide();self.progress_label.setText(f"Torrent saved to: {output_path}");self.convert_button.setEnabled(True);self.cancel_button.setEnabled(False);QMessageBox.information(self,'Success',f"Torrent file created successfully at:\n{output_path}")
	def conversion_failed(self,error_message):self.progress_bar.hide();self.progress_label.setText(f"Error: {error_message}");self.convert_button.setEnabled(True);self.cancel_button.setEnabled(False);QMessageBox.critical(self,'Error',f"Conversion failed: {error_message}")
if __name__=='__main__':
	app=QApplication(sys.argv);AppStyles.setup_styles(app);window=MagnetToTorrentApp()
	if not window.app_icon.isNull():app.setWindowIcon(window.app_icon)
	window.show();sys.exit(app.exec_())
