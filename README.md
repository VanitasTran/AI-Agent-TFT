<div align="center">
  <img src="https://raw.githubusercontent.com/VanitasTran/AI-Agent-TFT/main/assets/logo.png" width="220" alt="TFT AI Agent Logo">
  <h1>🌌 Autonomous TFT AI Agent — Master Manual</h1>
  <p><b>Hệ thống AI tự động hóa hoàn toàn việc chơi Đấu Trường Chân Lý Mùa 17 bằng Computer Vision & Llama 3.2 Tool-Calling</b></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/OpenCV-RAM_Piping-green?style=for-the-badge&logo=opencv" alt="OpenCV">
    <img src="https://img.shields.io/badge/Ollama-Llama_3.2-orange?style=for-the-badge&logo=ollama" alt="Ollama">
    <img src="https://img.shields.io/badge/ADB-Android-3DDC84?style=for-the-badge&logo=android" alt="ADB">
  </p>
</div>

---

## 📖 Mục lục
1. [Tổng quan hệ thống](#-tổng-quan-hệ-thống)
2. [Kiến trúc Tool-Calling Agent](#-kiến-trúc-tool-calling-agent)
3. [Tối ưu hóa hiệu năng siêu tốc](#-tối-ưu-hóa-hiệu-năng-siêu-tốc)
4. [Tích hợp ĐTCL Mùa 17 (Space Gods)](#-tích-hợp-đtcl-mùa-17-space-gods)
5. [Hướng dẫn cài đặt & Khởi chạy](#%EF%B8%8F-hướng-dẫn-cài-đặt--khởi-chạy)
6. [Hồ sơ hiệu chuẩn tọa độ (Calibration Log)](#-hồ-sơ-hiệu-chuẩn-tọa-độ-calibration-log)
7. [Lộ trình phát triển (Roadmap)](#-lộ-trình-phát-triển-roadmap)

---

## 🌟 Tổng quan hệ thống
**TFT AI Agent** là hệ thống AI Agent chơi ĐTCL (TFT Mobile) tự động tích hợp mô hình **Tool-Calling** hiện đại. Agent kết hợp chụp màn hình siêu tốc, xử lý thị giác máy tính OpenCV để trích xuất trạng thái game (State) và gửi trực tiếp tới bộ não LLM cục bộ (Ollama - Llama 3.2) để chọn lựa và thực thi các **Gaming Tools** chuyên dụng thông qua giao thức kết nối ADB.

---

## 🏗️ Kiến trúc Tool-Calling Agent
Hệ thống hoạt động theo mô hình **Đầu não chỉ huy & Công cụ thực thi**:

```
 ┌────────────────────────────────────────────────────────┐
 │                      GAME DEVICE                       │
 │                   (TFT Android Phone)                  │
 └───────────▲──────────────────────────────┬─────────────┘
             │ ADB Action Swipe/Tap         │ ADB exec-out screencap -p
             │                              ▼ (Sub-100ms)
 ┌───────────┴──────────┐       ┌─────────────────────────┐
 │   ACTION EXECUTOR    │       │     VISION ENGINE       │
 │  (Gaming Toolkit)    │       │   (OpenCV + EasyOCR)    │
 └───────────▲──────────┘       └───────────┬─────────────┘
             │                              │ Structured Game State
             │ Executed Tool                ▼ (Gold, Level, HP, Shop)
 ┌───────────┴──────────────────────────────┴─────────────┐
 │                     MAIN CONTROLLER                    │
 │         State Change Detection & Fast Path Router      │
 └──────────────────────────┬─────────────────────────────┘
                            │ Query Llama 3.2 (If state changed)
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │                       LLM BRAIN                        │
 │           Local Ollama API (Llama 3.2 3B)              │
 │      Quyết định Tool và Tham số dưới dạng JSON         │
 └────────────────────────────────────────────────────────┘
```

### Bộ Gaming Tools (Toolkit) đăng ký với AI:
1.  `buy_shop_unit(slot_index)`: Mua tướng ở Shop.
2.  `roll_shop()`: Tái chọn cửa hàng (2 vàng).
3.  `level_up()`: Mua kinh nghiệm (4 vàng).
4.  `sell_bench_unit(bench_slot)`: Bán tướng trên hàng chờ.
5.  `deploy_bench_to_board(bench_slot, board_x, board_y)`: Kéo tướng từ hàng chờ ra sân đấu.
6.  `reposition_board_units(from_x, from_y, to_x, to_y)`: Hoán đổi vị trí cờ.
7.  `select_god_blessing(choice_index)`: Chọn chúc phúc của Thần Vũ Trụ.
8.  `select_augment(augment_index)`: Chọn Lõi Nâng Cấp công nghệ.
9.  `equip_item_to_unit(item_index, board_x, board_y)`: Ghép và lắp trang bị cho tướng.
10. `hold_gold(reason)`: Tích vàng nhận lợi tức.

---

## ⚡ Tối ưu hóa hiệu năng siêu tốc
Để đạt tốc độ phản xạ chớp nhoáng của các tool thương mại, hệ thống đã giải quyết triệt để 3 điểm nghẽn hiệu năng lớn:

1.  **RAM Stream Piping (Chụp ảnh siêu tốc dưới 100ms)**:
    Sử dụng lệnh `adb exec-out screencap -p` để truyền trực tiếp luồng byte ảnh từ điện thoại vào bộ nhớ RAM máy tính. Ảnh được OpenCV decode trực tiếp bằng `cv2.imdecode` mà không cần ghi đĩa flash trên điện thoại hay chạy lệnh `adb pull` chậm chạp.
2.  **EasyOCR Fast Path (Quét số trong 300ms)**:
    Cấu hình bộ nhận diện số chỉ định `allowlist='0123456789'` và bỏ qua phân đoạn vị trí `detail=0` để giảm tải 90% tính toán mạng nơ-ron tích chập.
3.  **State Change Detection (Bỏ qua LLM khi combat)**:
    So khớp trạng thái mới và cũ của Gold, HP, Level, Shop. Nếu trạng thái tĩnh (ví dụ đang trong Combat dài), Agent sẽ bỏ qua gọi LLM và phản xạ tức thời trong vòng **150ms** để tiết kiệm điện năng và giảm tải CPU.

---

## 🌌 Tích hợp ĐTCL Mùa 17 (Space Gods)
Agent được thiết kế sẵn sàng hỗ trợ cơ chế cốt lõi của **Mùa 17 (Space Gods - Thần Vũ Trụ)**:
*   **Vòng Realm of the Gods (Stage 2-4, 3-4, 4-4)**: Bấm chọn chúc phúc của các vị Thần Vũ Trụ hoặc Pengu bằng tool `select_god_blessing`.
*   **Bảng chọn Lõi nâng cấp (Augments)**: Bấm chọn lõi công nghệ tự động bằng `select_augment`.
*   **Tự động cân bằng độ phân giải (Auto-Scaling)**: Hệ thống đọc kích thước màn hình thực tế qua giao thức ADB và tự động co giãn tỷ lệ tất cả tọa độ ô cờ Hexagon 4x7 và vùng bấm từ màn hình chuẩn thiết kế `2400x1080` sang bất cứ độ phân giải nào khác.

---

## 🛠️ Hướng dẫn cài đặt & Khởi chạy

### 1. Yêu cầu hệ thống
*   Python 3.10+ cài đặt trong thư mục ảo (Virtual Environment).
*   Điện thoại Android đã bật gỡ lỗi **USB Debugging** (hoặc trình giả lập) kết nối với PC bằng cáp USB truyền dữ liệu tốt.
*   [Ollama](https://ollama.com/) đang hoạt động cục bộ trên máy tính. Tải model Llama 3.2 bằng dòng lệnh:
    ```bash
    ollama run llama3.2
    ```

### 2. Cài đặt nhanh
```bash
# Clone dự án về máy
git clone https://github.com/VanitasTran/AI-Agent-TFT.git
cd AI-Agent-TFT

# Kích hoạt môi trường ảo của dự án
venv\Scripts\activate

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

### 3. Vận hành Agent
```bash
# Khởi chạy Agent tự động
python main.py
```

---

## 📐 Hồ sơ hiệu chuẩn tọa độ (Calibration Log)
Dưới đây là nhật ký tọa độ chuẩn của màn hình **2400x1080** được lưu lại qua công cụ `calibrate.py` (tất cả các dòng máy khác sẽ tự động co giãn tỷ lệ tuyến tính dựa trên khung này):

### Các vùng chỉ số chính:
*   **Vàng (Gold Area)**: `X: 2049, Y: 859, W: 198, H: 200`
*   **Nút Roll**: `X: 2064, Y: 621, W: 176, H: 198`
*   **Nút Kinh Nghiệm (XP)**: `X: 165, Y: 870, W: 223, H: 189`
*   **Shop Tướng Slots 1 - 5**:
    *   Slot 1: `X: 620, Y: 74, W: 289, H: 347`
    *   Slot 2: `X: 948, Y: 77, W: 301, H: 346`
    *   Slot 3: `X: 1276, Y: 77, W: 298, H: 346`
    *   Slot 4: `X: 1604, Y: 77, W: 298, H: 346`
    *   Slot 5: `X: 1943, Y: 87, W: 294, H: 323`

### Hàng chờ Bench slots 1 - 9:
*   Slot 1: `X: 536, Y: 918, W: 143, H: 109`
*   Slot 2: `X: 709, Y: 921, W: 126, H: 106`
*   Slot 3: `X: 852, Y: 921, W: 123, H: 106`
*   Slot 4: `X: 1000, Y: 929, W: 121, H: 96`
*   Slot 5: `X: 1148, Y: 931, W: 119, H: 100`
*   Slot 6: `X: 1284, Y: 929, W: 109, H: 98`
*   Slot 7: `X: 1425, Y: 933, W: 126, H: 96`
*   Slot 8: `X: 1575, Y: 935, W: 129, H: 94`
*   Slot 9: `X: 1721, Y: 938, W: 106, H: 91`

### Tọa độ Lõi nâng cấp (Augments 1 - 3):
*   Lõi 1: `X: 478, Y: 188, W: 403, H: 621` (Đổi lõi: `X: 620, Y: 887, W: 127, H: 129`)
*   Lõi 2: `X: 1008, Y: 173, W: 392, H: 660` (Đổi lõi: `X: 1150, Y: 887, W: 114, H: 125`)
*   Lõi 3: `X: 1542, Y: 185, W: 377, H: 636` (Đổi lõi: `X: 1669, Y: 896, W: 104, H: 108`)

---

## 🎯 Lộ trình phát triển (Roadmap)
*   **Giai đoạn 1: Master Vision & Opponent Scouting**
    *   [x] Tự động co giãn màn hình đa độ phân giải.
    *   [ ] Quét và nhận diện round đấu (`2-1`, `3-2`...) để AI tính toán vòng quái/PvP.
    *   [ ] Đổi nhà quan sát đối thủ để phân tích hệ tộc đang bị tranh bài (Contested).
*   **Giai đoạn 2: Advanced Logic & Item Handlers**
    *   [x] Xây dựng tool kéo thả trang bị tự động lên tướng chiến đấu.
    *   [ ] Logic ghép đồ thành phẩm tối ưu cho Carry chính từ các mảnh thành phần.
*   **Giai đoạn 3: Positioning Hex Optimization**
    *   [x] Hệ toán staggered coordinate lưới Hexagon 4x7 cho bàn cờ.
    *   [ ] Dạy LLM các thế trận xếp bài nâng cao (Carry né sát thủ, Tanker chắn đường).

---
<div align="center">
  Kiến tạo bởi <b>VanitasTran</b> & Cộng Đồng AI Agent ĐTCL Việt Nam ❤️
</div>