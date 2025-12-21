# backend/core/detector.py
import mediapipe as mp
import cv2

class MPDetector:
    def __init__(self, enable_pose=True, enable_face=True, enable_hands=False):
        self.enable_pose = enable_pose
        self.enable_face = enable_face
        self.enable_hands = enable_hands

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.mp_face = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands

        if self.enable_pose:
            self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.pose = None

        if self.enable_face:
            self.face = self.mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
        else:
            self.face = None

        if self.enable_hands:
            self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        else:
            self.hands = None

    def _landmark_list(self, lm_list, shape):
        h, w = shape[:2]
        out = []
        for l in lm_list:
            out.append({'x': float(l.x * w), 'y': float(l.y * h), 'z': float(getattr(l, 'z', 0.0) * w)})
        return out

    def detect(self, frame_bgr):
        """
        Input: BGR frame (numpy array)
        Output: dict with keys 'pose','face','hands'
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = {'pose': None, 'face': None, 'hands': []}

        if self.pose:
            res_pose = self.pose.process(frame_rgb)
            if res_pose.pose_landmarks:
                results['pose'] = {'landmarks': self._landmark_list(res_pose.pose_landmarks.landmark, frame_bgr.shape)}

        if self.face:
            res_face = self.face.process(frame_rgb)
            if res_face.multi_face_landmarks and len(res_face.multi_face_landmarks) > 0:
                results['face'] = {'landmarks': self._landmark_list(res_face.multi_face_landmarks[0].landmark, frame_bgr.shape)}

        if self.hands:
            res_hands = self.hands.process(frame_rgb)
            if res_hands.multi_hand_landmarks:
                for hand_lm in res_hands.multi_hand_landmarks:
                    results['hands'].append({'landmarks': self._landmark_list(hand_lm.landmark, frame_bgr.shape)})

        return results
