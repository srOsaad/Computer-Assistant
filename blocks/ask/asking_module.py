import google.generativeai as genai

class AskingModule:
    def __init__(self):
        genai.configure(api_key="AIzaSyCyRcxLQYPRIaILgkz1I6EBKh_BYeAOaqg")
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    def ask(self, x):
        prompt = """
        Answer concisely.
        - Never give a single word answer.
        - If one sentence is enough, answer in exactly one sentence.
        - If more explanation is needed, use multiples lines but not more than 3.
        """
        response = self.model.generate_content(prompt + "\n\nQ: "+x)
        return response.text

