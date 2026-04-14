import easyocr
import cv2
import logging

class OCRReader:
    def __init__(self, languages=['en']):
        self.reader = easyocr.Reader(languages)
        logging.info("EasyOCR initialized.")

    def read_text(self, image_np):
        """Đọc text từ một ảnh numpy array"""
        results = self.reader.readtext(image_np)
        return results

    def extract_value(self, image_np, region=None):
        """Trích xuất giá trị số từ một vùng cụ thể"""
        if region:
            x, y, w, h = region
            crop = image_np[y:y+h, x:x+w]
        else:
            crop = image_np
        
        results = self.reader.readtext(crop)
        for (_, text, conf) in results:
            # Làm sạch text để lấy số
            clean_text = ''.join(filter(str.isdigit, text))
            if clean_text:
                return int(clean_text)
        return None
