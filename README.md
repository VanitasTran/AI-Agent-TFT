<div align="center">
  <img src="https://raw.githubusercontent.com/VanitasTran/AI-Agent-TFT/main/assets/logo.png" width="250" alt="TFT AI Agent Logo">
  <h1>🎮 Autonomous TFT AI Agent</h1>
  <p><b>Hệ thống AI tự động hóa hoàn toàn việc chơi Teamfight Tactics thông qua Computer Vision & LLM</b></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/OpenCV-Analyze-green?style=for-the-badge&logo=opencv" alt="OpenCV">
    <img src="https://img.shields.io/badge/Ollama-Brain-orange?style=for-the-badge&logo=ollama" alt="Ollama">
    <img src="https://img.shields.io/badge/ADB-Android-3DDC84?style=for-the-badge&logo=android" alt="ADB">
  </p>
</div>

---

## 🌟 Tổng quan
**TFT AI Agent** là một dự án nghiên cứu kết hợp giữa xử lý ảnh thời gian thực và trí tuệ nhân tạo để điều khiển game Teamfight Tactics trên các thiết bị Android. Agent không chỉ click đơn thuần mà còn có khả năng **Tư duy chiến thuật** dựa trên trạng thái ván đấu.

## 🚀 Tính năng nổi bật
- **🧠 Brain Engine (Llama 3.2)**: Tự động phân tích Máu, Vàng, Cấp độ để đưa ra quyết định Mua/Bán/Roll theo chiến thuật quản lý kinh tế (Econ).
- **👁️ Computer Vision**: Nhận diện tướng với độ chính xác cao dựa trên Template Matching và OCR (EasyOCR).
- **⚙️ Tối ưu hóa ADB**: Thực hiện thao tác bấm (Tap/Swipe) mượt mà, giả lập hành vi người dùng bằng lệnh `input swipe`.
- **📜 Logic tùy biến**: Hệ thống quy tắc được định nghĩa trong file `rule_tft.md`, cho phép người dùng thay đổi "lối chơi" mà không cần code lại.

## 📸 Demo & Cấu trúc
| Shop Detection | Decision Making |
| :--- | :--- |
| ![Shop](https://img.shields.io/badge/Status-Scanning-brightgreen) | ![Decision](https://img.shields.io/badge/Action-LLM_Controlled-blue) |

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
- Python 3.10+
- Điện thoại Android đã bật **Gỡ lỗi USB** (Nên dùng màn hình 2400x1080).
- [Ollama](https://ollama.com/) đang chạy local (Model: `llama3.2`).

### 2. Cài đặt nhanh
```bash
# Clone dự án
git clone https://github.com/VanitasTran/AI-Agent-TFT.git
cd AI-Agent-TFT

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Hiệu chuẩn (Calibration)
Nếu bạn dùng màn hình khác độ phân giải mặc định, hãy chạy công cụ hiệu chuẩn:
```bash
python calibrate.py
```

## 📂 Sơ đồ kiến trúc
- `src/vision/`: Xử lý hình ảnh & truyền tin ADB.
- `src/brain/`: Kết nối với LLM để ra quyết định.
- `src/executor/`: Thực thi các lệnh điều khiển game.
- `configs/`: Chứa tọa độ vùng chọn trên màn hình.

## 💡 Roadmap
- [ ] Tự động soi nhà đối thủ (Opponent Scouting).
- [ ] Kéo thả trang bị (Item Handling).
- [ ] Logic sắp xếp đội hình (Positioning).

## 🤝 Đóng góp
Chúng tôi rất trân trọng mọi sự đóng góp! Bạn có thể giúp dự án bằng cách:
1. Gửi bản vá lỗi (Pull Request).
2. Đóng góp thêm ảnh mẫu tướng trong `data/unit_templates`.
3. Góp ý về file `rule_tft.md` để AI chơi thông minh hơn.

---
<div align="center">
  Built with ❤️ by <b>VanitasTran</b> & AI Community
</div>