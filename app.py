"""
1. AT THE TOP OF THE FILE:
from ultralytics import YOLO  # Import your framework of choice (e.g., YOLOv8)


2. IN THE INITIALIZATION SECTOR:
model = YOLO("your_trained_weights.pt")  # Replace mock_model_inference completely

3. INTERNALLY UPDATE THE LOGIC:
Replace the contents of dummy_model_inference(frame) with:
results = model(frame)
Extract actual class IDs, coordinates (results[0].boxes.xyxy), and certainty bounds dynamically.


Flask Dashboard Application
Intrusion Detection System (IDS)

Responsibilities:
1. Dashboard UI
2. Alert History API
3. Owner Response Endpoint
4. Police Contact Lookup
5. Snapshot Access
"""

import os
import psycopg2
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    jsonify,
    request
)

# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

# ==================================================
# FLASK APP
# ==================================================

app = Flask(__name__)

# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432")
}

# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():
    """
    Create PostgreSQL connection.
    """
    return psycopg2.connect(**DB_CONFIG)

# ==================================================
# POLICE CONTACT DATABASE
# ==================================================

POLICE_CONTACTS = {
    "Warehouse Main Entrance": {
        "station": "Local Police Station",
        "phone": "+8801000000000"
    },

    "Back Gate": {
        "station": "Back Gate Police Station",
        "phone": "+8801111111111"
    },

    "Warehouse Entrance": {
        "station": "Warehouse Police Station",
        "phone": "+8801222222222"
    },

    "Main Lobby": {
        "station": "Main Lobby Police Station",
        "phone": "+8801333333333"
    }
}

# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def dashboard():
    """
    Main Dashboard UI
    """
    return render_template("dashboard.html")

# ==================================================
# GET LATEST ALERTS
# ==================================================

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """
    Return latest intrusion alerts.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                timestamp,
                location,
                confidence,
                snapshot_path
            FROM intrusion_logs
            ORDER BY timestamp DESC
            LIMIT 20;
        """)

        rows = cursor.fetchall()

        alerts = []

        for row in rows:
            alerts.append({
                "id": row[0],
                "timestamp": str(row[1]),
                "location": row[2],
                "confidence": round(float(row[3]) * 100, 2),
                "snapshot_path": row[4]
            })

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "alerts": alerts
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================================================
# OWNER RESPONSE ENDPOINT
# ==================================================

@app.route("/api/response", methods=["GET"])
def owner_response():
    """
    Email button endpoint.

    Example:
    /api/response?status=yes&location=Back Gate
    """

    status = request.args.get("status")
    location = request.args.get("location")

    if not status:
        return jsonify({
            "success": False,
            "message": "Status missing."
        }), 400

    # -----------------------------------------
    # THREAT CONFIRMED
    # -----------------------------------------

    if status.lower() == "yes":

        police_info = POLICE_CONTACTS.get(
            location,
            {
                "station": "Nearest Police Station",
                "phone": "999"
            }
        )

        return jsonify({
            "success": True,
            "message": "Threat confirmed by owner.",
            "police_station": police_info["station"],
            "police_phone": police_info["phone"]
        })

    # -----------------------------------------
    # FALSE ALARM
    # -----------------------------------------

    elif status.lower() == "no":

        return jsonify({
            "success": True,
            "message": "Incident marked as false alarm."
        })

    return jsonify({
        "success": False,
        "message": "Invalid status."
    }), 400

# ==================================================
# POLICE LOOKUP API
# ==================================================

@app.route("/api/police/<location>", methods=["GET"])
def get_police(location):
    """
    Get police information based on camera location.
    """

    police = POLICE_CONTACTS.get(location)

    if not police:
        return jsonify({
            "success": False,
            "message": "Police information not found."
        }), 404

    return jsonify({
        "success": True,
        "location": location,
        "station": police["station"],
        "phone": police["phone"]
    })

# ==================================================
# SYSTEM HEALTH CHECK
# ==================================================

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health monitoring endpoint.
    """

    try:
        conn = get_db_connection()
        conn.close()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": str(e)
        }), 500

# ==================================================
# APPLICATION ENTRY
# ==================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


"""
- This backend script does three things:

1. Simulates a live stream by reading your sample video frame-by-frame.

2. Runs a dummy model function that randomly triggers an intrusion alert (with a mock bounding box and confidence score).

3. Saves a "snapshot" frame to disk whenever an alert triggers.
"""

# Install dependencies: pip install flask opencv-python

# If You Later Swap In the Real Model
"""
When you replace dummy_model_inference() with an actual YOLO model (as noted in your comments), you'll also need:

pip install ultralytics

That will pull in PyTorch and everything YOLOv8 needs.
"""
# Run the application: python app.py

# Open your web browser and go to http://127.0.0.1:5000/