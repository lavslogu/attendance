from __future__ import annotations

from datetime import datetime
import time
import cv2


def run_camera(recognizer, attendance, technical, camera_index: int = 0) -> None:
    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions and camera_index.")

    technical.log("CAMERA_ON", f"camera_index={camera_index}")
    last_logged: dict[str, float] = {}
    interval = 60.0
    print("Camera is running. Press Q or Esc to stop.")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("Webcam stopped returning frames")
            for face in recognizer.detect(frame):
                x1, y1, x2, y2 = face["box"]
                name = face["name"]
                registered = name is not None
                color = (40, 190, 40) if registered else (40, 40, 230)
                label = name if registered else "User not registered"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.62, 2)
                top = max(0, y1 - th - 12)
                cv2.rectangle(frame, (x1, top), (x1 + tw + 8, y1), color, -1)
                cv2.putText(frame, label, (x1 + 4, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
                key = name if registered else "UNREGISTERED"
                now = time.monotonic()
                if now - last_logged.get(key, -interval) >= interval:
                    attendance.record(frame, face["box"], name)
                    last_logged[key] = now
            cv2.imshow("Attendance - Q to quit", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        technical.log("CAMERA_OFF")
