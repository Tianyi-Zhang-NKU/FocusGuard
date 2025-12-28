from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from core.processor import FocusDetector
import traceback
import database
import config
import time
from datetime import datetime

app = Flask(__name__)
# Allow all origins for development purposes
CORS(app) 

# Initialize Database
database.init_db()

# Global instance of the detector
try:
    focus_detector = FocusDetector()
except Exception as e:
    print(f"Failed to initialize FocusDetector: {e}")
    focus_detector = None

def generate_frames():
    """Generator function that yields video frames and saves logs."""
    if not focus_detector:
        print("FocusDetector not available. Cannot generate frames.")
        return

    last_save_time = time.time()

    while True:
        try:
            frame = focus_detector.process_frame()
            if frame is None:
                continue
            
            # Auto-save logic (Every SAVE_INTERVAL seconds)
            now = time.time()
            if now - last_save_time > config.SAVE_INTERVAL:
                # Get current status
                status = focus_detector.status
                # Determine if alert (bad posture or fatigue)
                is_alert = (status["posture_status"] == "姿态不佳") or (status["fatigue_status"] == "疲劳/困倦")
                
                # Save to DB (Default user 'admin' for now, can be enhanced)
                database.add_log(
                    "admin", 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status["posture_status"],
                    status.get("fatigue_status", "未知"), # Safe get
                    is_alert
                )
                print(f"Log saved at {datetime.now().strftime('%H:%M:%S')}")
                last_save_time = now

            # Yield the frame in the multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error generating frame: {e}")
            traceback.print_exc()
            # If the camera fails, we might want to stop the loop
            break

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    if not focus_detector:
        return "Error: Camera or FocusDetector not available.", 503
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    """API endpoint to get the current status."""
    if not focus_detector:
        return jsonify({
            "error": "FocusDetector not initialized.",
            "posture_status": "Unknown",
            "fatigue_status": "Unknown",
            "fps": 0,
            "timestamp": "N/A"
        }), 503
    return jsonify(focus_detector.status)

# === New Database API Endpoints ===

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "账号密码不能为空"}), 400

    success, msg = database.add_user(data['username'], data['password'])
    if success:
        return jsonify({"code": 200, "msg": msg})
    else:
        return jsonify({"code": 409, "msg": msg}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "请输入账号密码"}), 400

    success, msg = database.check_login(data['username'], data['password'])
    if success:
        return jsonify({"code": 200, "msg": msg, "user": data['username']})
    else:
        return jsonify({"code": 401, "msg": msg}), 401

@app.route('/api/history', methods=['GET'])
def get_history():
    # In a real app, get username from session/token. 
    # Here we default to 'admin' or query param for simplicity
    username = request.args.get('username', 'admin') 
    data = database.get_logs(username)
    return jsonify(data)

if __name__ == '__main__':
    try:
        print("Starting FocusGuard Backend Server...")
        # The host='0.0.0.0' makes the server accessible from other devices on the network
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
    except Exception as e:
        print(f"CRITICAL ERROR STARTING SERVER: {e}")
        traceback.print_exc()
    input("Press Enter to exit...")
