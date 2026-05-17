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
        self.prev_state = {"gold": -1, "hp": -1, "level": -1, "shop": []}
        
        if not self.adb.check_device():
            logger.error("Không tìm thấy thiết bị ADB!")
            sys.exit(1)


    def load_configs(self):
        config_path = "configs/regions.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Tự động co giãn tọa độ theo độ phân giải màn hình thực tế của thiết bị
            device_res = self.adb.get_screen_resolution()
            design_res = self.config.get('screen_resolution', [2400, 1080])
            
            if device_res:
                logger.info(f"📱 Độ phân giải màn hình thiết bị: {device_res[0]}x{device_res[1]} (Thiết kế mẫu: {design_res[0]}x{design_res[1]})")
                if device_res != design_res:
                    self.scale_regions(device_res, design_res)
            else:
                logger.warning(f"⚠️ Không đọc được độ phân giải từ ADB, sử dụng tọa độ thiết kế gốc: {design_res[0]}x{design_res[1]}")
        else:
            logger.error("Missing regions.yaml!")
            sys.exit(1)

    def scale_regions(self, device_res, design_res):
        """Tự động co giãn các tọa độ [x, y, w, h] theo tỷ lệ màn hình của thiết bị"""
        scale_x = device_res[0] / design_res[0]
        scale_y = device_res[1] / design_res[1]
        
        logger.warning(f"📐 Tỷ lệ co giãn tọa độ màn hình: X: {scale_x:.4f} | Y: {scale_y:.4f}")
        
        regions = self.config['regions']
        
        # 1. Co giãn các vùng đơn lẻ [x, y, w, h] hoặc [x, y]
        single_keys = ['gold', 'btn_roll', 'btn_xp', 'level_region', 'xp_region', 'hp_sidebar_region', 'sell_zone_left', 'sell_zone_right']
        for key in single_keys:
            if key in regions:
                regions[key] = self._scale_box(regions[key], scale_x, scale_y)
                
        # 2. Co giãn danh sách các ô (shop_slots, bench_slots, god_blessing_slots, augment_slots, item_slots)
        list_keys = ['shop_slots', 'bench_slots', 'god_blessing_slots', 'augment_slots', 'item_slots']
        for key in list_keys:
            if key in regions:
                regions[key] = [self._scale_box(box, scale_x, scale_y) for box in regions[key]]
                
        # 3. Co giãn tọa độ lưới bàn cờ board_grid
        if 'board_grid' in regions:
            bg = regions['board_grid']
            bg['start_x'] = int(bg['start_x'] * scale_x)
            bg['start_y'] = int(bg['start_y'] * scale_y)
            bg['dx'] = int(bg['dx'] * scale_x)
            bg['dy'] = int(bg['dy'] * scale_y)
            if 'row_offsets' in bg:
                bg['row_offsets'] = [int(offset * scale_x) for offset in bg['row_offsets']]

    def _scale_box(self, box, scale_x, scale_y):
        if len(box) == 4:
            return [int(box[0] * scale_x), int(box[1] * scale_y), int(box[2] * scale_x), int(box[3] * scale_y)]
        elif len(box) == 2:
            return [int(box[0] * scale_x), int(box[1] * scale_y)]
        return box


    def run_step(self):
        """ Một vòng lặp tự động hoàn toàn """
        # Reset Roll sau 30s
        if time.time() - self.last_roll_reset > 30:
            self.roll_count = 0
            self.last_roll_reset = time.time()

        # Chụp màn hình siêu tốc trực tiếp vào bộ nhớ RAM (Sub-120ms!)
        screen_img = self.adb.capture_screen_fast()
        
        # Dự phòng (Fallback) nếu chụp siêu tốc lỗi thì chạy adb pull chậm
        if screen_img is None:
            logger.warning("⚠️ Chụp nhanh thất bại, chuyển sang phương pháp adb pull dự phòng...")
            if not self.adb.capture_screen(self.screen_file):
                return
            screen_img = cv2.imread(self.screen_file)
            if screen_img is None: return

        # 1. Thu thập dữ liệu trạng thái (State)
        state = self.collect_game_state(screen_img)
        
        # So khớp và phát hiện thay đổi trạng thái (Change Detection)
        state_changed = (
            state['gold'] != self.prev_state.get('gold') or
            state['level'] != self.prev_state.get('level') or
            state['hp'] != self.prev_state.get('hp') or
            state['shop'] != self.prev_state.get('shop')
        )
        
        if not state_changed:
            # Nhịp thở siêu tốc (Fast Path): Bỏ qua LLM nếu trạng thái game tĩnh lặng (đang trong round đấu)
            logger.debug("⏳ Trạng thái game đứng im (Combat/Waiting) -> Tạm ngừng gọi LLM để tiết kiệm pin/CPU.")
            return

        logger.info(f"📊 State Cập Nhật: Gold: {state['gold']} | HP: {state['hp']} | Lvl: {state['level']} | Shop: {state['shop']}")
        self.prev_state = state

        # 2. Hỏi bộ não AI xem nên chọn Tool nào (Chỉ kích hoạt khi có thay đổi thực tế)
        decision = self.brain.get_decision(state)

        # 3. Thực thi Tool hành động
        self.execute_tool(decision)


    def collect_game_state(self, img):
        """ Trích xuất mọi thông tin từ màn hình """
        state = {
            "gold": self.ocr.extract_value(img, self.config['regions']['gold']) or 0,
            "hp": self.ocr.extract_value(img, self.config['regions']['hp_sidebar_region']) or 100, # Tạm để 100 nếu k đọc đc
            "level": self.ocr.extract_value(img, self.config['regions']['level_region']) or 1,
            "shop": self.scan_shop(img)
        }
        return state

    def execute_tool(self, decision):
        """ Thực thi công cụ chuyên dụng do LLM Brain lựa chọn """
        tool_name = decision.get("tool", "").lower()
        args = decision.get("arguments", {})
        reason = decision.get("reason", "")
        
        logger.warning(f"🤖 [TOOL SELECTION] -> Tool: {tool_name.upper()} | Lý do: {reason}")
        
        if tool_name == "buy_shop_unit":
            slot = args.get("slot_index")
            if slot is not None and 0 <= slot <= 4:
                self.executor.buy_unit(slot)
            else:
                logger.error(f"Slot mua tướng không hợp lệ: {slot}")
                
        elif tool_name == "roll_shop":
            self.executor.roll()
            self.roll_count += 1
            
        elif tool_name == "level_up":
            self.executor.level_up()
            
        elif tool_name == "sell_bench_unit":
            slot = args.get("bench_slot")
            if slot is not None and 0 <= slot <= 8:
                self.executor.sell_bench_unit(slot)
            else:
                logger.error(f"Slot hàng chờ để bán không hợp lệ: {slot}")
                
        elif tool_name == "deploy_bench_to_board":
            slot = args.get("bench_slot")
            bx = args.get("board_x")
            by = args.get("board_y")
            if slot is not None and bx is not None and by is not None:
                self.executor.deploy_bench_to_board(slot, bx, by)
            else:
                logger.error(f"Thiếu tham số kéo tướng từ hàng chờ: slot={slot}, x={bx}, y={by}")
                
        elif tool_name == "reposition_board_units":
            fx = args.get("from_x")
            fy = args.get("from_y")
            tx = args.get("to_x")
            ty = args.get("to_y")
            if fx is not None and fy is not None and tx is not None and ty is not None:
                self.executor.reposition_board_units(fx, fy, tx, ty)
            else:
                logger.error(f"Thiếu tham số hoán đổi tướng trên bàn cờ: from=({fx}, {fy}), to=({tx}, {ty})")

        elif tool_name == "select_god_blessing":
            choice = args.get("choice_index")
            if choice is not None and 0 <= choice <= 2:
                self.executor.select_god_blessing(choice)
            else:
                logger.error(f"Lựa chọn chúc phúc của Thần không hợp lệ: {choice}")

        elif tool_name == "select_augment":
            idx = args.get("augment_index")
            if idx is not None and 0 <= idx <= 2:
                self.executor.select_augment(idx)
            else:
                logger.error(f"Lựa chọn lõi công nghệ không hợp lệ: {idx}")

        elif tool_name == "equip_item_to_unit":
            item = args.get("item_index")
            bx = args.get("board_x")
            by = args.get("board_y")
            if item is not None and bx is not None and by is not None:
                self.executor.equip_item_to_unit(item, bx, by)
            else:
                logger.error(f"Thiếu tham số kéo trang bị: item={item}, board_x={bx}, board_y={by}")
                
        elif tool_name == "hold_gold":
            logger.info(f"AI quyết định giữ tiền tích econ. Lý do: {args.get('reason', 'N/A')}")
            
        else:
            logger.error(f"Không nhận diện được tool: {tool_name}")



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
