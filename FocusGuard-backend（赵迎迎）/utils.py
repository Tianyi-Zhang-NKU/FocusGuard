# backend/utils.py
import cv2
import base64
import json

def frame_to_jpeg_bytes(frame, quality=80):
    ret, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ret:
        return None
    return buf.tobytes()

def frame_to_base64(frame, quality=80):
    b = frame_to_jpeg_bytes(frame, quality=quality)
    if not b:
        return None
    return "data:image/jpeg;base64," + base64.b64encode(b).decode('utf-8')

def to_json(obj):
    return json.dumps(obj, ensure_ascii=False)
