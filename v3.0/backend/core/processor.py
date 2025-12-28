import cv2
import time
import numpy as np
import mediapipe as mp
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import math

class FocusDetector:
    def __init__(self, camera_index=0):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1)
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

        self.status = {
            "posture_status": "未检测到",
            "fatigue_status": "未检测到",
            "distance_warning": False,
            "fps": 0,
            "timestamp": datetime.now().isoformat(),
            "spine_angle": 0,
            "head_angle": 0,
            # New fields for linear scores
            "posture_score": 0,
            "focus_score": 0
        }
        self.frame_count = 0
        self.start_time = time.time()
        self.fatigue_frames = 0
        self.FATIGUE_THRESHOLD = 8 
        
        self.yawn_counter = 0
        self.YAWN_THRESH = 0.5
        self.YAWN_FRAMES = 10
        self.DIST_THRESH = 0.5 

        # Smoothing variables
        self.score_posture = 100.0
        self.score_focus = 100.0
        self.ALPHA = 0.1 # Smoothing factor

    @staticmethod
    def calculate_angle(a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    @staticmethod
    def calculate_ear(eye):
        p1, p2, p3, p4, p5, p6 = [np.array([coord.x, coord.y]) for coord in eye]
        a = np.linalg.norm(p2 - p6)
        b = np.linalg.norm(p3 - p5)
        c = np.linalg.norm(p1 - p4)
        ear = (a + b) / (2.0 * c)
        return ear

    @staticmethod
    def calculate_vertical_angle(p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)
        v = p2 - p1
        v_up = np.array([0, -1])
        dot_product = np.dot(v, v_up)
        mag_v = np.linalg.norm(v)
        mag_v_up = np.linalg.norm(v_up)
        if mag_v == 0 or mag_v_up == 0: return 0
        cos_theta = dot_product / (mag_v * mag_v_up)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)
        angle_deg = np.degrees(angle_rad)
        if v[0] < 0: angle_deg *= -1
        return angle_deg

    def _calculate_mar(self, face_landmarks, image_shape):
        h, w = image_shape[:2]
        p13 = np.array([face_landmarks[13].x * w, face_landmarks[13].y * h])
        p14 = np.array([face_landmarks[14].x * w, face_landmarks[14].y * h])
        p61 = np.array([face_landmarks[61].x * w, face_landmarks[61].y * h])
        p291 = np.array([face_landmarks[291].x * w, face_landmarks[291].y * h])
        A = np.linalg.norm(p13 - p14)
        B = np.linalg.norm(p61 - p291)
        if B == 0: return 0
        return A / B

    def _estimate_distance_ratio(self, face_landmarks):
        p33_x = face_landmarks[33].x
        p263_x = face_landmarks[263].x
        return abs(p33_x - p263_x)

    def process_frame(self):
        success, image = self.cap.read()
        if not success: return None

        # --- 0. Ambient Light Detection (Moved to start) ---
        try:
            # Calculate brightness directly from the BGR image
            # Make sure to work on a copy or ensure cvtColor doesn't affect subsequent steps if writeable is changed later
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            avg_brightness = np.mean(hsv_image[:, :, 2])
            self.status['brightness_value'] = int(avg_brightness)
            self.status['lighting_warning'] = bool(avg_brightness < 60)  # Threshold = 60, convert to native bool
        except Exception as e:
            print(f"Error calculating brightness: {e}")
            self.status['brightness_value'] = 0
            self.status['lighting_warning'] = False

        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.status['fps'] = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        pose_results = self.pose.process(image_rgb)
        face_results = self.face_mesh.process(image_rgb)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = image.shape

        # --- 1. Linear Posture Scoring ---
        target_posture = 0
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            left_ear = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]

            shoulder_midpoint = ((left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2)
            hip_midpoint = ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)

            self.status['spine_angle'] = self.calculate_vertical_angle(hip_midpoint, shoulder_midpoint)
            self.status['head_angle'] = self.calculate_vertical_angle(shoulder_midpoint, left_ear)

            # Formula: 100 - penalties based on angles
            spine_penalty = max(0, abs(self.status['spine_angle']) - 5) * 2  # Tolerate 5 degrees
            head_penalty = max(0, abs(self.status['head_angle']) - 8) * 1.5 # Tolerate 8 degrees
            
            target_posture = max(0, 100 - (spine_penalty + head_penalty))
            
            # Draw skeleton
            self.mp_drawing.draw_landmarks(image, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        else:
            target_posture = 0 # No person detected

        # Apply smoothing
        self.score_posture = self.score_posture * (1 - self.ALPHA) + target_posture * self.ALPHA
        self.status['posture_score'] = int(self.score_posture)

        # Set status string based on score
        if self.status['posture_score'] < 70:
             self.status["posture_status"] = "姿态不佳"
        else:
            self.status["posture_status"] = "姿态良好"


        # --- 2. Linear Focus Scoring ---
        target_focus = 100
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                left_eye = [landmarks[i] for i in [33, 160, 158, 133, 153, 144]]
                right_eye = [landmarks[i] for i in [362, 385, 387, 263, 373, 380]]
                ear_left = self.calculate_ear(left_eye)
                ear_right = self.calculate_ear(right_eye)
                avg_ear = (ear_left + ear_right) / 2.0
                mar = self._calculate_mar(landmarks, image.shape)
                dist_ratio = self._estimate_distance_ratio(landmarks)

                # Penalties
                penalty = 0
                
                # Eye closure penalty
                if avg_ear < 0.28: 
                    penalty += 40
                elif avg_ear < 0.32: # Drowsy eyes
                    penalty += 15
                
                # Yawning penalty
                if mar > self.YAWN_THRESH:
                    penalty += 60
                
                target_focus = max(0, 100 - penalty)

                # Update Fatigue Frames for status string logic
                if avg_ear < 0.25: self.fatigue_frames += 1
                else: self.fatigue_frames = 0
                
                if mar > self.YAWN_THRESH: self.yawn_counter += 1
                else: self.yawn_counter = 0

                # Determine Status String
                if self.fatigue_frames >= self.FATIGUE_THRESHOLD:
                    self.status["fatigue_status"] = "疲劳/困倦"
                elif self.yawn_counter > self.YAWN_FRAMES:
                    self.status["fatigue_status"] = "打哈欠(疲劳)"
                else:
                    self.status["fatigue_status"] = "清醒"

                # Distance Warning
                if dist_ratio > self.DIST_THRESH:
                    self.status["distance_warning"] = True
                    cv2.rectangle(image, (0, 0), (w, h), (0, 0, 255), 10)
                else:
                    self.status["distance_warning"] = False
        else:
            target_focus = 0 # No face
            self.status["fatigue_status"] = "未检测到"
            self.status["distance_warning"] = False

        # Apply smoothing to focus score (slower recovery)
        self.score_focus = self.score_focus * (1 - self.ALPHA) + target_focus * self.ALPHA
        self.status['focus_score'] = int(self.score_focus)


        # --- 3. Draw Warnings ---
        if (self.status["posture_status"] == "姿态不佳" or 
            self.status["fatigue_status"] in ["疲劳/困倦", "打哈欠(疲劳)"] or
            self.status["distance_warning"]):
            
            img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            try:
                font = ImageFont.truetype("simhei.ttf", 30)
                font_large = ImageFont.truetype("simhei.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
                font_large = ImageFont.load_default()

            warning_text = ""
            if self.status["posture_status"] == "姿态不佳":
                warning_text += "坐姿不规范！ "
            if self.status["fatigue_status"] == "疲劳/困倦":
                warning_text += "感到困倦？"
            if self.status["fatigue_status"] == "打哈欠(疲劳)":
                warning_text += "正在打哈欠 "
            
            draw.text((50, 50), warning_text, font=font, fill=(255, 0, 0))
            
            if self.status["distance_warning"]:
                dist_text = "距离屏幕太近！"
                text_width = len(dist_text) * 40 
                draw.text(((w - text_width)//2, h//2), dist_text, font=font_large, fill=(255, 0, 0))
            
            image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        self.status["timestamp"] = datetime.now().isoformat()
        
        ret, buffer = cv2.imencode('.jpg', image)
        if not ret: return None
        frame = buffer.tobytes()
        return frame

    def release(self):
        self.cap.release()
        self.pose.close()
        self.face_mesh.close()

if __name__ == '__main__':
    detector = FocusDetector()
    while True:
        frame = detector.process_frame()
        if frame is None: break
        print(f"Posture: {detector.status['posture_score']} | Focus: {detector.status['focus_score']}")
    detector.release()
