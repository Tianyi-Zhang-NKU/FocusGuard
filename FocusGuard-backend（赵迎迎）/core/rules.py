import time
from collections import deque
from .geometry import angle_between, eye_aspect_ratio, distance

# ================== 参数区 ==================
MIN_INTERVAL = 0.1            # 更新频率
WINDOW_SIZE = 30              # ≈3 秒窗口
FATIGUE_WINDOW = 90           # ≈9 秒窗口

BLINK_EAR_THRESH = 0.18
CONSEC_FRAMES_BLINK = 3       # 连续低EAR帧判定眨眼

GOOD_SPINE_ANGLE = 70
GOOD_HEAD_ANGLE = 15
NEAR_FACE_AREA = 10000
NEAR_EYE_DIST = 50             # 眼间距阈值

NORMAL_BLINK_RATE = 20        # 次 / 分钟
FATIGUE_BLINK_RATE = 30

EMA_ALPHA = 0.4               # EAR 平滑系数

# ================== 全局状态 ==================
_last_update_ts = 0
ema_ear = None                 # EMA EAR
low_ear_frames = 0             # 连续低EAR帧计数

ear_history = deque(maxlen=WINDOW_SIZE)
posture_history = deque(maxlen=WINDOW_SIZE)
distance_history = deque(maxlen=WINDOW_SIZE)

blink_timestamps = deque(maxlen=FATIGUE_WINDOW)
ear_long_term = deque(maxlen=FATIGUE_WINDOW)

# ================== 工具函数 ==================
def midpoint(a, b):
    return {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}

def compute_attention_score(posture_h, distance_h, ear_h):
    score = 100
    def penalty(hist, weight):
        bad = hist.count(False)
        return int((bad / max(len(hist), 1))**1.2 * weight)  # 非线性惩罚
    score -= penalty(posture_h, 30)
    score -= penalty(distance_h, 25)
    score -= penalty(ear_h, 45)
    return max(0, min(100, score))

# ================== 疲劳模块 ==================
def compute_fatigue():
    now = time.time()
    # 最近 60s 眨眼次数
    recent_blinks = [t for t in blink_timestamps if now - t <= 60]
    blink_rate = len(recent_blinks)
    # EAR 平均
    avg_ear = sum(ear_long_term) / max(len(ear_long_term), 1)
    score = 0
    # 眨眼频率评分
    if blink_rate > FATIGUE_BLINK_RATE:
        score += 40
    elif blink_rate > NORMAL_BLINK_RATE:
        score += 20
    # EAR 低值评分
    if avg_ear < 0.20:
        score += 40
    elif avg_ear < 0.22:
        score += 20
    # 闭眼持续时间
    global low_ear_frames
    if low_ear_frames >= CONSEC_FRAMES_BLINK * 3:
        score = min(score + 10, 100)
    score = min(score, 100)
    level = (
        "alert" if score < 30 else
        "mild" if score < 60 else
        "severe"
    )
    return score, level, {"blink_rate": blink_rate, "avg_ear": round(avg_ear,3), "low_ear_frames": low_ear_frames}

# ================== 主函数 ==================
def evaluate_posture(detections):
    global _last_update_ts, ema_ear, low_ear_frames

    now = time.time()
    if now - _last_update_ts < MIN_INTERVAL:
        return None
    _last_update_ts = now

    details = {}
    pose = detections.get("pose")
    face = detections.get("face")

    # ---------------- 姿态 ----------------
    spine_ok = False
    posture = "unknown"
    if pose and "landmarks" in pose:
        try:
            lms = pose["landmarks"]
            mid_sh = midpoint(lms[11], lms[12])
            mid_hip = midpoint(lms[23], lms[24])
            nose = lms[0]
            # 头部偏离角度
            left_ear = lms[7]
            right_ear = lms[8]
            spine_angle = angle_between(mid_hip, mid_sh, nose)
            head_angle = angle_between(left_ear, nose, right_ear)
            spine_score = 0.7 * spine_angle + 0.3 * (180 - head_angle)
            spine_ok = spine_score >= GOOD_SPINE_ANGLE
            posture = "ok" if spine_ok else "slouch"
            details["spine_angle"] = round(spine_angle, 1)
            details["head_angle"] = round(head_angle, 1)
        except Exception:
            pass
    posture_history.append(spine_ok)

    # ---------------- 距离 ----------------
    distance_ok = True
    distance_status = "unknown"
    if face and "landmarks" in face:
        try:
            xs = [p["x"] for p in face["landmarks"]]
            ys = [p["y"] for p in face["landmarks"]]
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            # 双眼间距
            left_eye = face["landmarks"][33]
            right_eye = face["landmarks"][263]
            eye_dist = distance(left_eye, right_eye)
            distance_ok = area < NEAR_FACE_AREA and eye_dist > NEAR_EYE_DIST
            distance_status = "normal" if distance_ok else "too_close"
            details["face_area"] = int(area)
            details["eye_dist"] = round(eye_dist, 1)
        except Exception:
            pass
    distance_history.append(distance_ok)

    # ---------------- 眼睛 & 眨眼 ----------------
    avoid_blink = False
    ear_frame = None
    if face and "landmarks" in face:
        try:
            left_eye_idx = [33,160,158,133,153,144]
            right_eye_idx = [362,385,387,263,373,380]
            left_eye = [face["landmarks"][i] for i in left_eye_idx]
            right_eye = [face["landmarks"][i] for i in right_eye_idx]

            ear_instant = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2
            # EMA 平滑
            if ema_ear is None:
                ema_ear = ear_instant
            else:
                ema_ear = EMA_ALPHA * ear_instant + (1 - EMA_ALPHA) * ema_ear

            ear_long_term.append(ema_ear)
            details["ear"] = round(ema_ear, 3)

            # 连续低EAR帧判定眨眼
            if ema_ear < BLINK_EAR_THRESH:
                low_ear_frames += 1
            else:
                if low_ear_frames >= CONSEC_FRAMES_BLINK:
                    blink_timestamps.append(time.time())
                low_ear_frames = 0
            avoid_blink = ema_ear < BLINK_EAR_THRESH
        except Exception:
            pass
    ear_history.append(not avoid_blink)

    # ---------------- 专注度 ----------------
    attention_score = compute_attention_score(posture_history, distance_history, ear_history)
    attention = (
        "focused" if attention_score >= 75 else
        "normal" if attention_score >= 50 else
        "distracted"
    )

    # ---------------- 疲劳 ----------------
    fatigue_score, fatigue_level, fatigue_details = compute_fatigue()
    details.update(fatigue_details)

    return {
        "posture": posture,
        "distance": distance_status,
        "attention": attention,
        "attention_score": attention_score,
        "fatigue": fatigue_level,
        "fatigue_score": fatigue_score,
        "details": details
    }
