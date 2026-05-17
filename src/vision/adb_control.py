import subprocess
import logging
import os

class ADBController:
    def __init__(self, adb_path="adb"):
        self.adb_path = adb_path

    def _execute(self, command):
        full_command = f"{self.adb_path} {command}"
        try:
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr.strip()
            return True, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def check_device(self):
        success, output = self._execute("devices")
        if success:
            lines = output.splitlines()
            devices = [line for line in lines[1:] if line.strip() and "device" in line]
            if devices:
                return True
        return False

    def get_screen_resolution(self):
        """Lấy độ phân giải thực tế của màn hình điện thoại từ ADB"""
        success, output = self._execute("shell wm size")
        if success:
            # Output mẫu: "Physical size: 2400x1080" hoặc "Physical size: 1080x2400"
            for line in output.splitlines():
                if "Physical size" in line:
                    parts = line.split(":")[-1].strip().split("x")
                    if len(parts) == 2:
                        try:
                            # Trả về [rộng, cao]
                            return [int(parts[0]), int(parts[1])]
                        except:
                            pass
        return None


    def capture_screen(self, filename="screen.png"):
        device_temp_path = "/sdcard/screen_temp.png"
        success_cap, _ = self._execute(f"shell screencap -p {device_temp_path}")
        if not success_cap:
            return False
        success_pull, _ = self._execute(f"pull {device_temp_path} {filename}")
        return success_pull

    def capture_screen_fast(self):
        """Chụp ảnh màn hình cực nhanh trực tiếp vào bộ nhớ RAM bằng adb exec-out (Sub-120ms!)"""
        import numpy as np
        import cv2
        full_command = f"{self.adb_path} exec-out screencap -p"
        try:
            process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0 or not stdout:
                return None
            
            # Giải mã luồng dữ liệu nhị phân thành numpy array và decode sang định dạng ảnh bằng OpenCV
            img_array = np.frombuffer(stdout, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logging.error(f"Lỗi chụp màn hình siêu tốc: {e}")
            return None


    def tap(self, x, y):
        # Sử dụng swipe tại chỗ với thời gian 100ms để game dễ nhận diện hơn lệnh tap thuần túy
        return self._execute(f"shell input swipe {int(x)} {int(y)} {int(x)} {int(y)} 100")

    def swipe(self, x1, y1, x2, y2, duration=300):
        return self._execute(f"shell input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {duration}")
