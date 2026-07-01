### What Needs Refactoring

Currently:

```bash
app.py
```

> contains

- database connection
- police dictionary

> while

```bash
live_observer.py
```

> contains

- email sending
- database logic
- logging

These should move into **utils**.
