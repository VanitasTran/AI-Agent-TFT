from loguru import logger
import requests
import json

class LLMBrain:
    def __init__(self, model_name="llama3.2", api_url="http://localhost:11434/v1/chat/completions"):
        self.model_name = model_name
        self.api_url = api_url
        self.rules = self.load_rules()
        self.tools = self.define_tools()
        logger.info(f"LLMBrain initialized with model: {model_name} in Tool-Calling mode.")

    def load_rules(self):
        try:
            with open("rule_tft.md", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return "Play TFT best as you can."

    def define_tools(self):
        return [
            {
                "name": "buy_shop_unit",
                "description": "Mua một vị tướng từ cửa hàng tại ô chỉ định (1-5) để nâng cấp hoặc kích hệ tộc.",
                "parameters": {
                    "slot_index": "int (từ 0 đến 4 tương ứng với ô 1 đến 5 từ trái sang phải)"
                }
            },
            {
                "name": "roll_shop",
                "description": "Làm mới (Roll) cửa hàng để tìm tướng mới (tốn 2 vàng). Chỉ nên sử dụng khi cần roll gấp để nâng sao hoặc kích hệ.",
                "parameters": {}
            },
            {
                "name": "level_up",
                "description": "Mua kinh nghiệm (XP) để tăng cấp độ người chơi (tốn 4 vàng). Giúp tăng slot cờ trên sân và tăng tỷ lệ ra tướng xịn.",
                "parameters": {}
            },
            {
                "name": "sell_bench_unit",
                "description": "Bán một vị tướng đang ở trên hàng chờ (bench) từ ô 1 đến 9 để giải phóng chỗ trống hoặc lấy lại vàng.",
                "parameters": {
                    "bench_slot": "int (từ 0 đến 8 tương ứng với ô hàng chờ 1 đến 9)"
                }
            },
            {
                "name": "deploy_bench_to_board",
                "description": "Kéo thả một vị tướng từ hàng chờ lên bàn cờ để thi đấu.",
                "parameters": {
                    "bench_slot": "int (0-8, vị trí trên hàng chờ)",
                    "board_x": "int (0-6, tọa độ cột trên bàn cờ từ trái sang)",
                    "board_y": "int (0-3, tọa độ hàng trên bàn cờ từ trên xuống, hàng 0 gần đối thủ nhất, hàng 3 gần hàng chờ nhất)"
                }
            },
            {
                "name": "reposition_board_units",
                "description": "Di chuyển hoặc hoán đổi vị trí của 2 tướng trên bàn cờ để tối ưu đội hình (Tanker hàng trước, Carry hàng sau).",
                "parameters": {
                    "from_x": "int (0-6, cột gốc)",
                    "from_y": "int (0-3, hàng gốc)",
                    "to_x": "int (0-6, cột đích)",
                    "to_y": "int (0-3, hàng đích)"
                }
            },
            {
                "name": "select_god_blessing",
                "description": "Bấm chọn 1 trong 3 chúc phúc của Thần (hoặc Pengu) xuất hiện tại các vòng Realm of the Gods (Stage 2-4, 3-4, 4-4).",
                "parameters": {
                    "choice_index": "int (từ 0 đến 2 tương ứng với Lựa chọn 1, 2, 3 từ trái qua phải)"
                }
            },
            {
                "name": "select_augment",
                "description": "Bấm chọn 1 trong 3 Lõi Nâng Cấp Nâng (Augments) tại Stage 2-1, 3-2, 4-2.",
                "parameters": {
                    "augment_index": "int (từ 0 đến 2 tương ứng với Lõi 1, 2, 3 từ trái qua phải)"
                }
            },
            {
                "name": "equip_item_to_unit",
                "description": "Kéo thả trang bị từ hàng trang bị dự bị vào tướng chỉ định đang đứng trên bàn cờ.",
                "parameters": {
                    "item_index": "int (từ 0 đến 9 tương ứng với 10 ô chứa trang bị)",
                    "board_x": "int (0-6, vị trí cột trên bàn cờ của tướng cần lắp đồ)",
                    "board_y": "int (0-3, vị trí hàng trên bàn cờ của tướng cần lắp đồ)"
                }
            },
            {
                "name": "hold_gold",
                "description": "Giữ nguyên trạng thái để tích lũy lợi tức (Econ) hoặc tiết kiệm vàng lên cấp.",
                "parameters": {
                    "reason": "string (giải thích chiến thuật tại sao lại giữ tiền)"
                }
            }
        ]

    def get_decision(self, game_state_json):
        prompt = self.build_prompt(game_state_json)
        system_prompt = f"""
You are a TFT Challenger Coach and Bot Commander. You operate by choosing the exact 'Tool' to run.
Here is your instruction set:
{self.rules}

Here are the tools available in your toolkit:
{json.dumps(self.tools, ensure_ascii=False, indent=2)}

You MUST analyze the current state and select exactly ONE tool from the list above.
You MUST output ONLY a valid JSON object in this format:
{{
  "tool": "name_of_the_tool",
  "arguments": {{
    "parameter_name": value
  }},
  "reason": "strategic explanation in Vietnamese"
}}
        """
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
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
            
        return {"tool": "hold_gold", "arguments": {"reason": "API Failure"}, "reason": "Lỗi kết nối bộ não AI."}

    def build_prompt(self, state):
        return f"""
=== TRẠNG THÁI TRẬN ĐẤU THỜI GIAN THỰC ===
Vàng hiện có (Gold): {state['gold']}
Máu người chơi (HP): {state['hp']}
Cấp độ (Level): {state['level']}
Tướng trong Cửa hàng (Shop Slots 1-5): {state['shop']}

Quyết định xem nên sử dụng TOOL nào tiếp theo để tối ưu hóa ván đấu.
Hãy trả về JSON tương ứng với định dạng yêu cầu.
        """

    def parse_response(self, content):
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except Exception as e:
            logger.error(f"Parse response failure: {e}")
        return {"tool": "hold_gold", "arguments": {"reason": "Parse error"}, "reason": "Lỗi phân tích cú pháp kết quả."}

