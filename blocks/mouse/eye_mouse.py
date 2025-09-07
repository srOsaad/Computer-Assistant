import os
import cv2
import dlib
import numpy as np
import pyautogui
import threading
import time
from collections import deque
from blocks.auxiliary.auxiliary import say

class EyeMouseModule:
    def __init__(self):
        self.running = True
        self.detector = dlib.get_frontal_face_detector()
        self.paused = False
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "shape_predictor_68_face_landmarks.dat")
        self.predictor = dlib.shape_predictor(model_path)
        pyautogui.FAILSAFE = True
        self.sensitivity = 2.0
        self.safe_margin = 1
        self.max_history = 2

        self.screen_width, self.screen_height = pyautogui.size()
        self.xmin = int(self.screen_width * 0.01)
        self.xmax = int(self.screen_width * 0.99)
        self.ymin = int(self.screen_height * 0.01)
        self.ymax = int(self.screen_height * 0.99)

    def run_function(self, x):
        if x == 'terminate':
            self.running = False
            return False
        elif x == 'start':
            if not hasattr(self, 'thread') or not self.thread.is_alive():
                self.running = True
                self.thread = threading.Thread(target=self.start)
                self.thread.start()
            else:
                say("Already running!")
        elif x == 'pause':
            self.paused = True
        elif x == 'resume':
            self.paused = False


    
    def start(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        initial_face_midpoint = None
        position_history = deque(maxlen=self.max_history)

        pyautogui.moveTo(self.screen_width // 2, self.screen_height // 2)
        
        time.sleep(1)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            if self.paused:
                continue
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            for face in faces:
                landmarks = self.predictor(gray, face)

                left_eye_pts = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
                right_eye_pts = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
                nose_tip = (landmarks.part(30).x, landmarks.part(30).y)

                left_eye = np.mean(left_eye_pts, axis=0)
                right_eye = np.mean(right_eye_pts, axis=0)
                face_midpoint = np.mean([left_eye, right_eye, nose_tip], axis=0)

                if initial_face_midpoint is None:
                    initial_face_midpoint = face_midpoint
                    print("Reference face position set.")
                    break

                delta = face_midpoint - initial_face_midpoint
                move_x = int(delta[0] * self.sensitivity)
                move_y = int(delta[1] * self.sensitivity)

                position_history.append((move_x, move_y))
                smooth_x = int(np.mean([p[0] for p in position_history]))
                smooth_y = int(np.mean([p[1] for p in position_history]))

                curr_x, curr_y = pyautogui.position()
                new_x = np.clip(curr_x + smooth_x, self.xmin + self.safe_margin, self.xmax - self.safe_margin)
                new_y = np.clip(curr_y + smooth_y, self.ymin + self.safe_margin, self.ymax - self.safe_margin)
                pyautogui.moveTo(new_x, new_y)
        cap.release()
        cv2.destroyAllWindows()