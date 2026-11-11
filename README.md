# Attendance

CPU-based webcam attendance app using InsightFace and ONNX Runtime. Training photos are read from `photos/<person name>/`; the folder name becomes the registered name. The supplied photos register **Lavanya**.

## Setup and run

Use Python 3.10–3.12 on Windows. Python 3.13+ may not yet have compatible InsightFace wheels. InsightFace may require Microsoft C++ Build Tools during installation.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python run.py
```

On first run, `run.py` installs missing packages from `requirements.txt`. The app downloads InsightFace's `buffalo_l` model on first use and runs it through `CPUExecutionProvider`; the laptop needs internet for initial setup/model download. Allow webcam access when Windows prompts. Press **Q** or **Esc** to stop. Edit `camera_index` in `src/face/webcam.py` if the default camera is not index 0.

## Files produced

- `data/attendance.xlsx`: face thumbnail, name, present status, date, and time. One entry per person every 60 seconds while visible; unregistered faces are recorded under “User not registered.”
- `data/captures/`: cropped face images referenced by the workbook.
- `data/technical.log`: program start/stop, webcam start/stop, and errors with local timezone timestamps.

## Register another person

Create a folder such as `photos/Person Name/` and add clear, well-lit JPG/PNG photos with one visible face. On startup the app detects the largest face in each photo and builds in-memory embeddings; it does not modify the photos or save biometric embeddings to disk. Similarity threshold is configured in `src/face/recognizer.py`.

Attendance is a local convenience log and should be reviewed for false matches. Provide appropriate notice and consent before collecting or using face images.
