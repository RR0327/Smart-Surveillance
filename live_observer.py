"""
live_observer.py

Continuous AI Observer
---------------------------------
Responsibilities:
1. Connect to RTSP / Webcam
2. Run YOLO Detection
3. Capture Snapshots
4. Store Events in PostgreSQL
5. Send Email Alerts
6. Prevent Alert Spam
"""

import cv2
import os
import time
import threading
import logging
import smtplib
import psycopg2

from datetime import datetime
from ultralytics import YOLO

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from config import (
    DB_CONFIG,
    EMAIL_CONFIG,
    CONFIDENCE_THRESHOLD,
    ALERT_COOLDOWN,
    BASE_URL,
    SNAPSHOT_DIR,
    DEFAULT_CAMERA_LOCATION
)

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==================================================
# GLOBAL ALERT TRACKER
# ==================================================

last_alert_time = 0


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():
    """
    Create PostgreSQL connection.
    """
    return psycopg2.connect(**DB_CONFIG)


# ==================================================
# AFTER HOURS LOGIC
# ==================================================

def is_after_hours():
    """
    Define business hours.

    Example:
    Open: 8 AM
    Close: 10 PM

    Intrusion if detected outside.
    """

    current_hour = datetime.now().hour

    if current_hour < 8 or current_hour >= 22:
        return True

    return False


# ==================================================
# EMAIL ALERT FUNCTION
# ==================================================

def send_smtp_alert(timestamp, location, image_path):
    """
    Send intrusion email alert.
    """

    try:

        msg = MIMEMultipart()

        msg["From"] = EMAIL_CONFIG["sender_email"]
        msg["To"] = EMAIL_CONFIG["receiver_email"]

        msg["Subject"] = (
            f"🚨 Intrusion Detected - {location}"
        )

        body = f"""
        <h2>Security Alert</h2>

        <p>
        An intrusion has been detected.
        </p>

        <ul>
            <li><b>Location:</b> {location}</li>
            <li><b>Time:</b> {timestamp}</li>
        </ul>

        <hr>

        <p>
        Is this an active threat?
        </p>

        <a href="{BASE_URL}/api/response?status=yes&location={location}"
           style="
           background:red;
           color:white;
           padding:10px 20px;
           text-decoration:none;
           border-radius:5px;">
           YES - Call Police
        </a>

        &nbsp;&nbsp;

        <a href="{BASE_URL}/api/response?status=no"
           style="
           background:green;
           color:white;
           padding:10px 20px;
           text-decoration:none;
           border-radius:5px;">
           NO - False Alarm
        </a>
        """

        msg.attach(MIMEText(body, "html"))

        with open(image_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(image_path)
            )

            msg.attach(img)

        server = smtplib.SMTP(
            EMAIL_CONFIG["smtp_server"],
            EMAIL_CONFIG["smtp_port"]
        )

        server.starttls()

        server.login(
            EMAIL_CONFIG["sender_email"],
            EMAIL_CONFIG["app_password"]
        )

        server.send_message(msg)

        server.quit()

        logging.info(
            "Email alert sent successfully."
        )

    except Exception as e:
        logging.error(
            f"Email sending failed: {e}"
        )


# ==================================================
# SAVE EVENT TO DATABASE
# ==================================================

def save_intrusion_event(
    timestamp,
    location,
    confidence,
    image_path
):
    """
    Save intrusion to PostgreSQL.
    """

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        query = """
        INSERT INTO intrusion_logs
        (
            timestamp,
            location,
            confidence,
            snapshot_path
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        );
        """

        cursor.execute(
            query,
            (
                timestamp,
                location,
                confidence,
                image_path
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        logging.info(
            "Intrusion saved to database."
        )

    except Exception as e:

        logging.error(
            f"Database error: {e}"
        )


# ==================================================
# MAIN OBSERVER
# ==================================================

def start_live_observer(
    model_path,
    source_rtsp,
    camera_location=DEFAULT_CAMERA_LOCATION
):
    """
    Start AI monitoring.
    """

    global last_alert_time

    logging.info(
        f"Loading YOLO model: {model_path}"
    )

    model = YOLO(model_path)

    os.makedirs(
        SNAPSHOT_DIR,
        exist_ok=True
    )

    cap = cv2.VideoCapture(source_rtsp)

    if not cap.isOpened():

        logging.error(
            "Unable to connect to camera."
        )

        return

    logging.info(
        "Camera stream connected."
    )

    while True:

        ret, frame = cap.read()

        if not ret:

            logging.warning(
                "Camera disconnected. Reconnecting..."
            )

            cap.release()

            time.sleep(2)

            cap = cv2.VideoCapture(
                source_rtsp
            )

            continue

        try:

            results = model(
                frame,
                verbose=False
            )[0]

            for box in results.boxes:

                conf = float(box.conf[0])

                cls = int(box.cls[0])

                # COCO person class = 0
                if (
                    cls == 0
                    and conf >= CONFIDENCE_THRESHOLD
                    and is_after_hours()
                ):

                    current_time = time.time()

                    # Cooldown Protection
                    if (
                        current_time
                        - last_alert_time
                        < ALERT_COOLDOWN
                    ):
                        continue

                    last_alert_time = current_time

                    now = datetime.now()

                    timestamp_str = now.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    file_safe_time = now.strftime(
                        "%Y%m%d_%H%M%S"
                    )

                    image_name = (
                        f"intrusion_{file_safe_time}.jpg"
                    )

                    image_path = os.path.join(
                        SNAPSHOT_DIR,
                        image_name
                    )

                    # Save Snapshot
                    cv2.imwrite(
                        image_path,
                        frame
                    )

                    # Save DB Event
                    save_intrusion_event(
                        now,
                        camera_location,
                        conf,
                        image_path
                    )

                    # Send Email Thread
                    email_thread = threading.Thread(
                        target=send_smtp_alert,
                        args=(
                            timestamp_str,
                            camera_location,
                            image_path
                        ),
                        daemon=True
                    )

                    email_thread.start()

                    logging.warning(
                        f"INTRUSION DETECTED | "
                        f"{camera_location} | "
                        f"{conf:.2f}"
                    )

                    break

        except Exception as e:

            logging.error(
                f"Inference error: {e}"
            )

        # ~10 FPS processing
        time.sleep(0.1)

    cap.release()


# ==================================================
# DIRECT EXECUTION
# ==================================================

if __name__ == "__main__":

    MODEL_PATH = "models/best.pt"

    RTSP_SOURCE = 0
    # Example:
    # rtsp://username:password@ip:554/stream

    start_live_observer(
        model_path=MODEL_PATH,
        source_rtsp=RTSP_SOURCE
    )