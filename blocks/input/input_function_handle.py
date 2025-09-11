from blocks.input.primary_input import PrimaryInputModule
from blocks.mouse.voice_control_module import VoiceControlModule
from blocks.auxiliary.auxiliary import word_check, say

class InputFunctionHandle:
    def __init__(self):
        self.pim = PrimaryInputModule()
        self.vcm = VoiceControlModule()

    def input_command(self,x):
        m = word_check(x,['press','click','tap'])
        if m != None:
            if 'double' in x:
                self.pim.click(2)
                return '52'
            elif 'right' in x:
                self.pim.right_click()
                return '52'
            elif 'enter' in x:
                self.pim.press('enter')
                return '52'
            elif 'exit' in x:
                self.pim.press('esc')
                return '52'
    
        if x == 'select all':
            self.pim.select_all()
            return '53'
    
        elif 'copy' in x:
            self.pim.copy_all()
            return '53'

        elif 'cut' in x:
            self.pim.cut_all()
            return '53'
        
        elif 'paste' in x:
            self.pim.paste_all()
            return '53'

        elif 'capslock' in x or ('caps' in x or 'lock' in x):
            self.pim.capslock_toggle()
            return '53'
        
        if x.startswith(('press','click','tap')):
            if x[:3]=='tap':
                if len(x)==3:
                    self.pim.click(1)
                    return '51'
                elif len(x)>4:
                    x = x[4:]
                    pr,p = self.vcm.get_click_per_point(x)
                    print(pr,p)
                    if pr<60:
                        say('Say click or press, if it is where you want me to click')
                        self.pim.moveTo(p)
                        return '51'
                    else:
                        self.pim.clickAt(p) 
                        return '51'  
                return
            if len(x)==5:
                self.pim.click(1)
                return '51'
            if len(x)>6:
                x = x[6:]
                pr,p = self.vcm.get_click_per_point(x)
                print(pr,p)
                if pr<60:
                    say('Say click or press, if it is where you want me to click')
                    print(pr)
                    self.pim.moveTo(p)
                    return '51'
                else:
                    self.pim.clickAt(p)  
                    return '51'