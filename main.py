import sys
import subprocess
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, QBuffer, QIODevice
#from blocks.voice.voice import VoiceThread
from PySide6.QtGui import QGuiApplication, QClipboard, QImage
from datetime import datetime
from blocks.devices.audio_device import AudioDevice
from blocks.devices.camera_device import CameraDevice
from blocks.workflow.workflow import Backend
from blocks.voice.voice import VoiceThread

class Bridge(QObject):
    screenshotData = Signal(str,str)
    alarmData = Signal(str)
    showApp = Signal(bool)
    listening = Signal()
    thinking = Signal()
    gotResult = Signal(bool)
    micOn = Signal(bool)
    cameraOn = Signal(bool) 
    availableDevices = Signal(list,int,list,int)

    def __init__(self):
        super().__init__()
        self.audio_device_manager = AudioDevice()
        self.camera_device_manage = CameraDevice()

        self.audio_device_manager.check_all_devices()
        self.camera_device_manage.check_all_devices()

        self.audio_devices = self.audio_device_manager.get_all_devices()
        self.camera_devices = self.camera_device_manage.get_all_devices()
        self.selected_audio_device = 0 if len(self.audio_devices)>0 else -1
        self.selected_camera_device = 0 if len(self.camera_devices)>0 else -1
        self.backend = Backend()
        self.backend.ok.connect(self.executedSuccessfully)
        self.backend.screenshotData.connect(self.screenshotData)
        #self.voice_thread = VoiceThread()
        #self.voice_thread.recognized
        self.voice_thread = VoiceThread()
        self.voice_thread.recognized.connect(self.newCommand)
        self.voice_thread.listening_started.connect(self.listening)
        self.voice_thread.listening_stopped.connect(self.thinking)

    def executedSuccessfully(self, x: bool):
        self.gotResult.emit(x)


    @Slot(str, result=bool)
    def copyImageToClipboard(self, filepath: str) -> bool:
        print('copy click')
        return self.backend.handle('#d copy '+filepath)
    
    @Slot(str)
    def revealFile(self, filepath: str):
        self.backend.handle('#d reveal '+filepath)
        print('dead')

    @Slot() 
    def takeScreenshotAndSend(self):
        print('dead')
        
    @Slot() 
    def kk(self):
        current_time = datetime.now().strftime("%I:%M%p")
        self.alarmData.emit(current_time)

    @Slot(bool)
    def showapp(self,showda: bool):
        print(showda)
        self.showApp.emit(showda)

    @Slot(bool)
    def on(self, on):
        if on :
            self.voice_thread.start()
            self.isResult(5)
        else:
            self.voice_thread.stop()
            self.isResult(5)

    @Slot()
    def request_for_devices(self):
        previous_audio_device_name = -1 if self.selected_audio_device==-1 else self.audio_devices[self.selected_audio_device]
        self.audio_device_manager = AudioDevice()

        previous_camera_device_name = -1 if self.selected_camera_device==-1 else self.camera_devices[self.selected_camera_device]
        self.camera_device_manage = CameraDevice()

        self.audio_device_manager.check_all_devices()
        self.camera_device_manage.check_all_devices()

        self.audio_devices = self.audio_device_manager.get_all_devices()
        self.camera_devices = self.camera_device_manage.get_all_devices()

        p = self.audio_device_manager.check_if_available(previous_audio_device_name,self.selected_audio_device)
        if self.selected_audio_device!=-1 and p!=1:
            self.selected_audio_device =  p
        else:
            self.selected_audio_device = 0 if len(self.audio_devices)>0 else -1

        p = self.audio_device_manager.check_if_available(previous_camera_device_name,self.selected_camera_device)
        if self.selected_camera_device!=-1 and p!=1:
            self.selected_camera_device =  p
        else:
            self.selected_camera_device = 0 if len(self.camera_devices)>0 else -1
        print(self.audio_devices,self.selected_audio_device,self.camera_devices,self.selected_camera_device)
        self.availableDevices.emit(self.audio_devices,self.selected_audio_device,self.camera_devices,self.selected_camera_device)

    @Slot(int,int)
    def selected_devices(self, audio_device_index, camera_device_index):
        print(audio_device_index,camera_device_index)
        self.selected_audio_device = audio_device_index
        self.selected_camera_device = camera_device_index

    @Slot(str)
    def newCommand(self,command):
        print(command)
        output = self.backend.handle(command)
        if output == None:
            self.backend.ok.emit(False)
            return
        if output[0] == '0':
            if output[1] == '1':
                self.showApp.emit(True)
            elif output[1] == '0':
                self.showApp.emit(False)
        elif output[0] == 'd':
            if output[1] == '1':
                self.takeScreenshotAndSend()

    @Slot(int)
    def isResult(self,x):
        if x==1:
            self.listening.emit()
        elif x==2:
            self.thinking.emit()
        elif x==3:
            self.gotResult.emit(True)
        else:
            self.gotResult.emit(False)
    
bridge = Bridge()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('bridge',bridge)
    engine.load('ui.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())