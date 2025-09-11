import requests
import os
from PIL import Image, ImageGrab, ImageOps
from difflib import SequenceMatcher
from itertools import combinations
import re

def clean_text(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9:]', '', s).lower()

def word_match_percentage(said: str, given: str) -> float:
    said_clean = clean_text(said)
    given_clean = clean_text(given)

    said_words = said_clean.split()
    given_words = given_clean.split()

    if len(given_words) < len(said_words) or len(given_words) == len(said_words):
        ratio = SequenceMatcher(None, said_clean, given_clean).ratio()
        return round(ratio * 100, 2)

    max_ratio = 0.0
    for combo in combinations(given_words, len(said_words)):
        candidate = " ".join(combo)
        ratio = SequenceMatcher(None, said_clean, candidate).ratio()
        max_ratio = max(max_ratio, ratio)

    return round(max_ratio * 100, 2)

def predicted_word_index_per(word: str, result):
    mx_i = -1
    mx_pre = -1
    for line_index, line in enumerate(result):
        words = line['Words']
        for i in range(len(words)):
            for j in range(i+1, len(words)+1):
                candidate = ' '.join([w['WordText'] for w in words[i:j]])
                p = word_match_percentage(word.lower(), candidate.lower())
                if p > mx_pre:
                    mx_pre = p
                    mx_i = line_index
    return mx_i, mx_pre

def center_point(words,xx):
    wp = 0
    x, y = 0.0 , 0.0
    print(words)
    for word in words:
        print(word['WordText'], x)
        twp = word_match_percentage(word['WordText'].lower(), xx)
        if twp>wp:
            wp=twp
            x = word['Left']+word['Width']/2
            y = word['Top']+word['Height']/2
            if wp==100:
                break
    return (x, y)

class VoiceControlModule:
    def __init__(self):
        self.api_key = os.environ["SPACE_OCR_API_KEY"]
        self.url_api = "https://api.ocr.space/parse/image"

    def get_click_per_point(self, target_word: str):
        sv_w = target_word.lower()
        os.makedirs('cache', exist_ok=True)
        file_path = os.path.join('cache', 'click.jpg')
        image = os.path.abspath(file_path)

        img = ImageGrab.grab()
        img.save(image, "JPEG", quality=100, optimize=True)

        max_size = 1024 * 1024
        est_quality = 95
        while os.path.getsize(image) > max_size and est_quality > 20:
            est_quality -= 5
            img.save(image, "JPEG", quality=est_quality, optimize=True)

        percentage, coords = 0, (0, 0)

        with open(image, 'rb') as f:
            response = requests.post(
                self.url_api,
                files={image: f},
                data={'apikey': self.api_key, 'language': 'eng', 'isOverlayRequired': True}
            )
            result = response.json()

        if result['IsErroredOnProcessing']:
            print('OCR Error:', result['ErrorMessage'])
        else:
            lines = result['ParsedResults'][0]['TextOverlay']['Lines']
            #print("OCR Lines:", lines)
            predicted_index, percentage = predicted_word_index_per(target_word, lines)
            if predicted_index != -1:
                print(lines[predicted_index]['Words'])
                print(sv_w)
                p = center_point(lines[predicted_index]['Words'],sv_w)
                coords = (float(p[0]), float(p[1]))
                print(coords)

        return percentage, coords
