import win32com.client

class CameraDevice:
    def __init__(self):
        self.devices = []

    def check_all_devices(self):
        self.devices = []
        wmi = win32com.client.GetObject("winmgmts:")
        cameras = wmi.ExecQuery("SELECT * FROM Win32_PnPEntity WHERE Description LIKE '%Camera%'")
        for idx, cam in enumerate(cameras):
            self.devices.append({'index': idx, 'name': cam.Name})

    def get_all_devices(self):
        return [f"{d['name']}" for d in self.devices]

    def check_if_available(self, x, index):
        if index<len(self.devices) and self.devices[index]==x:
            return index
        for i in range(len(self.devices)):
            if self.devices[i]['name'] == x:
                return i
        return -1  