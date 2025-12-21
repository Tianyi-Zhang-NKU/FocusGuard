import cv2
import numpy as np
import random


# 这个文件用来模拟 Member A 和 B 的功能
# 等A、B代码写好了，这里就可以删掉了

class MockCamera:
    """模拟摄像头"""

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        success, frame = self.cap.read()
        if success:
            return frame
        else:
            # 如果打不开摄像头，就生成一张黑色的图
            img = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(img, "No Camera", (200, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return img


class MockAlgorithm:
    """模拟算法模块"""

    def analyze(self, frame):
        # 随机生成一些数据来测试前端显示
        ear = round(random.uniform(0.15, 0.45), 2)
        postures = ["Normal", "Hunchback", "Leaning"]  # 正常，驼背，侧倾
        posture = random.choice(postures)

        # 简单的在图上写个字
        img = frame.copy()
        color = (0, 255, 0) if posture == "Normal" else (0, 0, 255)
        cv2.putText(img, f"Status: {posture}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        return {
            "frame": img,
            "data": {
                "posture": posture,
                "fatigue": ear,
                "is_alert": ear < 0.20  # 假设小于0.2就是疲劳
            }
        }