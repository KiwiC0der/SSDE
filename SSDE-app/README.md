# SDE (Spatial Desktop Envirnoment)

A head-tracked 3D wireframe demo. Your webcam tracks your face; the perspective of a 3D box updates in real time so it feels like you’re looking at a frame in space.

## Requirements

- Python 3.8+
- Webcam
- (Optional) Good lighting so your face is clearly visible

## Setup

### 1. Open a terminal in this folder

```bash
cd /home/mimo/Desktop/SSDE/SSDE-app
```

### 2. (Recommended) Create a virtual environment

On many systems (e.g. Kali, Ubuntu 24+) Python is “externally managed”; install packages inside a venv to avoid errors like `No module named 'cv2'`:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or on Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run

From the project folder (with `.venv` or `venv` activated if you use it):

```bash
python run.py
```

Or use the script (it auto-activates `.venv` or `venv` if present):

```bash
./run.sh
```

- **First run:** The app will download the Face Landmarker model (~10 MB) into the `models/` folder once. This requires an internet connection.
- **Escape** or close the window to quit.
- If the camera doesn’t open, check that no other app is using it and that your system allows camera access.

## Testing

**1. Automated tests (no webcam or display)** — Verifies projection math and imports:

```bash
cd /home/mimo/Desktop/SSDE/SSDE-app
python3 -m unittest tests.test_projection -v
```

You should see `Ran 3 tests ... OK`.

**2. Run the app** — After `pip install -r requirements.txt`:

```bash
python run.py
```

- A window titled **SDE (Spatial Desktop Envirnoment) — Head Tracking Demo** should open.
- Bottom of the window shows **"Face detected — move your head"** (green) when your face is seen, or **"Looking for face..."** (red) otherwise.
- Move your head left/right and up/down: the white 3D box should shift perspective. If that happens, the app is working.
- Press **Escape** or close the window to exit.

## Project layout

- **`run.py`** — Entry point; run this to start the demo.
- **`config.py`** — Constants (window size, projection, box size, FPS, etc.). Edit here to experiment.
- **`src/projection.py`** — Off-axis projection math.
- **`src/head_tracker.py`** — Webcam + MediaPipe face tracking.
- **`src/renderer.py`** — Pygame wireframe and status text drawing.

## Tweaking

- **`config.py`**: Change `SCALE`, `EYE_DIST`, `BOX_*`, `TARGET_FPS`, or `HEAD_POSITION_SCALE` to alter the look and feel.
- **`src/renderer.py`**: Adjust `LINE_COLOR`, `LINE_WIDTH`, or the 3D box geometry.

## License

This custom build is for personal use and experimentation.
