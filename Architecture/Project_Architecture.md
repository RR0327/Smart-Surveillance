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

## Final Architecture

```bash
Camera
   │
   ▼
live_observer.py
   │
   ├─────────────┐
   ▼             ▼
database.py   email_service.py
   │             │
   ▼             ▼
 PostgreSQL     SMTP
      │
      ▼
   app.py
      │
      ▼
dashboard.html
      │
dashboard.js
```

This is a `professional software architecture`.
