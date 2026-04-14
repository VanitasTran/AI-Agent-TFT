# TFT AI LOGIC (SIMPLIFIED & PRECISE)

## 1. OBJECTIVE

* Mục tiêu chính: Top 4
* Nếu có lợi thế: hướng tới Top 1

---

## 2. CORE VARIABLES

State gồm:

* gold (0–100)
* hp (0–100)
* level (1–9)
* shop (list tướng)
* bench (tướng dự bị)
* board (đội hình hiện tại)
* items

---

## 3. ECON RULE

* gold < 10:
  → tiêu hợp lý để mạnh sớm

* 10 ≤ gold < 50:
  → ưu tiên tích tiền

* gold ≥ 50:
  → giữ, chỉ tiêu khi cần

---

## 4. HP RULE

* hp > 70:
  → chơi greed (ưu tiên econ)

* 40 < hp ≤ 70:
  → cân bằng econ và sức mạnh

* hp ≤ 40:
  → bỏ econ, roll để sống

---

## 5. ROLL LOGIC

Roll khi:

* hp ≤ 40
* thua nhiều round liên tiếp
* cần nâng tướng lên 2 sao (đã có 2 bản sao)

Không roll khi:

* đang giữ econ
* board đủ mạnh để không mất nhiều máu

---

## 6. LEVEL LOGIC

Level up khi:

* đang win streak
* board mạnh
* còn dư gold sau khi giữ econ

Không level khi:

* hp thấp và cần roll
* đang xây dựng đội hình chưa ổn định

---

## 7. BUY / SELL

Buy khi:

* tướng thuộc đội hình đang build
* có thể nâng sao (2/3 bản)
* tướng mạnh đầu game

Sell khi:

* không thuộc đội hình
* không có synergy
* cần giải phóng gold

---

## 8. TEAM BUILDING

* luôn ưu tiên synergy (hệ/tộc)
* không giữ quá nhiều tướng không liên quan
* xác định 1 đội hình chính từ sớm

---

## 9. UPGRADE PRIORITY

Ưu tiên:

1. tướng có thể lên 2 sao
2. carry chính
3. frontline

---

## 10. POSITIONING

* tank ở hàng trước
* carry ở hàng sau
* tránh để carry bị focus trực tiếp

---

## 11. ITEM LOGIC

* ưu tiên ghép item sớm nếu giúp giữ máu
* item đúng tướng quan trọng hơn giữ item đẹp

---

## 12. DECISION PRIORITY

Thứ tự ưu tiên:

1. Sống sót (hp thấp → roll)
2. Nâng cấp đội hình (2 sao)
3. Giữ kinh tế (gold ≥ 50)
4. Tăng cấp (level)
5. Giữ trạng thái

---

## 13. FINAL DECISION FUNCTION

Pseudo:

if hp ≤ 40:
return "roll"

if can_upgrade_unit:
return "buy"

if gold ≥ 50:
return "hold"

if strong_board and gold > threshold:
return "level_up"

return "hold"
