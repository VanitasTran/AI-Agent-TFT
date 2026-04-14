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

    def sell_unit(self, bench_index):
        """Thực hiện bán tướng ở hàng chờ (Chưa triển khai kéo thả, chỉ demo tap)"""
        # Lưu ý: Bán tướng thường cần kéo vào góc hoặc click rồi bấm nút bán
        # Tạm thời để skeleton ở đây
        pass
