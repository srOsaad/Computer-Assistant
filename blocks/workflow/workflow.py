from blocks.ask.asking_module import AskingModule
from blocks.input.primary_input import PrimaryInputModule
from blocks.mouse.eye_mouse import EyeMouseModule
from blocks.dynamic_island.dynamic_island_module import DynamicIslan
from blocks.auxiliary.auxiliary import say, word_check, webopen, appopen, openSettings, current_time, google_search
from PySide6.QtCore import QObject, Signal
from blocks.input.input_function_handle import InputFunctionHandle

class Backend(QObject):
    ok = Signal(bool)
    screenshotData = Signal(str,str)
    def __init__(self):
        super().__init__()
        self.input_handler = PrimaryInputModule()
        self.inputfunction_handler = InputFunctionHandle()
        self.eyemouse_handler = EyeMouseModule()
        self.dynamicisland_handler = DynamicIslan()
        self.qna_handler = AskingModule()
        self.modes = []

    def handle(self,y):
        x = y.strip().lower()
        if x.endswith("."):
            x = x[:-1]
        if x.startswith(('turn off','stop','shutdown')):
            if 'mode' in x:
                if 'typing' in x and 't' in self.modes:
                    self.ok.emit(True)
                    self.modes.remove('t')
                    say('Typing mode turned off.')
                    return '1t'
                elif ('eye' in x or 'i' in x) and 'e' in self.modes:
                    self.ok.emit(True)
                    self.eyemouse_handler.run_function('terminate')
                    self.modes.remove('e')
                    say('Eye control mode turned off.')
                    return '1e'
        if 't' in self.modes:
            self.ok.emit(True)
            self.input_handler.type(x)
            return '1T'
        
        if 'e' in self.modes:
            if x == 'pause':
                self.ok.emit(True)
                self.eyemouse_handler.run_function('pause')
                return '1E'
            if x == 'resume':
                self.ok.emit(True)
                self.eyemouse_handler.run_function('resume')
                return '1E'
        
        if x.startswith(('turn on','start')):
            if 'mode' in x:
                if 'typing' in x and 't' not in self.modes:
                    self.ok.emit(True)
                    self.modes.append('t')
                    say('Typing mode turn on.')
                    return '1T'
                elif ('eye' in x or 'i' in x) and 'e' not in self.modes:
                    self.ok.emit(True)
                    self.eyemouse_handler.run_function('start')
                    self.modes.append('e')
                    say('Eye control mode turn on.')
                    return '1E'
                return
            
        if x.startswith('type'):
            if len(x)>5:
                self.ok.emit(True)
                self.input_handler.type(x[5:])
                return '1T'
            return
        
        if 'time' in x and not 'in' in x:
            self.ok.emit(True)
            say(f"It's {current_time()} now.")
            return 'd2'
        
        if x.startswith('search'):
            if len(x)>7:
                self.ok.emit(True)
                x = x[7:]
                google_search(x)
                return '30'
            return
        
        if x.startswith('tell me'):
            if len(x)>8:
                x = x[8:]
                ans = self.qna_handler.ask(x)
                say(ans)
                self.ok.emit(True)
                return '62'
            return
        
        if x.startswith(('start','show','open')):
            m = word_check(x,['facebook','youtube','instagram'])
            if m != None:
                self.ok.emit(True)
                webopen(m)
                return '21'
            m = word_check(x,['chrome','notebook'])
            if m != None:
                self.ok.emit(True)
                appopen(True)
                return '22'
            if 'setting' in x:
                self.ok.emit(True)
                openSettings()
                return '23'

        if x == 'show yourself':
            self.ok.emit(True)
            return '01'
        if x == 'hide yourself':
            self.ok.emit(True)
            return '00'
        
        if self.inputfunction_handler.input_command(x) != None:
            self.ok.emit(True)
            return '55'
        
        if 'screenshot' in x and ('take' in x or 'click' in x):
            self.ok.emit(True)
            ss_data, filepath = self.dynamicisland_handler.takeScreenShot()
            self.screenshotData.emit(ss_data,filepath)
            return 'd1'

        if y.startswith('#d cpy_'):
            print('123')
            y = y[8:]
            print(y)
            result = self.dynamicisland_handler.copyImageToClipboard(y)
            if result:
                self.ok.emit(True)
                return 'd1'
        
        if y.startswith('#d reveal'):
            y = y[10:]
            r = self.dynamicisland_handler.revealFile(y)
            self.ok.emit(r)
            return 'd1'