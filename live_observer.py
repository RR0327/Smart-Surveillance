# Continuous Background AI Stream (OpenCV9+ YOLO Load) for Intrusion Detection System (IDS) with Email Alerting and Logging

import cv2
import time
import os
import threading
import psycopg2
from datetime import datetime
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Database connection configuration
DB_CONFIG = {
    'dbname': 'your_db_name',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}

def send_smtp_alert(timestamp, camera_location, image_path):
    """Pillar 4: Triggers secure SMTP alert with snapshot attachment"""
    sender_email = "your_security_email@gmail.com"
    receiver_email = "owner_email@gmail.com"
    password = "your_app_password" # Use Gmail App Passwords if using Gmail

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚨 SECURITY ALERT: Unauthorized Intrusion at {camera_location}"

    # Actionable UI Webhook Button targeting your Flask server endpoint
    body = f"""
    <h3>Intrusion Detected!</h3>
    <p><b>Location:</b> {camera_location}</p>
    <p><b>Time:</b> {timestamp}</p>
    <p>Please review the attached snapshot below.</p>
    <hr/>
    <p><b>Is this an active threat?</b></p>
    <a href="http://localhost:5000/api/response?status=yes&location={camera_location}"
       style="background-color: red; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px;">
       YES - Call Police
    </a>
    &nbsp;&nbsp;
    <a href="http://localhost:5000/api/response?status=no"
       style="background-color: green; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 5px;">
       NO - False Alarm
    </a>
    """
    msg.attach(MIMEText(body, 'html'))

    # Attach the high-quality captured frame image
    with open(image_path, 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename(image_path))
    msg.attach(image)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 557) # TLS Setup
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("[-] SMTP Security Alert successfully dispatched.")
    except Exception as e:
        print(f"[!] SMTP Failure: {e}")

def start_live_observer(model_path, source_rtsp, camera_location="Warehouse Main Entrance"):
    """Pillar 1 & 2: Continuous Real-Time Streaming and YOLO Inference Engine"""
    print(f"[-] Initializing AI Model from path: {model_path}")
    model = YOLO(model_path)

    # Connect to RTSP stream or web-camera (0 for default local webcam test)
    cap = cv2.VideoCapture(source_rtsp)

    # Establish connection to your PostgreSQL database instance
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    confidence_threshold = 0.50 # Hardcoded base threshold (Can optimize dynamically later!)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[!] Video stream interrupted. Reconnecting...")
            time.sleep(2)
            cap = cv2.VideoCapture(source_rtsp)
            continue

        # Run local frame through YOLO
        results = model(frame, verbose=False)[0]

        for box in results.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Check if class is 0 (assuming standard human detection category) and passes threshold
            if cls == 0 and conf >= confidence_threshold:
                now = datetime.now()
                timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
                file_safe_time = now.strftime("%Y%m%d_%H%M%S")

                # Pillar 3: Save the precise frame Snapshot locally
                snapshot_dir = "static/snapshots"
                os.makedirs(snapshot_dir, exist_ok=True)
                image_name = f"intrusion_{file_safe_time}.jpg"
                image_path = os.path.join(snapshot_dir, image_name)
                cv2.imwrite(image_path, frame)

                # Pillar 3: Log full event Metadata directly to PostgreSQL
                try:
                    insert_query = """
                    INSERT INTO intrusion_logs (timestamp, location, confidence, snapshot_path)
                    VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(insert_query, (timestamp_str, camera_location, conf, image_path))
                    conn.commit()
                    print(f"[+] Intrusion recorded in Database at {timestamp_str}")
                except Exception as db_err:
                    conn.rollback()
                    print(f"[!] DB Log failure: {db_err}")

                # Run SMTP alert handler as a non-blocking execution block
                email_thread = threading.Thread(
                    target=send_smtp_alert,
                    args=(timestamp_str, camera_location, image_path)
                )
                email_thread.start()

                # Enforce a 15-second cooldown delay to prevent spamming the owner's mailbox
                time.sleep(15)
                break

        # Enforce FPS pacing limitation (sleep briefly to maintain ~10 FPS processing rate)
        time.sleep(0.1)

    cursor.close()
    conn.close()
    cap.release()
