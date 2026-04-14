# 🗺️ TFT AI AGENT ROADMAP & RESEARCH

## 🎯 Mục tiêu hiện tại
Nâng cấp Agent từ hệ thống phản xạ đơn giản (Reactive) sang hệ thống chiến lược (Strategic).

---

## 🛠️ GIAI ĐOẠN 1: LÀM CHỦ THỊ GIÁC (VISION MASTER)
Đây là nền tảng để Agent không còn bị "mù" thông tin.

*   **1.1. Thu thập bộ Unit Templates khổng lồ:**
    *   Cần chụp ảnh tất cả tướng ở nhiều mức sao (1, 2, 3 sao) và trạng thái (trong shop, trên bench).
    *   *Kế hoạch:* Tạo script tự động lưu ảnh tướng vào `debug/` sau mỗi lượt mua thành công để người dùng chỉ cần phân loại.
*   **1.2. Nhận diện Round (Giai đoạn):**
    *   Cần đọc được con số `2-1`, `3-2`... ở phía trên màn hình.
    *   *Mục đích:* Giúp AI biết khi nào sắp đến vòng quái, khi nào sắp đến vòng chọn chung.
*   **1.3. Trạng thái Shop (Ẩn/Hiện):**
    *   Xác định tọa độ nút Tắt/Mở Shop.
    *   *Mục đích:* Agent cần tắt Shop để quan sát đội hình của mình và đối thủ.

---

## 🧠 GIAI ĐOẠN 2: TRINH SÁT & ĐỐI THỦ (OPPONENT SCOUTING)
Agent sẽ không chơi một mình, nó sẽ "liếc" sang nhà hàng xóm.

*   **2.1. Tự động soi nhà (Scouting):**
    *   Gửi lệnh Tab hoặc Click vào danh sách người chơi bên phải để đổi góc nhìn.
    *   Nhận diện: Đối thủ đang chơi hệ gì? Họ có bao nhiêu tiền? Họ đã lên cấp mấy?
*   **2.2. Đánh giá sức mạnh (Power Calculation):**
    *   Đếm số tướng 2 sao/3 sao của đối thủ.
    *   Đếm số trang bị hoàn chỉnh trên bàn cờ.
    *   *Decision:* Nếu đối thủ quá mạnh -> Cần Roll sớm để giữ máu. Nếu mình đang mạnh nhất -> Kiếm tiền (Greed).

---

## 🏗️ GIAI ĐOẠN 3: CHIẾN THUẬT NÂNG CAO (ADVANCED LOGIC)
Nâng cấp file `rule_tft.md` thành một bộ quy tắc thông minh hơn.

*   **3.1. Phân loại đội hình (Archtypes):**
    *   Dạy Agent các đội hình Meta (ví dụ: Zaun, Bilgewater, Ixtal...).
    *   *Logic:* Nếu đã có 2 tướng Ixtal -> Ưu tiên mua Ixtal, bán các tướng khác.
*   **3.2. Quản lý Trang bị (Item Management):**
    *   Nhận diện Item trong kho.
    *   *Logic:* Ghép đồ sớm để giữ máu hay đợi đồ chuẩn (Best in slot)?

---

## 🎮 GIAI ĐOẠN 4: THỰC THI CHUẨN XÁC (PRECISE EXECUTION)
*   **4.1. Kéo & Thả (Drag & Drop):**
    *   Phát triển lệnh `adb.swipe` để Agent có thể kéo tướng từ hàng chờ lên sân và ngược lại.
    *   Kéo trang bị lắp vào tướng.
*   **4.2. Sắp xếp đội hình (Positioning):**
    *   Gemma sẽ ra lệnh: "Kéo Garen vào ô (3, 1)" để tối ưu hóa việc chống chịu.

---

## 📝 CÁC CÔNG VIỆC CẦN LÀM NGAY (ACTION ITEMS)
1.  **Cập nhật `regions.yaml`**: Thêm vùng quét Round và nút Tắt/Mở Shop.
2.  **Viết Logic `scout()`**: Thử nghiệm việc click vào danh sách đối thủ và chụp ảnh sân của họ.
3.  **Mở rộng File Rule**: Định nghĩa rõ các giai đoạn (Early, Mid, Late game).
