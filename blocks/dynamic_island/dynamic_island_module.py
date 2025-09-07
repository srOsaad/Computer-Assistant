from PySide6.QtGui import QGuiApplication, QImage, QClipboard
from PySide6.QtCore import QBuffer, QIODevice
import winshell
from winshell import shellcon
from datetime import datetime
import base64
import subprocess
from blocks.auxiliary.auxiliary import say

class DynamicIslan:
    def __init__(self):
        pass

    def takeScreenShot(self):
        screen = QGuiApplication.primaryScreen()
        filepath = winshell.get_path(shellcon.CSIDL_MYPICTURES) +'\\Screenshots\\'+datetime.now().strftime("Screenshot_agent_%Y%m%d%H%M%S.jpg")
        if not screen:
            return
        img = screen.grabWindow(0).toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        img.save(buffer, 'jpg')
        img.save(filepath,'jpg')
        data = buffer.data()
        b64 = base64.b64encode(data).decode("utf-8")
        return b64,filepath
    
    def copyImageToClipboard(self, filepath: str):
        image = QImage(filepath)
        if not image.isNull():
            QGuiApplication.clipboard().setImage(image, QClipboard.Clipboard)
            copied = not QGuiApplication.clipboard().image().isNull()           
            return copied
        return False
    
    def revealFile(self, filepath: str):
        try:
            subprocess.run(["explorer", "/select,", filepath])
            return True
        except Exception as e:
            say('An error occured!')
            return False