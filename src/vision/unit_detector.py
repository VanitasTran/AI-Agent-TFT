import cv2
import numpy as np
import os
import logging

class UnitDetector:
    def __init__(self, template_dir="data/unit_templates"):
        self.template_dir = template_dir
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            return

        for filename in os.listdir(self.template_dir):
            if filename.endswith((".png", ".jpg")):
                name = os.path.splitext(filename)[0]
                path = os.path.join(self.template_dir, filename)
                img = cv2.imread(path)
                if img is not None:
                    self.templates[name] = img
        logging.info(f"Loaded {len(self.templates)} unit templates.")

    def detect_units(self, screen_img, threshold=0.8):
        results = []
        h_s, w_s = screen_img.shape[:2]

        for name, template in self.templates.items():
            h_t, w_t = template.shape[:2]

            # KIỂM TRA: Nếu ảnh mẫu to hơn ảnh nền thì bỏ qua để tránh crash
            if h_t > h_s or w_t > w_s:
                # logger.warning(f"Bỏ qua {name}: Ảnh mẫu ({w_t}x{h_t}) to hơn vùng shop ({w_s}x{h_s})")
                continue

            res = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            
            for pt in zip(*loc[::-1]):
                results.append({
                    "name": name,
                    "center": (pt[0] + w_t // 2, pt[1] + h_t // 2),
                    "bbox": (pt[0], pt[1], w_t, h_t)
                })
        return results
