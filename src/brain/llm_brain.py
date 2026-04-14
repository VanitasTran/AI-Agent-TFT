from loguru import logger
import requests
import json

class LLMBrain:
    def __init__(self, model_name="llama3.2", api_url="http://localhost:11434/v1/chat/completions"):
        self.model_name = model_name
        self.api_url = api_url
        self.rules = self.load_rules()
        logger.info(f"LLMBrain initialized with model: {model_name}")

    def load_rules(self):
        try:
            with open("rule_tft.md", "r", encoding="utf-8") as f:
                return f.read()
        except:
            return "Play TFT best as you can."

    def get_decision(self, game_state_json):
        prompt = self.build_prompt(game_state_json)
        system_prompt = f"You are a TFT Pro. Follow these rules exactly:\n{self.rules}\nOutput ONLY a single JSON object."
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=20)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                logger.debug(f"AI Thought: {content}")
                return self.parse_response(content)
            else:
                logger.error(f"LLM API Error: {response.status_code}")
        except Exception as e:
            logger.error(f"LLM Connection Failed: {e}")
            
        return {"action": "hold", "reason": "API Failure"}

    def build_prompt(self, state):
        return f"""
        STATE: Gold:{state['gold']}, HP:{state['hp']}, Lvl:{state['level']}, Shop:{state['shop']}
        DECIDE NEXT ACTION.
        JSON format: {{"action": "buy|roll|level_up|hold", "target": "unit_name", "reason": "why"}}
        """

    def parse_response(self, content):
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except:
            pass
        return {"action": "hold", "reason": "Parse error"}
