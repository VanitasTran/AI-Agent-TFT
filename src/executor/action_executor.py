import logging
import time

class ActionExecutor:
    def __init__(self, adb_controller, config):
        self.adb = adb_controller
        self.config = config
        self.logger = logging.getLogger(__name__)

    def buy_unit(self, slot_index):
        """Thực hiện click vào ô shop tương ứng để mua (0-4)"""
        try:
            reg = self.config['regions']['shop_slots'][slot_index]
            x, y, w, h = reg
            center_x = x + w // 2
            center_y = y + h // 2
            
            logging.warning(f"🛒 EXECUTOR: Đang mua tướng ở ô số {slot_index + 1}")
            return self.adb.tap(center_x, center_y)
        except Exception as e:
            logging.error(f"Lỗi khi mua tướng: {e}")
            return False

    def roll(self):
        """Thực hiện click nút Roll"""
        try:
            reg = self.config['regions']['btn_roll']
            x, y, w, h = reg
            logging.info("🔄 EXECUTOR: Đang thực hiện Roll shop")
            return self.adb.tap(x + w // 2, y + h // 2)
        except Exception as e:
            logging.error(f"Lỗi khi roll: {e}")
            return False

    def level_up(self):
        """Thực hiện click nút Lên cấp (XP)"""
        try:
            reg = self.config['regions']['btn_xp']
            x, y, w, h = reg
            logging.info("🆙 EXECUTOR: Đang thực hiện Lên cấp")
            return self.adb.tap(x + w // 2, y + h // 2)
        except Exception as e:
            logging.error(f"Lỗi khi lên cấp: {e}")
            return False

    def get_board_coords(self, board_x, board_y):
        """Tính toán tọa độ pixel tâm của ô cờ tại cột board_x (0-6) và hàng board_y (0-3)"""
        try:
            grid = self.config['regions']['board_grid']
            start_x = grid['start_x']
            start_y = grid['start_y']
            dx = grid['dx']
            dy = grid['dy']
            row_offset = grid['row_offsets'][board_y]
            
            pos_x = start_x + board_x * dx + row_offset
            pos_y = start_y + board_y * dy
            return int(pos_x), int(pos_y)
        except Exception as e:
            self.logger.error(f"Lỗi khi tính tọa độ bàn cờ ({board_x}, {board_y}): {e}")
            return 0, 0

    def sell_bench_unit(self, bench_slot):
        """Bán tướng ở hàng chờ bằng cách kéo thả vào ô bán tướng ở góc trái (bench_slot từ 0-8)"""
        try:
            reg = self.config['regions']['bench_slots'][bench_slot]
            x, y, w, h = reg
            from_x = x + w // 2
            from_y = y + h // 2
            
            sell_reg = self.config['regions']['sell_zone_left']
            sx, sy, sw, sh = sell_reg
            to_x = sx + sw // 2
            to_y = sy + sh // 2
            
            self.logger.warning(f"💰 EXECUTOR: Đang bán tướng ở hàng chờ ô số {bench_slot + 1}")
            return self.adb.swipe(from_x, from_y, to_x, to_y, duration=400)
        except Exception as e:
            self.logger.error(f"Lỗi khi bán tướng hàng chờ: {e}")
            return False

    def deploy_bench_to_board(self, bench_slot, board_x, board_y):
        """Kéo tướng từ hàng chờ (0-8) lên bàn cờ tại vị trí ô (board_x: 0-6, board_y: 0-3)"""
        try:
            reg = self.config['regions']['bench_slots'][bench_slot]
            x, y, w, h = reg
            from_x = x + w // 2
            from_y = y + h // 2
            
            to_x, to_y = self.get_board_coords(board_x, board_y)
            if to_x == 0 and to_y == 0:
                return False
            
            self.logger.warning(f"⚔️ EXECUTOR: Kéo tướng từ hàng chờ ô {bench_slot + 1} lên bàn cờ tại ({board_x}, {board_y})")
            return self.adb.swipe(from_x, from_y, to_x, to_y, duration=500)
        except Exception as e:
            self.logger.error(f"Lỗi khi kéo tướng lên bàn cờ: {e}")
            return False

    def reposition_board_units(self, from_x, from_y, to_x, to_y):
        """Hoán đổi/Di chuyển tướng giữa hai ô cờ (from_x, from_y) và (to_x, to_y)"""
        try:
            start_x, start_y = self.get_board_coords(from_x, from_y)
            end_x, end_y = self.get_board_coords(to_x, to_y)
            if start_x == 0 or end_x == 0:
                return False
            
            self.logger.warning(f"🔄 EXECUTOR: Di chuyển tướng từ ô ({from_x}, {from_y}) sang ô ({to_x}, {to_y})")
            return self.adb.swipe(start_x, start_y, end_x, end_y, duration=500)
        except Exception as e:
            self.logger.error(f"Lỗi khi di chuyển tướng trên bàn cờ: {e}")
            return False

    def select_god_blessing(self, choice_index):
        """Bấm chọn 1 trong 3 Lựa chọn Chúc Phúc của Thần (choice_index từ 0 đến 2) tại Stage 2-4, 3-4, 4-4"""
        try:
            coord = self.config['regions']['god_blessing_slots'][choice_index]
            x, y = coord
            self.logger.warning(f"🔮 EXECUTOR: Bấm chọn Chúc Phúc của Thần ở ô số {choice_index + 1}")
            return self.adb.tap(x, y)
        except Exception as e:
            self.logger.error(f"Lỗi khi chọn chúc phúc của Thần: {e}")
            return False

    def select_augment(self, augment_index):
        """Bấm chọn 1 trong 3 Lõi Nâng Cấp Nâng (augment_index từ 0 đến 2) tại Stage 2-1, 3-2, 4-2"""
        try:
            coord = self.config['regions']['augment_slots'][augment_index]
            x, y = coord
            self.logger.warning(f"🧬 EXECUTOR: Bấm chọn Lõi Nâng Cấp ở ô số {augment_index + 1}")
            return self.adb.tap(x, y)
        except Exception as e:
            self.logger.error(f"Lỗi khi chọn Lõi Nâng Cấp: {e}")
            return False

    def equip_item_to_unit(self, item_index, board_x, board_y):
        """Kéo thả trang bị từ ô dự bị (item_index từ 0-9) vào tướng trên bàn cờ tại ô (board_x, board_y)"""
        try:
            coord = self.config['regions']['item_slots'][item_index]
            from_x, from_y = coord
            
            to_x, to_y = self.get_board_coords(board_x, board_y)
            if to_x == 0 or to_y == 0:
                return False
            
            self.logger.warning(f"⚔️ EXECUTOR: Kéo trang bị ở ô {item_index + 1} vào tướng tại ô ({board_x}, {board_y})")
            return self.adb.swipe(from_x, from_y, to_x, to_y, duration=600)
        except Exception as e:
            self.logger.error(f"Lỗi khi kéo ghép trang bị: {e}")
            return False


