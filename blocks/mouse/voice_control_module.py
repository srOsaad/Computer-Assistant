import requests
import os
from PIL import ImageGrab
from difflib import SequenceMatcher
from itertools import combinations

def word_match_percentage(said: str, given: str) -> float:
    said_words = said.split()
    given_words = given.split()

    if len(given_words) < len(said_words):
        ratio = SequenceMatcher(None, said, given).ratio()
        return round(ratio * 100, 2)
    
    if len(given_words) == len(said_words):
        ratio = SequenceMatcher(None, said, given).ratio()
        return round(ratio * 100, 2)

    max_ratio = 0.0
    for combo in combinations(given_words, len(said_words)):
        candidate = " ".join(combo)
        ratio = SequenceMatcher(None, said, candidate).ratio()
        max_ratio = max(max_ratio, ratio)

    return round(max_ratio * 100, 2)

def predicted_word_index_per(word:str, result) :
    mx_i = -1
    mx_pre = -1
    i = 0
    for x in result:
        if x==' ' or x=='':
            continue
        x = x['LineText']
        p = word_match_percentage(word,x)
        if p>mx_pre:
            mx_pre = p
            mx_i = i
        i+=1
    return mx_i,mx_pre

def center_point(words):
    first = words[0]
    x1 = first['Left'] + first['Width'] / 2
    y1 = first['Top'] + first['Height'] / 2

    if len(words) > 1:
        last = words[-1]
        x2 = last['Left'] + last['Width'] / 2
        y2 = last['Top'] + last['Height'] / 2
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    else:
        return (x1, y1)

class VoiceControlModule:
    def __init__(self):
        self.api_key = "K83540931188957"
        self.url_api = "https://api.ocr.space/parse/image"
    
    def get_click_per_point(self, x):
        os.makedirs('cache', exist_ok=True)
        file_path = os.path.join('cache', 'click.jpg')  # JPG is smaller than PNG
        image = os.path.abspath(file_path)

        screenshot = ImageGrab.grab()

        screenshot.save(image, "JPEG", quality=95, optimize=True)

        max_size = 1024 * 1024 
        file_size = os.path.getsize(image)

        if file_size > max_size:
            ratio = max_size / file_size
            est_quality = int(95 * ratio)

            est_quality = max(20, min(est_quality, 95))

            screenshot.save(image, "JPEG", quality=est_quality, optimize=True)

            while os.path.getsize(image) > max_size and est_quality > 20:
                est_quality -= 5
                screenshot.save(image, "JPEG", quality=est_quality, optimize=True)

        percentage, coords = 0, (0, 0)

        with open(image, 'rb') as f:
            response = requests.post(
                self.url_api,
                files={image: f},
                data={'apikey': self.api_key, 'language': 'eng', 'isOverlayRequired': True}
            )
            result = response.json()

            if result['IsErroredOnProcessing']:
                print('error', result['ErrorMessage'])
            else:
                result = result['ParsedResults'][0]['TextOverlay']['Lines']
                predicted_index, percentage = predicted_word_index_per(x, result)
                p = center_point(result[predicted_index]['Words'])
                coords = (float(p[0]), float(p[1]))

        return percentage, coords
