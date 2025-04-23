_O='complete'
_N='waiting'
_M='Processing...'
_L='#34495e'
_K='#dce4ec'
_J='#3498db'
_I='resources'
_H='frozen'
_G='icon.svg'
_F=b'opacity'
_E='processing'
_D=None
_C=1.
_B=True
_A=False
import sys,os,subprocess,threading,tempfile,time,shutil,re,zipfile,urllib.request,platform
from PyQt5.QtWidgets import QApplication,QMainWindow,QLabel,QLineEdit,QPushButton,QVBoxLayout,QHBoxLayout,QFileDialog,QProgressBar,QWidget,QMessageBox,QFrame,QSplitter,QTextEdit,QScrollArea,QListWidget,QListWidgetItem,QGraphicsOpacityEffect
from PyQt5.QtCore import pyqtSignal,QObject,Qt,QByteArray,QPropertyAnimation,QEasingCurve,QTimer,QSize,QRect
from PyQt5.QtGui import QIcon,QPixmap,QPainter,QFont,QColor,QPalette,QFontMetrics,QLinearGradient,QGradient
from PyQt5.QtSvg import QSvgRenderer
class IconManager:
	@staticmethod
	def download_icon(url,resources_dir):
		A=os.path.join(resources_dir,_G)
		try:urllib.request.urlretrieve(url,A);return A
		except Exception as B:print(f"Error downloading icon: {str(B)}");return _D
	@staticmethod
	def get_application_icon(custom_path=_D):
		C=custom_path
		if getattr(sys,_H,_A):D=os.path.dirname(sys.executable)
		else:D=os.path.dirname(os.path.abspath(__file__))
		B=os.path.join(D,_I)
		if not os.path.exists(B):os.makedirs(B)
		if C and os.path.exists(C):A=C
		else:
			A=os.path.join(B,_G)
			if not os.path.exists(A):
				E='https://raw.githubusercontent.com/Uwedwa/magnet-to-torrent/refs/heads/main/icon.svg';A=IconManager.download_icon(E,B)
				if not A:return QIcon()
		return IconManager.svg_to_icon(A)
	@staticmethod
	def svg_to_icon(svg_path):
		B=svg_path
		if not os.path.exists(B):return QIcon()
		C=QIcon();F=QSvgRenderer(B)
		for D in[16,24,32,48,64,128,256]:A=QPixmap(D,D);A.fill(Qt.transparent);E=QPainter(A);F.render(E);E.end();C.addPixmap(A)
		return C
class ResourceExtractor:
	@staticmethod
	def get_aria2c_path():
		L='aria2c.exe';K='windows'
		if getattr(sys,_H,_A):F=os.path.dirname(sys.executable)
		else:F=os.path.dirname(os.path.abspath(__file__))
		A=os.path.join(F,_I)
		if not os.path.exists(A):os.makedirs(A)
		G=platform.system().lower()
		if G==K:H=L
		else:H='aria2c'
		B=os.path.join(A,H)
		if os.path.exists(B):return B
		try:
			if G==K:
				M='https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip';C=os.path.join(A,'aria2c.zip');urllib.request.urlretrieve(M,C)
				with zipfile.ZipFile(C,'r')as I:
					for D in I.namelist():
						if D.endswith(L):
							I.extract(D,A);J=os.path.join(A,D);shutil.move(J,B);E=os.path.dirname(J)
							if os.path.exists(E)and E!=A:shutil.rmtree(E)
							break
				if os.path.exists(C):os.remove(C)
			else:return _D
			if os.path.exists(B):return B
		except Exception as N:print(f"Error extracting aria2c: {str(N)}");return _D
		return _D
class WorkerSignals(QObject):progress=pyqtSignal(str,str,int);finished=pyqtSignal(str,str);error=pyqtSignal(str,str)
class ConversionWorker(threading.Thread):
	def __init__(A,magnet_id,magnet,output_dir):super().__init__();A.magnet_id=magnet_id;A.magnet=magnet;A.output_dir=output_dir;A.signals=WorkerSignals();A.process=_D;A.running=_B;A.temp_dir=tempfile.mkdtemp()
	def run(A):
		try:
			D=ResourceExtractor.get_aria2c_path()
			if not D:A.signals.error.emit(A.magnet_id,'Could not find or download aria2c. Please check your internet connection.');return
			E='download'
			if'dn='in A.magnet:
				C=re.search('dn=([^&]+)',A.magnet)
				if C:E=C.group(1).replace('+',' ')
			if not os.path.exists(A.output_dir):os.makedirs(A.output_dir)
			I=[D,'--dir='+A.temp_dir,'--bt-metadata-only=true','--bt-save-metadata=true','--follow-torrent=mem',A.magnet];A.signals.progress.emit(A.magnet_id,'Starting download...',0);A.process=subprocess.Popen(I,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=_B,bufsize=1,universal_newlines=_B)
			for B in iter(A.process.stdout.readline,''):
				if not A.running:
					if A.process:A.process.terminate()
					break
				B=B.strip();F=-1
				if'%'in B:
					C=re.search('(?P<percent>\\d+)%',B)
					if C:F=int(C.group('percent'))
				A.signals.progress.emit(A.magnet_id,B,F)
				if'Download complete'in B:A.signals.progress.emit(A.magnet_id,'Metadata download complete!',100);break
			if not A.running:return
			A.process.wait()
			if A.process.returncode!=0:A.signals.error.emit(A.magnet_id,f"aria2c process failed with return code {A.process.returncode}");return
			A.signals.progress.emit(A.magnet_id,'Processing metadata...',-1);G=[A for A in os.listdir(A.temp_dir)if A.endswith('.torrent')]
			if not G:A.signals.error.emit(A.magnet_id,'No torrent file was created. The magnet link may be invalid.');return
			J=os.path.join(A.temp_dir,G[0]);H=os.path.join(A.output_dir,f"{E}.torrent");A.signals.progress.emit(A.magnet_id,f"Saving torrent file...",100);shutil.copy2(J,H);A.signals.finished.emit(A.magnet_id,H)
		except Exception as K:A.signals.error.emit(A.magnet_id,str(K))
		finally:
			try:
				if os.path.exists(A.temp_dir):shutil.rmtree(A.temp_dir)
			except:pass
	def stop(A):
		A.running=_A
		if A.process:
			try:A.process.terminate()
			except:pass
class AnimatedProgressBar(QProgressBar):
	def __init__(A,parent=_D):super().__init__(parent);A.setRange(0,100);A.setValue(0);A.setTextVisible(_B);A.animation_timer=QTimer(A);A.animation_timer.timeout.connect(A.update_animation);A.animation_offset=0;A.indeterminate=_A;A.setMinimumHeight(16);A.setStyleSheet('\n            QProgressBar {\n                border: 1px solid #dce4ec;\n                border-radius: 5px;\n                text-align: center;\n                color: #34495e;\n                background-color: white;\n                font-size: 10px;\n            }\n            QProgressBar::chunk {\n                border-radius: 4px;\n            }\n        ')
	def set_indeterminate(A,indeterminate):
		B=indeterminate;A.indeterminate=B
		if B:A.animation_timer.start(50)
		else:A.animation_timer.stop()
		A.update()
	def paintEvent(A,event):
		if not A.indeterminate:super().paintEvent(event);return
		B=QPainter(A);B.setRenderHint(QPainter.Antialiasing);G=QColor(_J);B.setPen(Qt.NoPen);D=QRect(0,0,A.width(),A.height());B.fillRect(D,QColor('white'));B.setPen(QColor(_K));B.drawRoundedRect(0,0,A.width()-1,A.height()-1,5,5);B.setPen(Qt.NoPen);C=A.width()/5;B.setBrush(G);E=A.animation_offset*A.width()%(A.width()+C)-C
		if E<A.width():B.drawRoundedRect(int(E),2,int(C),A.height()-4,4,4)
		F=(A.animation_offset*A.width()+A.width()/3)%(A.width()+C)-C
		if F<A.width():B.drawRoundedRect(int(F),2,int(C),A.height()-4,4,4)
		B.setPen(QColor(_L));B.drawText(D,Qt.AlignCenter,_M)
	def update_animation(A):A.animation_offset=(A.animation_offset+.03)%_C;A.update()
class MagnetConversionItem(QWidget):
	def __init__(A,magnet_id,magnet_url,parent=_D):super().__init__(parent);A.magnet_id=magnet_id;A.magnet_url=magnet_url;B=QVBoxLayout(A);B.setContentsMargins(10,10,10,10);B.setSpacing(6);C=QHBoxLayout();D=QLabel();D.setFixedSize(16,16);A.status_icon=D;E=QLabel(A.get_shortened_url());E.setTextInteractionFlags(Qt.TextSelectableByMouse);G=QFont();G.setBold(_B);E.setFont(G);C.addWidget(D);C.addWidget(E);C.addStretch();F=QHBoxLayout();A.status_label=QLabel('Waiting to start...');A.status_label.setWordWrap(_B);A.progress_bar=AnimatedProgressBar();A.progress_bar.setFixedHeight(16);A.progress_bar.setValue(0);F.addWidget(A.status_label);F.addWidget(A.progress_bar);B.addLayout(C);B.addLayout(F);A.setAutoFillBackground(_B);H=A.palette();H.setColor(QPalette.Window,QColor('#f8f9fa'));A.setPalette(H);A.fade_animation=QPropertyAnimation(A,b'windowOpacity');A.fade_animation.setDuration(500);A.fade_animation.setStartValue(.0);A.fade_animation.setEndValue(_C);A.fade_animation.setEasingCurve(QEasingCurve.OutCubic);A.fade_animation.start();A.set_status_icon(_N)
	def get_shortened_url(A):
		if len(A.magnet_url)>80:return A.magnet_url[:77]+'...'
		return A.magnet_url
	def set_status_icon(E,status):
		C=status;D=QPixmap(16,16);D.fill(Qt.transparent);A=QPainter(D);A.setRenderHint(QPainter.Antialiasing)
		if C==_N:B=QColor('#f39c12')
		elif C==_E:B=QColor(_J)
		elif C==_O:B=QColor('#2ecc71')
		elif C=='error':B=QColor('#e74c3c')
		else:B=QColor('#95a5a6')
		A.setPen(Qt.NoPen);A.setBrush(B);A.drawEllipse(2,2,12,12);A.end();E.status_icon.setPixmap(D)
	def update_status(A,status,progress=-1):
		B=progress;A.status_label.setText(status)
		if B>=0 and B<=100:A.progress_bar.set_indeterminate(_A);A.progress_bar.setValue(B);A.set_status_icon(_E)
		else:A.progress_bar.set_indeterminate(_B);A.set_status_icon(_E)
	def mark_complete(A,output_path):A.progress_bar.set_indeterminate(_A);A.progress_bar.setValue(100);A.progress_bar.setStyleSheet('\n            QProgressBar {\n                border: 1px solid #dce4ec;\n                border-radius: 5px;\n                text-align: center;\n                color: #27ae60;\n                background-color: white;\n                font-size: 10px;\n            }\n            QProgressBar::chunk {\n                background-color: #2ecc71;\n                border-radius: 4px;\n            }\n        ');A.status_label.setText(f"Complete: {os.path.basename(output_path)}");A.status_label.setStyleSheet('color: #27ae60; font-weight: bold;');A.set_status_icon(_O);A.flash_animation()
	def mark_error(A,error):A.progress_bar.set_indeterminate(_A);A.progress_bar.setValue(100);A.progress_bar.setStyleSheet('\n            QProgressBar {\n                border: 1px solid #dce4ec;\n                border-radius: 5px;\n                text-align: center;\n                color: #c0392b;\n                background-color: white;\n                font-size: 10px;\n            }\n            QProgressBar::chunk {\n                background-color: #e74c3c;\n                border-radius: 4px;\n            }\n        ');A.status_label.setText(f"Error: {error}");A.status_label.setStyleSheet('color: #e74c3c; font-weight: bold;');A.set_status_icon('error');A.flash_animation()
	def flash_animation(B):C=QGraphicsOpacityEffect(B);B.setGraphicsEffect(C);A=QPropertyAnimation(C,_F);A.setDuration(400);A.setStartValue(.7);A.setEndValue(_C);A.setEasingCurve(QEasingCurve.OutQuad);A.start()
class AppStyles:
	@staticmethod
	def setup_styles(app):A=QFont('Segoe UI',9);app.setFont(A);B='\n        QMainWindow, QWidget {\n            background-color: #f8f9fa;\n        }\n        QLabel {\n            color: #343a40;\n            font-weight: normal;\n        }\n        QLabel#HeaderLabel {\n            font-size: 22px;\n            font-weight: bold;\n            color: #2c3e50;\n            padding: 5px;\n        }\n        QLabel#AppDescription {\n            color: #6c757d;\n            font-size: 13px;\n        }\n        QLineEdit, QTextEdit {\n            border: 1px solid #ced4da;\n            border-radius: 6px;\n            padding: 10px;\n            background-color: white;\n            color: #212529;\n            selection-background-color: #4dabf7;\n        }\n        QLineEdit:focus, QTextEdit:focus {\n            border: 2px solid #4dabf7;\n            outline: none;\n        }\n        QPushButton {\n            background-color: #4dabf7;\n            color: white;\n            border: none;\n            border-radius: 6px;\n            padding: 10px 18px;\n            font-weight: bold;\n            min-height: 20px;\n        }\n        QPushButton:hover {\n            background-color: #339af0;\n        }\n        QPushButton:pressed {\n            background-color: #228be6;\n        }\n        QPushButton:disabled {\n            background-color: #ced4da;\n            color: #868e96;\n        }\n        QPushButton#ConvertButton {\n            background-color: #40c057;\n            font-size: 14px;\n            padding: 12px 24px;\n        }\n        QPushButton#ConvertButton:hover {\n            background-color: #37b24d;\n        }\n        QPushButton#CancelButton {\n            background-color: #fa5252;\n            font-size: 14px;\n            padding: 12px 24px;\n        }\n        QPushButton#CancelButton:hover {\n            background-color: #e03131;\n        }\n        QFrame#SectionFrame {\n            background-color: white;\n            border-radius: 12px;\n            border: 1px solid #e9ecef;\n            padding: 5px;\n        }\n        QLabel#SectionTitle {\n            font-weight: bold;\n            color: #1971c2;\n            font-size: 14px;\n        }\n        QScrollArea {\n            border: none;\n            background-color: transparent;\n        }\n        QListWidget {\n            background-color: white;\n            border: 1px solid #e9ecef;\n            border-radius: 6px;\n            padding: 2px;\n            outline: none;\n        }\n        QListWidget::item {\n            padding: 2px;\n            border-radius: 4px;\n            margin: 2px;\n        }\n        QListWidget::item:selected {\n            background-color: #e7f5ff;\n            color: #1864ab;\n        }\n        QListWidget:focus {\n            border: 1px solid #4dabf7;\n        }\n        ';app.setStyleSheet(B)
	@staticmethod
	def create_section_frame(title,layout=_D):
		E=layout;D=title;A=QFrame();A.setObjectName('SectionFrame');A.setStyleSheet('\n            QFrame#SectionFrame { \n                border: 1px solid #e9ecef; \n                border-radius: 12px; \n                background-color: white;\n            }\n        ');B=QVBoxLayout(A);B.setContentsMargins(15,15,15,15)
		if D:C=QHBoxLayout();F=QLabel(D);F.setObjectName('SectionTitle');C.addWidget(F);C.addStretch();B.addLayout(C)
		if E:B.addLayout(E)
		A.setGraphicsEffect(AppStyles.create_shadow_effect(A));return A
	@staticmethod
	def create_shadow_effect(widget):A=QGraphicsOpacityEffect(widget);return A
class MagnetToTorrentApp(QMainWindow):
	def __init__(A):
		Q='Magnet to Torrent Converter';super().__init__();A.setWindowTitle(Q);A.setMinimumSize(750,550)
		try:
			A.app_icon=IconManager.get_application_icon();A.setWindowIcon(A.app_icon)
			if platform.system()=='Windows':import ctypes as R;S='magnet.to.torrent.converter.1.0';R.windll.shell32.SetCurrentProcessExplicitAppUserModelID(S)
		except Exception as T:print(f"Failed to set icon: {str(T)}");A.app_icon=QIcon()
		M=QWidget();B=QVBoxLayout(M);B.setContentsMargins(20,20,20,20);B.setSpacing(15);C=QFrame();C.setObjectName('HeaderFrame');C.setStyleSheet('\n            QFrame#HeaderFrame {\n                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n                                                stop:0 #f5f7fa, stop:1 #e9ecef);\n                border-radius: 12px;\n            }\n        ');C.setMinimumHeight(70);C.setMaximumHeight(70);E=QHBoxLayout(C);E.setContentsMargins(20,10,20,10);F=40;G=QLabel()
		if not A.app_icon.isNull():U=A.app_icon.pixmap(F,F);G.setPixmap(U)
		G.setFixedSize(F,F);H=QVBoxLayout();N=QLabel(Q);N.setObjectName('HeaderLabel');O=QLabel('Convert multiple magnet links to .torrent files easily');O.setObjectName('AppDescription');H.addWidget(N);H.addWidget(O);E.addWidget(G);E.addLayout(H);E.addStretch();B.addWidget(C);I=QVBoxLayout();V=QLabel('Magnet URLs (separate multiple links with commas):');A.magnet_input=QTextEdit();A.magnet_input.setPlaceholderText("Enter magnet links here (starting with 'magnet:')\nExample: magnet:?xt=urn:btih:..., magnet:?xt=urn:btih:...");A.magnet_input.setAcceptRichText(_A);A.magnet_input.setMinimumHeight(100);I.addWidget(V);I.addWidget(A.magnet_input);W=AppStyles.create_section_frame('MAGNET LINKS',I);B.addWidget(W);J=QVBoxLayout();X=QLabel('Save to directory:');K=QHBoxLayout();A.output_input=QLineEdit();A.output_input.setPlaceholderText('Select where to save the .torrent files');L=QPushButton('Browse');L.clicked.connect(A.browse_output_dir);L.setIcon(A.style().standardIcon(getattr(A.style(),'SP_DirIcon')));K.addWidget(A.output_input);K.addWidget(L);J.addWidget(X);J.addLayout(K);Y=AppStyles.create_section_frame('OUTPUT DIRECTORY',J);B.addWidget(Y);P=QVBoxLayout();A.conversion_list=QListWidget();A.conversion_list.setMinimumHeight(200);A.conversion_list.setSpacing(6);P.addWidget(A.conversion_list);Z=AppStyles.create_section_frame('CONVERSION STATUS',P);B.addWidget(Z);D=QHBoxLayout();D.addStretch();A.convert_button=QPushButton('Convert');A.convert_button.setObjectName('ConvertButton');A.convert_button.clicked.connect(A.start_conversion);A.convert_button.setMinimumWidth(150);A.convert_button.setCursor(Qt.PointingHandCursor);A.cancel_button=QPushButton('Cancel');A.cancel_button.setObjectName('CancelButton');A.cancel_button.clicked.connect(A.cancel_conversion);A.cancel_button.setEnabled(_A);A.cancel_button.setMinimumWidth(150);A.cancel_button.setCursor(Qt.PointingHandCursor);D.addWidget(A.convert_button);D.addSpacing(15);D.addWidget(A.cancel_button);D.addStretch();B.addLayout(D);B.addStretch();A.setCentralWidget(M);A.workers={};A.conversion_items={};A.setup_aria2c()
	def setup_aria2c(A):
		B=ResourceExtractor.get_aria2c_path()
		if not B:QMessageBox.warning(A,'Component Missing','Failed to set up required components. Please check your internet connection.');A.convert_button.setEnabled(_A)
	def browse_output_dir(A):
		B=QFileDialog.getExistingDirectory(A,'Select Output Directory')
		if B:A.output_input.setText(B)
	def add_status_message(A,message):B=QListWidgetItem(message);A.conversion_list.addItem(B);A.conversion_list.scrollToBottom()
	def parse_magnet_links(D):
		B=D.magnet_input.toPlainText().strip()
		if not B:return[]
		E=re.split(',|\\n',B);C=[]
		for A in E:
			A=A.strip()
			if A.startswith('magnet:'):C.append(A)
		return C
	def start_conversion(A):
		G=A.parse_magnet_links();B=A.output_input.text().strip()
		if not G:QMessageBox.warning(A,'No Valid Magnets',"Please enter at least one valid magnet link starting with 'magnet:'");return
		if not B:B=os.path.join(os.path.expanduser('~'),'Downloads');A.output_input.setText(B)
		if not os.path.exists(B):
			try:os.makedirs(B)
			except Exception as I:QMessageBox.critical(A,'Directory Error',f"Could not create output directory: {str(I)}");return
		A.conversion_list.clear();A.cancel_conversion()
		for(J,H)in enumerate(G):D=f"magnet_{J}";F=MagnetConversionItem(D,H);E=QListWidgetItem(A.conversion_list);E.setSizeHint(F.sizeHint());A.conversion_list.addItem(E);A.conversion_list.setItemWidget(E,F);A.conversion_items[D]=E,F;C=ConversionWorker(D,H,B);C.signals.progress.connect(A.update_progress);C.signals.finished.connect(A.conversion_finished);C.signals.error.connect(A.conversion_error);C.start();A.workers[D]=C
		A.cancel_button.setEnabled(_B);A.convert_button.setEnabled(_A)
	def update_progress(A,magnet_id,message,progress):
		B=magnet_id
		if B in A.conversion_items:D,C=A.conversion_items[B];C.update_status(message,progress)
	def conversion_finished(A,magnet_id,output_path):
		B=magnet_id
		if B in A.conversion_items:D,C=A.conversion_items[B];C.mark_complete(output_path)
		if B in A.workers:del A.workers[B]
		A.check_all_finished()
	def conversion_error(A,magnet_id,error):
		B=magnet_id
		if B in A.conversion_items:D,C=A.conversion_items[B];C.mark_error(error)
		if B in A.workers:del A.workers[B]
		A.check_all_finished()
	def check_all_finished(A):
		if not A.workers:A.cancel_button.setEnabled(_A);A.convert_button.setEnabled(_B);A.show_toast_notification('Conversion Complete','All magnet links have been processed.')
	def cancel_conversion(A):
		for(C,B)in list(A.workers.items()):B.stop()
		A.workers.clear();A.cancel_button.setEnabled(_A);A.convert_button.setEnabled(_B)
	def show_toast_notification(C,title,message):A=QFrame(C);A.setFrameShape(QFrame.StyledPanel);A.setStyleSheet('\n            QFrame {\n                background-color: rgba(46, 204, 113, 0.9);\n                border-radius: 8px;\n                color: white;\n            }\n        ');D=QVBoxLayout(A);D.setContentsMargins(15,10,15,10);E=QLabel(title);E.setStyleSheet('font-weight: bold; font-size: 14px; color: white;');F=QLabel(message);F.setStyleSheet('color: white;');D.addWidget(E);D.addWidget(F);G=QApplication.desktop().availableGeometry(C);H=300;I=80;J=20;A.setFixedSize(H,I);L=G.width()-H-J;M=G.height()-I-J;A.move(L,M);A.show();K=QGraphicsOpacityEffect(A);A.setGraphicsEffect(K);B=QPropertyAnimation(K,_F);B.setDuration(500);B.setStartValue(.0);B.setEndValue(_C);B.setEasingCurve(QEasingCurve.OutCubic);B.start();QTimer.singleShot(3000,lambda:C.dismiss_toast(A))
	def dismiss_toast(D,toast):B=toast;C=B.graphicsEffect();A=QPropertyAnimation(C,_F);A.setDuration(500);A.setStartValue(_C);A.setEndValue(.0);A.setEasingCurve(QEasingCurve.OutCubic);A.finished.connect(B.deleteLater);A.start()
	def closeEvent(A,event):A.cancel_conversion();event.accept()
class EnhancedProgressBar(AnimatedProgressBar):
	def __init__(A,parent=_D):super().__init__(parent);A.animation_timer=QTimer(A);A.animation_timer.timeout.connect(A.update_animation);A.animation_offset=0;A.indeterminate=_A;A.ripple_effect=_A;A.ripple_position=0;A.ripple_size=0;A.ripple_opacity=0
	def set_ripple_effect(A,enabled):
		B=enabled;A.ripple_effect=B
		if B:A.ripple_position=A.width()/2;A.ripple_size=10;A.ripple_opacity=_C
		A.update()
	def paintEvent(A,event):
		if not A.indeterminate:
			super().paintEvent(event)
			if A.ripple_effect and A.value()==100:B=QPainter(A);B.setRenderHint(QPainter.Antialiasing);C=QLinearGradient(0,0,A.width(),0);C.setColorAt(0,QColor(255,255,255,0));C.setColorAt(.5,QColor(255,255,255,int(40*A.ripple_opacity)));C.setColorAt(1,QColor(255,255,255,0));B.setBrush(C);B.setPen(Qt.NoPen);B.drawRect(0,0,A.width(),A.height())
			return
		B=QPainter(A);B.setRenderHint(QPainter.Antialiasing);E=QRect(0,0,A.width(),A.height());H=QColor('white');B.fillRect(E,H);B.setPen(QColor(_K));B.drawRoundedRect(0,0,A.width()-1,A.height()-1,5,5);B.setPen(Qt.NoPen);C=QLinearGradient(0,0,A.width(),0);C.setColorAt(0,QColor(52,152,219,255));C.setColorAt(1,QColor(41,128,185,255));D=A.width()/4;B.setBrush(C)
		for F in range(3):
			G=(A.animation_offset*A.width()+F*A.width()/3)%(A.width()+D)-D
			if G<A.width():B.setOpacity(_C-F*.2);B.drawRoundedRect(int(G),2,int(D),A.height()-4,4,4)
		B.setOpacity(_C);B.setPen(QColor(_L));B.drawText(E,Qt.AlignCenter,_M)
	def update_animation(A):
		A.animation_offset=(A.animation_offset+.03)%_C
		if A.ripple_effect:
			A.ripple_size+=2;A.ripple_opacity-=.01
			if A.ripple_opacity<=0:A.ripple_effect=_A
		A.update()
class EnhancedMagnetConversionItem(MagnetConversionItem):
	def __init__(A,magnet_id,magnet_url,parent=_D):super().__init__(magnet_id,magnet_url,parent);A.layout().removeWidget(A.progress_bar);A.progress_bar=EnhancedProgressBar();A.progress_bar.setFixedHeight(16);A.progress_bar.setValue(0);A.layout().children()[1].addWidget(A.progress_bar);A.setMouseTracking(_B);A.hover_animation=QPropertyAnimation(A,b'background_color');A.hover_animation.setDuration(200);A.pulse_timer=QTimer(A);A.pulse_timer.timeout.connect(A.pulse_effect);A.pulse_timer.start(2000);A.pulse_opacity=_C;A.pulse_increasing=_A
	def pulse_effect(A):
		if A.pulse_increasing:
			A.pulse_opacity+=.05
			if A.pulse_opacity>=_C:A.pulse_opacity=_C;A.pulse_increasing=_A
		else:
			A.pulse_opacity-=.05
			if A.pulse_opacity<=.9:A.pulse_opacity=.9;A.pulse_increasing=_B
		B=QGraphicsOpacityEffect(A);B.setOpacity(A.pulse_opacity);A.setGraphicsEffect(B)
	def enterEvent(A,event):A.setStyleSheet('\n            background-color: #f0f4f8;\n            border-radius: 8px;\n        ')
	def leaveEvent(A,event):A.setStyleSheet('\n            background-color: #f8f9fa;\n            border-radius: 8px;\n        ')
	def mark_complete(A,output_path):super().mark_complete(output_path);A.progress_bar.set_ripple_effect(_B);A.pulse_timer.stop();A.setStyleSheet('\n            background-color: #e6f7ef;\n            border-radius: 8px;\n        ')
	def mark_error(A,error):super().mark_error(error);A.pulse_timer.stop();A.setStyleSheet('\n            background-color: #fdecec;\n            border-radius: 8px;\n        ')
def main():A=QApplication(sys.argv);AppStyles.setup_styles(A);B=MagnetToTorrentApp();B.show();sys.exit(A.exec_())
if __name__=='__main__':main()
