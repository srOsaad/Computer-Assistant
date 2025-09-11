import os
import google.generativeai as genai

class AskingModule:
    def __init__(self):
        genai.configure(api_key=os.environ["GENAI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    def ask(self, x):
        prompt = """
        Answer concisely.
        - Never give a single word answer.
        - If one sentence is enough, answer in exactly one sentence.
        - If more explanation is needed, use multiples lines but not more than 3.
        """
        response = self.model.generate_content(prompt + "\n\nQ: "+x)
        print(response.text)
        return response.text

