import cv2
import time
import numpy as np
import mediapipe as mp
from datetime import datetime

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
            "fps": 0,
            "timestamp": datetime.now().isoformat(),
            "spine_angle": 0,
            "head_angle": 0,
        }
        self.frame_count = 0
        self.start_time = time.time()
        self.fatigue_frames = 0
        self.FATIGUE_THRESHOLD = 8 # Lowered for more sensitivity

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
        # Vertical eye landmarks
        a = np.linalg.norm(p2 - p6)
        b = np.linalg.norm(p3 - p5)
        # Horizontal eye landmark
        c = np.linalg.norm(p1 - p4)
        # Eye Aspect Ratio
        ear = (a + b) / (2.0 * c)
        return ear

    @staticmethod
    def calculate_vertical_angle(p1, p2):
        """Calculates the angle of the vector p1->p2 with the upward vertical axis."""
        p1 = np.array(p1)
        p2 = np.array(p2)
        v = p2 - p1
        # Vector representing the upward vertical direction
        v_up = np.array([0, -1])
        
        # Calculate the angle using dot product
        dot_product = np.dot(v, v_up)
        mag_v = np.linalg.norm(v)
        mag_v_up = np.linalg.norm(v_up)
        
        if mag_v == 0 or mag_v_up == 0:
            return 0

        cos_theta = dot_product / (mag_v * mag_v_up)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        
        angle_rad = np.arccos(cos_theta)
        angle_deg = np.degrees(angle_rad)

        # Determine the sign of the angle (left or right lean)
        if v[0] < 0:
            angle_deg *= -1
            
        return angle_deg

    def process_frame(self):
        success, image = self.cap.read()
        if not success:
            return None

        # Performance measurement
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

        # Posture and Angle Detection
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

            if abs(self.status['spine_angle']) > 15 or abs(self.status['head_angle']) > 20:
                 self.status["posture_status"] = "姿态不佳"
            else:
                self.status["posture_status"] = "姿态良好"

            self.mp_drawing.draw_landmarks(
                image, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        else:
            self.status["posture_status"] = "未检测到"
            self.status["spine_angle"] = 0
            self.status["head_angle"] = 0

        # Fatigue Detection
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                left_eye = [landmarks[i] for i in [33, 160, 158, 133, 153, 144]]
                right_eye = [landmarks[i] for i in [362, 385, 387, 263, 373, 380]]

                ear_left = self.calculate_ear(left_eye)
                ear_right = self.calculate_ear(right_eye)
                avg_ear = (ear_left + ear_right) / 2.0

                if avg_ear < 0.25:
                    self.fatigue_frames += 1
                else:
                    self.fatigue_frames = 0
                    self.status["fatigue_status"] = "清醒"
                
                if self.fatigue_frames >= self.FATIGUE_THRESHOLD:
                    self.status["fatigue_status"] = "疲劳/困倦"
        else:
            self.status["fatigue_status"] = "未检测到"

        # Display Status
        if self.status["posture_status"] == "姿态不佳" or self.status["fatigue_status"] == "疲劳/困倦":
            warning_text = ""
            if self.status["posture_status"] == "姿态不佳":
                warning_text += "姿态不佳！ "
            if self.status["fatigue_status"] == "疲劳/困倦":
                warning_text += "感到困倦？"
            
            cv2.putText(image, warning_text, (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        self.status["timestamp"] = datetime.now().isoformat()
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', image)
        if not ret:
            return None
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
        if frame is None:
            break
        
        print(detector.status)

        # cv2.imshow('FocusGuard', cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR))
        # if cv2.waitKey(5) & 0xFF == 27:
        #     break

    detector.release()
