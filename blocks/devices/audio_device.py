import sounddevice as sd

class AudioDevice:
    def __init__(self):
        self.devices = None
        
    def check_all_devices(self):
        self.devices = sd.query_devices()
        self.devices = [d for d in self.devices if d['max_input_channels'] > 0]

    def get_all_devices(self):
        return [d['name'] for d in self.devices if d['max_input_channels'] > 0]
    
    def check_if_available(self,x,index):
        if index<len(self.devices) and self.devices[index]==x:
            return index
        for i in range(len(self.devices)):
            if self.devices[i]['name'] == x:
                return i
        return -1    