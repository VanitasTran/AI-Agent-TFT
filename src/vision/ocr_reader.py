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
        
        # Tối ưu hóa tốc độ cực đại cho EasyOCR bằng cách giới hạn bộ ký tự chỉ quét số (allowlist)
        # và tắt tính năng trả về tọa độ hộp chi tiết (detail=0) để giảm tải tính năng phân đoạn ảnh
        try:
            results = self.reader.readtext(crop, allowlist='0123456789', detail=0)
            for text in results:
                clean_text = ''.join(filter(str.isdigit, text))
                if clean_text:
                    return int(clean_text)
        except Exception as e:
            logging.error(f"Lỗi tối ưu EasyOCR: {e}")
            # Phương án dự phòng cơ bản nếu gặp lỗi phiên bản EasyOCR cũ
            try:
                results = self.reader.readtext(crop)
                for (_, text, conf) in results:
                    clean_text = ''.join(filter(str.isdigit, text))
                    if clean_text:
                        return int(clean_text)
            except:
                pass
        return None

