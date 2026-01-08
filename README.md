# Color Poll

A small Python project demonstrating a color poll implemented as:

- a desktop GUI using `tkinter` (`color_poll.py`) and
- a web app using `Flask` (`app.py` and templates under `templates/`).

This repository includes the UI, a detail page for each color and simple server endpoints.

**Colors available**: `R` (Red), `G` (Green), `Y` (Yellow), `B` (Blue).

## Files

- `app.py` — Flask application and routes (serves poll and color detail pages).
- `color_poll.py` — standalone `tkinter` desktop poll (alternative to web UI).
- `templates/index.html` — poll page (radio options, background color change).
- `templates/color_detail.html` — detail page showing description & real-world importance.
- `flask_output.log` — (if present) background server log created when running with `nohup`.

## Features implemented

- Single-choice poll (R/G/Y/B).
- Selecting a color changes the background color and redirects to a dedicated detail page.
- Each color has a description and a list of real-world importance/examples.
- The Flask app exposes a simple JSON API (`/api/colors`, `/api/select-color`).

## Run (web)

1. Install dependencies (only Flask is required for the web UI):

```bash
python3 -m pip install --user flask
```

2. Start the server (development):

```bash
cd /home/shazil/code-experiment
python3 app.py
# or run in background
nohup python3 app.py > flask_output.log 2>&1 &
```

3. Open in your browser:

- Local: `http://127.0.0.1:5000`
- Network: `http://<your-machine-ip>:5000`

## Run (desktop/tkinter)

The `tkinter` app requires the system package for Python tkinter. On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y python3-tk
python3 /home/shazil/code-experiment/color_poll.py
```

## Publish to GitHub (quick steps)

```bash
cd /home/shazil/code-experiment
git init
git checkout -b main
git add .
git commit -m "Initial commit: Color Poll web + desktop app"
# Create remote repo on GitHub (web UI) or via gh CLI, then push:
git remote add origin git@github.com:YOUR_USERNAME/color-poll.git
git push -u origin main
```

## Notes

- The Flask development server is suitable for testing only. For production, run behind a WSGI server (e.g. Gunicorn) and use Nginx as a reverse proxy.
- If you want, I can add a `requirements.txt`, `.gitignore`, and optionally create the GitHub repo for you via the `gh` CLI.

---

If you'd like, I can now create `requirements.txt` and `.gitignore` and commit them, or push the repo to GitHub for you (you'll need to authenticate). Which would you prefer?
