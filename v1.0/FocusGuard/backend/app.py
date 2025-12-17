from flask import Flask, Response, jsonify
from flask_cors import CORS
from core.processor import FocusDetector
import traceback

app = Flask(__name__)
# Allow all origins for development purposes
CORS(app) 

# Global instance of the detector
try:
    focus_detector = FocusDetector()
except Exception as e:
    print(f"Failed to initialize FocusDetector: {e}")
    focus_detector = None

def generate_frames():
    """Generator function that yields video frames."""
    if not focus_detector:
        print("FocusDetector not available. Cannot generate frames.")
        return

    while True:
        try:
            frame = focus_detector.process_frame()
            if frame is None:
                continue
            
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

if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
