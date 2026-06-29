### Our current project has two separate systems:

1. **`live_observer.py`**
   - Runs YOLO
   - Saves snapshots
   - Logs to PostgreSQL
   - Sends emails
2. **`app.py`**
   - Runs Flask dashboard
   - Streams video
   - Uses fake detections (dummy_model_inference)

> A production-quality app.py should not run another YOLO detector inside Flask. Instead:

```bash
RTSP Camera
      ↓
live_observer.py
      ↓
PostgreSQL
      ↓
Flask Dashboard (app.py)
```

The dashboard should simply:

- Display recent alerts from PostgreSQL
- Show snapshots
- Provide the owner response buttons
- Show police contact information
- Serve the UI
