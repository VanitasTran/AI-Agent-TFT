# 🤖 TFT AI AGENT — THIẾT KẾ HỆ THỐNG TOÀN DIỆN
### Phong cách OpenClaw + Reinforcement Learning
> **Phiên bản:** 1.0 | **Trạng thái:** Phác thảo kiến trúc | **Ngày:** 2025

---

## 📋 MỤC LỤC

1. [Mục tiêu hệ thống](#1-mục-tiêu-hệ-thống)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Module 1 — Vision (Nhìn)](#3-module-1--vision-nhìn)
4. [Module 2 — State Encoding](#4-module-2--state-encoding)
5. [Module 3 — LLM Brain (Chiến lược)](#5-module-3--llm-brain-chiến-lược)
6. [Module 4 — Reinforcement Learning (PPO)](#6-module-4--reinforcement-learning-ppo)
7. [Module 5 — Reward System](#7-module-5--reward-system)
8. [Training Loop](#8-training-loop)
9. [Cơ chế "Tiến hóa" thực sự](#9-cơ-chế-tiến-hóa-thực-sự)
10. [Lộ trình phát triển](#10-lộ-trình-phát-triển)
11. [Rủi ro & Giải pháp](#11-rủi-ro--giải-pháp)
12. [Output kỳ vọng](#12-output-kỳ-vọng)
13. [Stack công nghệ đề xuất](#13-stack-công-nghệ-đề-xuất)

---

## 1. Mục tiêu hệ thống

Xây dựng một **AI Agent tự động chơi Teamfight Tactics** có khả năng:

- **Quan sát** trạng thái game thông qua screen capture + computer vision
- **Ra quyết định** bằng kết hợp LLM (chiến lược meta) + RL Policy (học hành vi)
- **Thực thi hành động** thông qua điều khiển chuột/bàn phím tự động
- **Tự cải thiện** theo thời gian thông qua Reinforcement Learning (PPO)
- **Đạt Top 4 ổn định** và hướng tới Top 1 theo thời gian

---

## 2. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────┐
│                   GAME ENVIRONMENT                       │
│                  (TFT trên màn hình)                    │
└──────────────────────┬──────────────────────────────────┘
                       │ Screenshot (30fps)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  VISION PARSER                           │
│         OCR + Object Detection + Template Match         │
└──────────────────────┬──────────────────────────────────┘
                       │ Structured JSON State
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 STATE ENCODER                            │
│         Scalars + One-hot + Grid + Multi-hot            │
└───────────┬──────────────────────────────┬──────────────┘
            │                              │
            ▼                              ▼
┌───────────────────┐          ┌──────────────────────────┐
│    LLM BRAIN      │          │    RL POLICY MODEL       │
│  (GPT/Claude API) │◄────────►│        (PPO)             │
│  Chiến lược meta  │          │   Học hành vi tối ưu     │
└────────┬──────────┘          └────────────┬─────────────┘
         │                                  │
         └──────────────┬───────────────────┘
                        │ Action
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 ACTION EXECUTOR                          │
│          PyAutoGUI / Mouse + Keyboard Control           │
└──────────────────────┬──────────────────────────────────┘
                       │ Execute
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  REWARD SYSTEM                           │
│         HP delta + Placement + Streak + Synergy         │
└──────────────────────┬──────────────────────────────────┘
                       │ Reward signal
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 TRAINING LOOP                            │
│              PPO Update + Replay Buffer                  │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Module 1 — Vision (Nhìn)

### Mục tiêu
Trích xuất **game state có cấu trúc** từ screenshot màn hình game.

### Input
- Screenshot PNG/JPEG từ màn hình game (1920×1080 hoặc 1280×720)

### Output mẫu

```json
{
  "gold": 32,
  "level": 6,
  "xp": "42/60",
  "hp": 78,
  "round": "3-5",
  "shop": [
    { "unit": "Ahri", "cost": 3, "available": true },
    { "unit": "Garen", "cost": 1, "available": true },
    { "unit": "Lux", "cost": 4, "available": false }
  ],
  "bench": [
    { "slot": 1, "unit": "Ahri", "star": 1 },
    { "slot": 2, "unit": "Ahri", "star": 1 }
  ],
  "board": {
    "a1": { "unit": "Garen", "star": 2, "items": ["BF Sword"] },
    "b2": { "unit": "Ahri", "star": 1, "items": [] },
    "c3": null
  },
  "items_bench": ["Tear of Goddess", "Chain Vest"],
  "traits_active": ["Mage 3", "Void 2"]
}
```

### Pipeline xử lý

```
Screenshot
    │
    ├──► [Crop vùng GOLD]     → OCR (Tesseract / EasyOCR)
    ├──► [Crop vùng LEVEL]    → OCR
    ├──► [Crop vùng HP]       → OCR
    ├──► [Crop vùng SHOP]     → Object Detection (YOLOv8)
    ├──► [Crop vùng BENCH]    → Template Matching / CNN
    ├──► [Crop vùng BOARD]    → Grid Detection + Unit Classifier
    └──► [Crop vùng ITEMS]    → Item Icon Classifier
```

### Công nghệ
- **OCR:** EasyOCR hoặc Tesseract 5.0
- **Object Detection:** YOLOv8 fine-tuned trên TFT assets
- **Template Matching:** OpenCV cho icon item/unit
- **Screen Capture:** `mss` library (60fps, low latency)

---

## 4. Module 2 — State Encoding

### Mục tiêu
Chuyển đổi JSON state → **vector số** để đưa vào mô hình AI.

### Sơ đồ encoding

```
Raw State JSON
      │
      ├── Scalars ──────────────────► [gold/100, hp/100, level/9, round/40]
      │                                         → Vector dim: 4
      │
      ├── Shop ─────────────────────► One-hot encoding (N_units)
      │                                         → Vector dim: ~60
      │
      ├── Board (7×4 grid) ─────────► Mỗi ô: [unit_id, star_level, item1, item2, item3]
      │                               Flatten: 28 ô × 5 features
      │                                         → Vector dim: 140
      │
      ├── Bench (9 slots) ──────────► Tương tự board
      │                                         → Vector dim: 45
      │
      └── Items bench ────────────► Multi-hot vector (N_items)
                                              → Vector dim: ~80
                                    
Total State Vector: ~330 dimensions
```

### Code mẫu (Python)

```python
import numpy as np

N_UNITS = 60   # Tổng số tướng
N_ITEMS = 80   # Tổng số item

def encode_state(state: dict) -> np.ndarray:
    # Scalars
    scalars = np.array([
        state["gold"] / 100.0,
        state["hp"] / 100.0,
        state["level"] / 9.0,
        parse_round(state["round"]) / 40.0
    ])
    
    # Shop: one-hot
    shop_vec = np.zeros(N_UNITS)
    for unit in state["shop"]:
        shop_vec[UNIT_TO_IDX[unit["unit"]]] = 1.0
    
    # Board: grid encoding
    board_vec = encode_grid(state["board"], shape=(7, 4))
    
    # Items
    item_vec = np.zeros(N_ITEMS)
    for item in state["items_bench"]:
        item_vec[ITEM_TO_IDX[item]] = 1.0
    
    return np.concatenate([scalars, shop_vec, board_vec, item_vec])
```

---

## 5. Module 3 — LLM Brain (Chiến lược)

### Vai trò
- Nắm giữ **meta knowledge** (đội hình mạnh, synergy, item path)
- Đưa ra **gợi ý chiến lược cấp cao** cho RL Policy
- Giải thích lý do hành động (interpretability)

### System Prompt

```
Bạn là một AI chơi Teamfight Tactics ở trình độ Challenger.

Nhiệm vụ:
- Phân tích trạng thái game hiện tại
- Đưa ra quyết định tối ưu dựa trên meta
- Ưu tiên: Top 1 > Top 4 > sống sót

Nguyên tắc cốt lõi:
1. Kinh tế (Economy):
   - Giữ ≥50 gold để ăn lãi 5/round
   - Chỉ roll khi ≤30 HP hoặc có comp hoàn chỉnh
   
2. Win/Lose Streak:
   - Win streak (3+): Giữ gold, không roll
   - Lose streak có kiểm soát: Tiết kiệm để cướp streak bonus
   
3. Up sao:
   - Ưu tiên 2★ core units ngay khi có 2 bản
   - 3★ chỉ khi còn nhiều HP và gold dư
   
4. Level up:
   - Level 7 trước round 4-1
   - Level 8 khi có ≥50 gold
   
5. Item priority:
   - Hoàn thiện item cho carry trước
   - Không để item component quá nhiều trên bench
```

### User Prompt Template

```
=== TRẠNG THÁI GAME ===
Round: {round} | Phase: {phase}
Gold: {gold} (Lãi: {interest}/round)
Level: {level} (XP: {xp})
HP: {hp}/100

=== ĐỘI HÌNH HIỆN TẠI ===
Board: {board_summary}
Synergy active: {traits}

=== SHOP ===
{shop_units}

=== BENCH ===
{bench_units}

=== ITEM TRÊN TAY ===
{items}

=== CÂU HỎI ===
Hành động tốt nhất là gì? Trả lời theo format:
ACTION: [roll/buy/sell/level_up/reposition/hold]
TARGET: [unit_name / position / none]  
REASON: [1 câu giải thích]
PRIORITY: [high/medium/low]
```

### Output Parser

```python
def parse_llm_action(response: str) -> dict:
    lines = response.strip().split('\n')
    action = {}
    for line in lines:
        if line.startswith("ACTION:"):
            action["type"] = line.split(":")[1].strip()
        elif line.startswith("TARGET:"):
            action["target"] = line.split(":")[1].strip()
        elif line.startswith("REASON:"):
            action["reason"] = line.split(":")[1].strip()
    return action
```

---

## 6. Module 4 — Reinforcement Learning (PPO)

### Thuật toán: PPO (Proximal Policy Optimization)

PPO được chọn vì:
- Ổn định hơn DQN với action space lớn
- Phù hợp với **discrete + continuous mixed actions**
- Sample efficient hơn vanilla Policy Gradient

### Kiến trúc mạng

```
State Vector (330-dim)
        │
        ▼
┌────────────────────┐
│  Shared Backbone   │
│  MLP: 330→512→256  │
│  Activation: ReLU  │
└──────┬─────────────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
[Actor]   [Critic]
256→128   256→128
128→A     128→1
(Policy)  (Value)
```

### Action Space

```python
ACTION_SPACE = {
    # Macro actions
    "roll": 0,           # Roll shop (cost 2 gold)
    "level_up": 1,       # Buy XP (cost 4 gold)
    "hold": 2,           # Không làm gì
    
    # Buy actions: buy_unit_0 đến buy_unit_4 (5 slot shop)
    "buy_0": 3,
    "buy_1": 4,
    "buy_2": 5,
    "buy_3": 6,
    "buy_4": 7,
    
    # Sell actions: sell từ bench slot 1-9
    "sell_bench_0": 8,
    # ... đến sell_bench_8: 16
    
    # Move: từ bench → board (28 vị trí)
    # move_bench_X_to_board_Y: 17 đến ...
    
    # Reposition: swap 2 tướng trên board
    # swap_A_B: ...
}

TOTAL_ACTIONS ≈ 200  # Sau khi flatten
```

### Training Config

```python
PPO_CONFIG = {
    "learning_rate": 3e-4,
    "n_steps": 2048,           # Steps trước mỗi update
    "batch_size": 64,
    "n_epochs": 10,            # PPO epochs per update
    "gamma": 0.99,             # Discount factor
    "gae_lambda": 0.95,        # GAE lambda
    "clip_range": 0.2,         # PPO clip epsilon
    "ent_coef": 0.01,          # Entropy bonus (khuyến khích explore)
    "vf_coef": 0.5,            # Value function coefficient
    "max_grad_norm": 0.5,
}
```

---

## 7. Module 5 — Reward System

> ⚠️ **Reward shaping là yếu tố quan trọng nhất** quyết định AI học được gì.

### Reward Table

| Sự kiện | Reward | Ghi chú |
|---------|--------|---------|
| **Placement Rewards** | | |
| Top 1 | +100 | Chiến thắng tuyệt đối |
| Top 2 | +60 | |
| Top 3 | +40 | |
| Top 4 | +20 | Vùng an toàn |
| Top 5 | -10 | |
| Top 6 | -25 | |
| Top 7 | -40 | |
| Top 8 | -60 | Thất bại hoàn toàn |
| **Per-Round Rewards** | | |
| Thắng round PvP | +5 | |
| Thua round PvP | -2 | |
| Win streak 3+ | +3/round | Bonus streak |
| Lose streak (có kiểm soát) | +1/round | Streak lợi nhuận |
| **Economy Rewards** | | |
| Đạt ≥50 gold (lãi tối đa) | +2/round | Khuyến khích eco |
| Roll hết gold không hit | -5 | Penalize over-roll |
| **Team Building** | | |
| Up 2★ unit | +10 | |
| Up 3★ unit | +30 | |
| Activate synergy mới | +8 | |
| Build đúng meta comp | +15 | |
| **HP Tracking** | | |
| Mất HP (per point) | -1 | Real-time penalty |
| Còn >70 HP cuối giai đoạn | +5 | Reward HP management |

### Reward Shaping Code

```python
def compute_reward(prev_state: dict, curr_state: dict, result: dict) -> float:
    reward = 0.0
    
    # HP loss penalty
    hp_loss = prev_state["hp"] - curr_state["hp"]
    reward -= hp_loss * 1.0
    
    # Win/lose round
    if result.get("round_win"):
        reward += 5.0
        streak = result.get("win_streak", 0)
        if streak >= 3:
            reward += 3.0
    else:
        reward -= 2.0
    
    # Economy bonus
    if curr_state["gold"] >= 50:
        reward += 2.0
    
    # Unit upgrades
    if result.get("unit_upgraded"):
        star = result["unit_upgraded"]["star"]
        reward += 10.0 if star == 2 else 30.0
    
    # Placement (cuối game)
    if result.get("game_over"):
        placement = result["placement"]
        placement_rewards = {1: 100, 2: 60, 3: 40, 4: 20,
                             5: -10, 6: -25, 7: -40, 8: -60}
        reward += placement_rewards.get(placement, 0)
    
    return reward
```

---

## 8. Training Loop

```python
import time
from collections import deque

def training_loop(env, agent, config):
    """
    Main RL training loop cho TFT AI Agent
    """
    episode_rewards = deque(maxlen=100)
    best_avg_reward = float('-inf')
    
    for episode in range(config["max_episodes"]):
        # Reset môi trường (bắt đầu game mới)
        state = env.reset()
        episode_reward = 0
        done = False
        step = 0
        
        # Bộ nhớ cho PPO update
        states, actions, rewards, log_probs, values = [], [], [], [], []
        
        while not done:
            # 1. Encode state → vector
            state_vec = encode_state(state)
            
            # 2. [Optional] Query LLM cho meta guidance
            if step % 10 == 0:  # Query mỗi 10 bước (tiết kiệm API call)
                llm_hint = query_llm(state)
                state_vec = augment_with_llm_hint(state_vec, llm_hint)
            
            # 3. RL Policy chọn action
            action, log_prob, value = agent.select_action(state_vec)
            
            # 4. Thực thi action trong game
            next_state, reward, done, info = env.step(action)
            
            # 5. Lưu transition
            states.append(state_vec)
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob)
            values.append(value)
            
            episode_reward += reward
            state = next_state
            step += 1
            
            # 6. Update PPO mỗi N steps
            if len(states) >= config["n_steps"]:
                agent.update(states, actions, rewards, log_probs, values)
                states, actions, rewards, log_probs, values = [], [], [], [], []
        
        # Cuối episode: final update nếu còn data
        if states:
            agent.update(states, actions, rewards, log_probs, values)
        
        # Logging
        episode_rewards.append(episode_reward)
        avg_reward = np.mean(episode_rewards)
        
        if episode % 10 == 0:
            print(f"Episode {episode:5d} | "
                  f"Reward: {episode_reward:8.2f} | "
                  f"Avg(100): {avg_reward:8.2f} | "
                  f"Placement: {info.get('placement', '?')}")
        
        # Save checkpoint
        if avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            agent.save(f"checkpoints/best_model.pt")
```

---

## 9. Cơ chế "Tiến hóa" thực sự

AI tiến hóa qua các giai đoạn học:

```
Giai đoạn 1 (Episode 0-500):
━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI học hành động cơ bản:
- Không để hết gold
- Mua unit khi có tiền
- Không bán unit vô cớ
Kết quả: Top 7-8 → Top 5-6

Giai đoạn 2 (Episode 500-2000):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI học kinh tế:
- Giữ gold để ăn lãi
- Biết khi nào cần roll
- Biết level up đúng timing
Kết quả: Top 5-6 → Top 4-5

Giai đoạn 3 (Episode 2000-5000):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI học đội hình:
- Nhận ra synergy tốt
- Ưu tiên up sao core units
- Biết item path
Kết quả: Top 4-5 → Top 3-4

Giai đoạn 4 (Episode 5000+):
━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI học meta-game:
- Scouting board địch
- Chuyển comp linh hoạt
- Positioning theo địch
Kết quả: Top 3-4 → Top 1-2 ổn định
```

---

## 10. Lộ trình phát triển

### Phase 1 — Proof of Concept (2-4 tuần)
**Mục tiêu:** AI có thể chơi được game mà không crash

- [ ] Setup screen capture pipeline
- [ ] OCR basic: đọc gold, level, HP
- [ ] Template matching: nhận diện 10 tướng phổ biến
- [ ] Rule-based agent: mua tướng rẻ, level up đúng lúc
- [ ] Mouse control cơ bản
- [ ] **Milestone:** AI hoàn thành 1 ván full game

### Phase 2 — Imitation Learning (4-6 tuần)
**Mục tiêu:** AI copy hành vi người chơi giỏi

- [ ] Thu thập 1000+ game replays từ Challenger/Master
- [ ] Label hành động: state → action mapping
- [ ] Train Behavior Cloning model
- [ ] Tích hợp LLM Brain với meta guide
- [ ] **Milestone:** AI đạt Top 4 trong 40% ván

### Phase 3 — RL Training (6-8 tuần)
**Mục tiêu:** AI vượt qua imitation learning bằng self-play

- [ ] Implement PPO agent đầy đủ
- [ ] Design reward function chi tiết
- [ ] Training 10,000+ episodes
- [ ] Tune hyperparameters
- [ ] **Milestone:** AI đạt Top 4 trong 60% ván

### Phase 4 — OpenClaw Style Hybrid (8-12 tuần)
**Mục tiêu:** AI đạt trình Challenger

- [ ] Hybrid LLM + RL pipeline hoàn chỉnh
- [ ] Scouting system (đọc board địch)
- [ ] Dynamic comp switching
- [ ] Positioning optimization
- [ ] **Milestone:** Top 4 rate >70%, Top 1 rate >15%

---

## 11. Rủi ro & Giải pháp

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|-----------|
| **Vision sai** → AI nhận nhầm state | Cao | Validation layer, confidence threshold, fallback to last known state |
| **Reward sai** → Học lệch hướng | Rất cao | Extensive reward testing, human evaluation, A/B test reward functions |
| **Action space quá lớn** → Train chậm | Trung bình | Action masking (chặn illegal actions), hierarchical action space |
| **Overfitting meta** → AI không linh hoạt | Trung bình | Randomize comp targets, add exploration noise |
| **API rate limit** (LLM) | Thấp | Cache responses, giảm query frequency |
| **Game patch changes** → Vision fail | Cao | Modular vision system, easy re-training |
| **Anti-cheat detection** | Cao | Chỉ dùng cho local/private server, không dùng trên ranked |

---

## 12. Output kỳ vọng

AI hoàn chỉnh có khả năng:

```
✅ AUTO ROLL hợp lý theo tình huống
   - Roll khi HP thấp (<30)
   - Giữ gold khi đang win streak
   - Hit comp target rồi dừng roll

✅ BUILD ĐỘI HÌNH META
   - Nhận diện 10+ comp phổ biến
   - Flex comp khi không hit main
   - Prioritize augment phù hợp comp

✅ GIỮ KINH TẾ (ECONOMY)
   - Maintain ≥50 gold giai đoạn mid
   - Level up đúng timing
   - Không lãng phí gold

✅ ITEM MANAGEMENT
   - Build item đúng cho carry
   - Holder item khi chờ carry
   - Không để component quá nhiều

✅ KẾT QUẢ MONG ĐỢI
   - Top 4 rate: >65%
   - Top 1 rate: >12%
   - Average placement: ~3.8
```

---

## 13. Stack công nghệ đề xuất

### Core Stack

```
Ngôn ngữ: Python 3.11+

Vision:
├── mss (screen capture)
├── OpenCV 4.8
├── EasyOCR / PaddleOCR
└── YOLOv8 (Ultralytics)

AI/ML:
├── PyTorch 2.0
├── Stable-Baselines3 (PPO)
├── Hugging Face Transformers
└── NumPy / SciPy

LLM Integration:
├── Anthropic Claude API
├── OpenAI GPT-4 API
└── LangChain (orchestration)

Game Control:
├── PyAutoGUI
└── pynput

Monitoring:
├── Weights & Biases (experiment tracking)
├── TensorBoard
└── Loguru (logging)

Infrastructure:
├── Docker
├── CUDA 12.0 (GPU training)
└── Redis (state caching)
```

### Project Structure

```
tft-ai-agent/
├── src/
│   ├── vision/
│   │   ├── screen_capture.py
│   │   ├── ocr_reader.py
│   │   ├── unit_detector.py
│   │   └── state_parser.py
│   ├── encoding/
│   │   ├── state_encoder.py
│   │   └── action_encoder.py
│   ├── brain/
│   │   ├── llm_brain.py
│   │   └── prompt_templates.py
│   ├── rl/
│   │   ├── ppo_agent.py
│   │   ├── policy_network.py
│   │   └── reward_system.py
│   ├── executor/
│   │   ├── action_executor.py
│   │   └── mouse_controller.py
│   └── training/
│       ├── training_loop.py
│       └── evaluator.py
├── data/
│   ├── unit_templates/
│   ├── item_templates/
│   └── replays/
├── checkpoints/
├── configs/
│   └── training_config.yaml
├── tests/
└── README.md
```

---

> 💡 **Ghi chú quan trọng:**
> - Hệ thống này chỉ nên dùng cho **mục đích nghiên cứu, học tập, và môi trường local**.
> - Việc dùng AI agent trên **server ranked chính thức** có thể vi phạm Terms of Service của Riot Games.
> - Recommend test trên **TFT Trainer** hoặc môi trường sandbox.

---

*Document này là bản phác thảo kiến trúc. Chi tiết implementation sẽ được cập nhật theo từng phase.*
