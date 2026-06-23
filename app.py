# Main Flask Application

import os
import cv2
import time
import random
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, send_from_directory

app = Flask(__name__)

# Configuration
MOCK_DATASET_DIR = "mock_dataset"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Shared memory/in-memory log database to mimic past incidents
incident_logs = [
    {
        "id": "ALERT-000",
        "timestamp": "2026-06-22 14:32:10",
        "location": "Warehouse Entrance",
        "confidence": "94%",
        "snapshot_url": "/static/uploads/intruder_sample.jpg" # Fallback dummy
    }
]

# Copy a dummy intruder image over for initial rendering if available
if os.path.exists(f"{MOCK_DATASET_DIR}/intruder_sample.jpg"):
    import shutil
    shutil.copy(f"{MOCK_DATASET_DIR}/intruder_sample.jpg", f"{UPLOAD_DIR}/intruder_sample.jpg")


# ==========================================
# 1. THE DUMMY MODEL SECTOR (Swap this later!)
# ==========================================
def dummy_model_inference(frame):
    """
    Simulates a Computer Vision model analyzing a frame.
    Returns: (is_intrusion, confidence_score, bounding_box)
    """
    # 2% chance per frame to trigger an intrusion alert
    is_intrusion = random.choices([True, False], weights=[2, 98])[0]
    
    if is_intrusion:
        confidence = round(random.uniform(0.82, 0.98), 2)
        # Mock normalized coordinates: [ymin, xmin, ymax, xmax] 
        # Relative to a standard 640x480 frame space
        bounding_box = [100, 150, 350, 450] 
        return is_intrusion, confidence, bounding_box
    
    return False, 0.0, []


# ==========================================
# LIVE CCTV STREAM SIMULATOR
# ==========================================
def generate_frames():
    # Simulate video input stream
    video_path = os.path.join(MOCK_DATASET_DIR, "live_stream.mp4")
    
    while True:
        cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else 0) # Fallback to webcam
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break # Loop back to start of video if it ends

            # Pass the frame into our dummy AI engine!
            is_intrusion, confidence, bbox = dummy_model_inference(frame)

            if is_intrusion:
                # 1. Draw a mock red bounding box on the frame overlay
                ymin, xmin, ymax, xmax = bbox
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 3)
                cv2.putText(frame, f"INTRUDER: {int(confidence*100)}%", (xmin, ymin - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # 2. Capture Snapshot & Log Metadata asynchronously
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename = f"snapshot_{int(time.time())}.jpg"
                filepath = os.path.join(UPLOAD_DIR, filename)
                cv2.imwrite(filepath, frame) # Save the alert image frame
                
                # 3. Save to our system's active tracking logs
                incident_logs.insert(0, {
                    "id": f"ALERT-{random.randint(100, 999)}",
                    "timestamp": timestamp,
                    "location": random.choice(["Back Gate", "Warehouse Entrance", "Main Lobby"]),
                    "confidence": f"{int(confidence*100)}%",
                    "snapshot_url": f"/{UPLOAD_DIR}/{filename}"
                })

            # Reduce stream framework processing load slightly to simulate 10 FPS
            time.sleep(0.1)

            # Encode frame to serve over HTTP Multipart protocol
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        cap.release()

# ==========================================
# FLASK WEB ENDPOINTS
# ==========================================
@app.route('/')
def index():
    """Renders main Dashboard UI Interface"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream route for the HTML <img> tag"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for frontend UI to fetch latest incident alerts"""
    return jsonify(incident_logs[:10]) # Limit to last 10 incidents

if __name__ == '__main__':
    app.run(debug=True, port=5000)


"""
- This backend script does three things:

1. Simulates a live stream by reading your sample video frame-by-frame.

2. Runs a dummy model function that randomly triggers an intrusion alert (with a mock bounding box and confidence score).

3. Saves a "snapshot" frame to disk whenever an alert triggers.
"""