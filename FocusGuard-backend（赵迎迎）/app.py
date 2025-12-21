# backend/app.py
import time
import threading
from flask import Flask, jsonify, Response, send_from_directory
from flask_cors import CORS

from camera import Camera
from core.detector import MPDetector
from core.rules import evaluate_posture
from utils import frame_to_jpeg_bytes

app = Flask(__name__)
CORS(app)

# ---------------- 单例 ----------------

camera = Camera(src=0)
detector = MPDetector(
    enable_pose=True,
    enable_face=True,
    enable_hands=False
)

processing = {
    "running": False,
    "last_status": None
}

processing_thread = None

# ---------------- 处理线程 ----------------

def processing_loop():
    print("🧠 Processing thread started")
    while processing["running"]:
        frame = camera.read()
        if frame is None:
            time.sleep(0.05)
            continue

        detections = detector.detect(frame)
        status = evaluate_posture(detections)

        # ⭐⭐⭐ 关键新增：防 None ⭐⭐⭐
        if status is None:
            time.sleep(0.05)
            continue

        status["ts"] = time.time()
        processing["last_status"] = status

        time.sleep(0.05)

    print("🧠 Processing thread stopped")

# ---------------- 前端页面 ----------------

@app.route("/")
def index():
    return send_from_directory(".", "start.html")

# ---------------- API ----------------

@app.route("/api/test")
def api_test():
    return jsonify({"ok": True})

@app.route("/start", methods=["POST"])
def start():
    global processing_thread

    if not camera.running:
        camera.start()

    if not processing["running"]:
        processing["running"] = True
        processing_thread = threading.Thread(
            target=processing_loop,
            daemon=True
        )
        processing_thread.start()

    return jsonify({"ok": True, "msg": "started"})

@app.route("/stop", methods=["POST"])
def stop():
    processing["running"] = False
    camera.stop()
    return jsonify({"ok": True, "msg": "stopped"})

@app.route("/status")
def status():
    if processing["last_status"] is None:
        return jsonify({"ok": False, "reason": "no_data"})
    return jsonify(processing["last_status"])

@app.route("/frame.jpg")
def frame():
    frame = camera.read()
    if frame is None:
        return Response(status=204)
    return Response(
        frame_to_jpeg_bytes(frame),
        mimetype="image/jpeg"
    )
