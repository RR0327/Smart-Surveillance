> ## app.py

Only:

- Flask routes
- Dashboard
- API
- Health Check

Nothing else.

> ## live_observer.py

Only:

- Camera
- YOLO
- Snapshot
- Call database.py
- Call email_service.py

Nothing else.

> ## utils/database.py

Responsible for

```py
connect()

save_intrusion()

get_latest_alerts()

get_alert()

close()
```

> ## utils/email_service.py

Responsible for

```py
send_intrusion_email()
```

Only email.

> ## utils/logger.py

Responsible for

```py
logging.basicConfig(...)
```

Entire project imports

```py
logger
```

instead of writing

```py
logging.basicConfig(...)
```

everywhere.

> ### Why logger.py?

Both `app.py` and `live_observer.py` will use logging, so it's better to centralize it first.

A good logger.py should:

Configure both console and file logging.
Automatically create the logs/ directory if it doesn't exist.
Write logs to logs/system.log.
Use a consistent format (timestamp, level, module, message).
Expose a helper like get_logger(name) so every module can do:

> ## utils/police_lookup.py

Instead of

```py
POLICE = {
...
}
```

inside app.py

Move it here.

Example

```py
get_police_station(location)
```

> ## static/js/dashboard.js

Instead of putting

```py
fetch(...)
```

inside HTML

Move it here.

HTML becomes cleaner.

> ## static/css/style.css

Instead of

```html
<style>
```

Move everything here.

> ## schema.sql

Creates

```sql
intrusion_logs

camera_locations

police_contacts
```

> ## seed.sql

Insert

```sql
camera locations

police stations

sample data
```

> ## README.md

Professional GitHub page.

Include

- Features
- Installation
- Dataset
- Screenshots
- Research Objective
- Architecture
- Demo

> ## .gitignore

Ignore

```bash
__pycache__

.env

logs/

snapshots/

*.pyc

venv/

.idea/

.vscode/
```
