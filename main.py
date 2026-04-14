import time
import os
import sys
import cv2
import yaml
from loguru import logger

# Import các module từ src/
from src.vision.adb_control import ADBController
from src.vision.ocr_reader import OCRReader
from src.vision.unit_detector import UnitDetector
from src.brain.llm_brain import LLMBrain
from src.executor.action_executor import ActionExecutor

class TFTAgent:
    def __init__(self):
        logger.info("Khởi tạo TFT AI Agent v2 (Self-Decision)...")
        self.adb = ADBController()
        self.load_configs()
        
        self.ocr = OCRReader()
        self.detector = UnitDetector()
        self.brain = LLMBrain(model_name="llama3.2") # Đổi sang llama3.2 nhẹ và nhanh
        self.executor = ActionExecutor(self.adb, self.config)
        
        self.screen_file = "checkpoints/current_screen.png"
        self.roll_count = 0  
        self.last_roll_reset = time.time()
        
        if not self.adb.check_device():
            logger.error("Không tìm thấy thiết bị ADB!")
            sys.exit(1)

    def load_configs(self):
        config_path = "configs/regions.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            logger.error("Missing regions.yaml!")
            sys.exit(1)

    def run_step(self):
        """ Một vòng lặp tự động hoàn toàn """
        # Reset Roll sau 30s
        if time.time() - self.last_roll_reset > 30:
            self.roll_count = 0
            self.last_roll_reset = time.time()

        if not self.adb.capture_screen(self.screen_file):
            return

        screen_img = cv2.imread(self.screen_file)
        if screen_img is None: return

        # 1. Thu thập dữ liệu trạng thái (State)
        state = self.collect_game_state(screen_img)
        logger.info(f"📊 State: Gold: {state['gold']} | HP: {state['hp']} | Lvl: {state['level']} | Shop: {state['shop']}")

        # 2. Hỏi bộ não Gemma xem nên làm gì
        decision = self.brain.get_decision(state)
        logger.warning(f"🧠 Gemma Decision: {decision.get('action').upper()} | Lý do: {decision.get('reason')}")

        # 3. Thực thi hành động
        self.execute_decision(decision, state)

    def collect_game_state(self, img):
        """ Trích xuất mọi thông tin từ màn hình """
        state = {
            "gold": self.ocr.extract_value(img, self.config['regions']['gold']) or 0,
            "hp": self.ocr.extract_value(img, self.config['regions']['hp_sidebar_region']) or 100, # Tạm để 100 nếu k đọc đc
            "level": self.ocr.extract_value(img, self.config['regions']['level_region']) or 1,
            "shop": self.scan_shop(img)
        }
        return state

    def execute_decision(self, decision, state):
        """ Chuyển quyết định của LLM thành hành động cụ thể """
        action = decision.get("action", "").lower()
        target = decision.get("target", "")

        if action == "buy":
            # Nếu Gemma bảo mua tướng cụ thể, tìm xem nó ở ô nào trong shop
            for i, name in enumerate(state['shop']):
                if name.lower() == target.lower() and name != "Unknown":
                    self.executor.buy_unit(i)
                    return
        
        elif action == "roll":
            if state['gold'] >= 2:
                self.executor.roll()
                self.roll_count += 1
                
        elif action == "level_up":
            if state['gold'] >= 4:
                self.executor.level_up()
        
        elif action == "hold":
            logger.debug("AI quyết định giữ tiền (Hold).")

    def scan_shop(self, screen_img):
        units_found = []
        shop_regions = self.config['regions']['shop_slots']
        for i, reg in enumerate(shop_regions):
            x, y, w, h = reg
            slot_img = screen_img[y:y+h, x:x+w]
            matches = self.detector.detect_units(slot_img, threshold=0.7)
            units_found.append(matches[0]['name'] if matches else "Unknown")
        return units_found

    def start(self):
        logger.info("🤖 AI Agent đã ONLINE và tự vận hành...")
        try:
            while True:
                self.run_step()
                time.sleep(3) # Đợi 3s mỗi lượt để game cập nhật
        except KeyboardInterrupt:
            logger.info("Dừng Agent.")

if __name__ == "__main__":
    agent = TFTAgent()
    agent.start()
