import cv2
import os
import sys

# Thêm đường dẫn để import được ADBController
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from vision.adb_control import ADBController

# Cấu hình
TEMP_FILE = "calibration_screen.png"
adb = ADBController()

# Biến toàn cục để lưu trạng thái chuột
ix, iy = -1, -1
drawing = False
roi = (0, 0, 0, 0)

def draw_info(event, x, y, flags, param):
    global ix, iy, drawing, roi, img, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        print(f"\n[POINT] Clicked at: (X: {x}, Y: {y})")
        # Gửi lệnh Tap thử để người dùng xác nhận
        adb.tap(x, y)
        print(f"       -> Đã gửi lệnh bấm thử vào điện thoại tại ({x}, {y})")

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("CALIBRATION - Click to see Point, Drag to see Area", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        w = abs(x - ix)
        h = abs(y - iy)
        rx = min(ix, x)
        ry = min(iy, y)
        roi = (rx, ry, w, h)
        
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
        print(f"[AREA] Selected region: (X: {rx}, Y: {ry}, W: {w}, H: {h})")
        print(f"       Usage for OCR: region = ({rx}, {ry}, {w}, {h})")

def main():
    global img, img_copy

    print("--- TFT CALIBRATION TOOL ---")
    print("Đang chụp màn hình từ điện thoại...")
    
    if not adb.check_device():
        print("LỖI: Không tìm thấy thiết bị ADB!")
        return

    if not adb.capture_screen(TEMP_FILE):
        print("LỖI: Không thể chụp màn hình!")
        return

    img = cv2.imread(TEMP_FILE)
    if img is None:
        print("LỖI: Không thể đọc file ảnh!")
        return

    # Resize nếu ảnh quá lớn để hiển thị trên màn hình PC (tùy chọn)
    # img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 

    img_copy = img.copy()
    cv2.namedWindow("CALIBRATION - Click to see Point, Drag to see Area", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("CALIBRATION - Click to see Point, Drag to see Area", draw_info)

    print("\nHƯỚNG DẪN:")
    print("1. Click chuột trái: Xem tọa độ điểm.")
    print("2. Kéo thả chuột trái: Xem tọa độ vùng (X, Y, W, H).")
    print("3. Nhấn phím 'r': Chụp lại màn hình mới.")
    print("4. Nhấn phím 'ESC' hoặc 'q': Thoát.")

    while True:
        cv2.imshow("CALIBRATION - Click to see Point, Drag to see Area", img_copy)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('r'): # Refresh
            print("Đang chụp lại...")
            adb.capture_screen(TEMP_FILE)
            img = cv2.imread(TEMP_FILE)
            img_copy = img.copy()
        elif key == 27 or key == ord('q'): # Exit
            break

    cv2.destroyAllWindows()
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)

if __name__ == "__main__":
    main()
