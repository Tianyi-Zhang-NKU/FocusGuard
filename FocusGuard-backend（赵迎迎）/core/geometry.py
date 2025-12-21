# backend/core/geometry.py
import math

def distance(p1, p2):
    return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

def vector(a, b):
    return (b['x'] - a['x'], b['y'] - a['y'])

def angle_between(a, b, c):
    """
    angle at b formed by points a-b-c, return degrees
    """
    ab = vector(b, a)
    cb = vector(b, c)
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    mag_ab = math.hypot(ab[0], ab[1])
    mag_cb = math.hypot(cb[0], cb[1])
    if mag_ab*mag_cb == 0:
        return 0.0
    cosv = max(-1.0, min(1.0, dot / (mag_ab*mag_cb)))
    return math.degrees(math.acos(cosv))

def eye_aspect_ratio(eye_landmarks):
    """
    eye_landmarks: list of 6 points (x,y)
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    expects dicts with x,y
    """
    if len(eye_landmarks) < 6:
        return 0.0
    p1, p2, p3, p4, p5, p6 = eye_landmarks[:6]
    a = distance(p2, p6)
    b = distance(p3, p5)
    c = distance(p1, p4)
    if c == 0:
        return 0.0
    return (a + b) / (2.0 * c)