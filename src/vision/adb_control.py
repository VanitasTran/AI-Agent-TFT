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

    def capture_screen(self, filename="screen.png"):
        device_temp_path = "/sdcard/screen_temp.png"
        success_cap, _ = self._execute(f"shell screencap -p {device_temp_path}")
        if not success_cap:
            return False
        success_pull, _ = self._execute(f"pull {device_temp_path} {filename}")
        return success_pull

    def tap(self, x, y):
        # Sử dụng swipe tại chỗ với thời gian 100ms để game dễ nhận diện hơn lệnh tap thuần túy
        return self._execute(f"shell input swipe {int(x)} {int(y)} {int(x)} {int(y)} 100")

    def swipe(self, x1, y1, x2, y2, duration=300):
        return self._execute(f"shell input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {duration}")
