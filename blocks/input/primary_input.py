import pyautogui

class PrimaryInputModule:
    def __init__(self):
        pass
    
    def type(self,x):
        pyautogui.typewrite(x,interval=0.05)
    
    def moveTo(self,point):
        pyautogui.moveTo(point[0],point[1],0.5)
    
    def clickAt(self,point):
        pyautogui.doubleClick(point[0],point[1])
    
    def click(self,x=1):
        if x==1:
            pyautogui.leftClick()
        elif x==2:
            pyautogui.doubleClick()
    
    def right_click(self):
        pyautogui.rightClick()
    
    def press(self,x):
        if x=='enter':
            pyautogui.press('enter')
        elif x=='exit':
            pyautogui.press('esc')
    
    def select_all(self):
        pyautogui.hotkey('ctrl','a')

    def copy_all(self):
        pyautogui.hotkey('ctrl','c')
    
    def cut_all(self):
        pyautogui.hotkey('ctrl','x')
    
    def paste_all(self):
        pyautogui.hotkey('ctrl','v')
    
    def delete_all(self):
        pyautogui.press('del')
    
    def capslock_toggle(self):
        pyautogui.press('capslock')