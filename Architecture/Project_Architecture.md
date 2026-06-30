The **AI engine** (`live_observer.py`) and **Web Dashboard** (`app.py`) are separated.

```bash

RTSP Camera
      │
      ▼
live_observer.py
      │
      ├── YOLO Detection
      ├── Snapshot Capture
      ├── PostgreSQL Logging
      └── Email Alerts
              │
              ▼
        PostgreSQL
              │
              ▼
          app.py
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
 Dashboard  Alerts  Owner Response

```
