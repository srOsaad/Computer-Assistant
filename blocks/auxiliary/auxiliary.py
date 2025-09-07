import webbrowser
import subprocess
import datetime
import os
import win32com.client


speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Rate = 1.5
speaker.Volume = 60
speaker.Voice = speaker.GetVoices()[1]

def say(x):
    speaker.Speak(x)

def openSettings():
    subprocess.run(["start", "ms-settings:"], shell=True)

def appopen(self,x):
    os.system(x)
    
def webopen(x):
    webbrowser.open(f"https://www.{x}.com")

def word_check(x,wordlist):
    match = next((word for word in wordlist if word in x.lower()), None)
    if match:
        return match
    return None

def current_time():
        am = True
        h = int(datetime.datetime.now().strftime('%H'))
        m = datetime.datetime.now().strftime('%M')
        if h>12:
            am=False
            h-=12
        return str(h)+':'+m+' '+('am' if am else 'pm')

def google_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)

