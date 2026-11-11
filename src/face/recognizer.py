from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognizer:
    """Build CPU face embeddings from photos/<person> and match webcam faces."""

    def __init__(self, photos_dir: Path, threshold: float = 0.42) -> None:
        if not photos_dir.is_dir():
            raise FileNotFoundError(f"Training folder not found: {photos_dir}")
        self.threshold = threshold
        model_cache = photos_dir.parent / "data" / "models"
        model_cache.mkdir(parents=True, exist_ok=True)
        self.engine = FaceAnalysis(
            name="buffalo_l", root=str(model_cache), providers=["CPUExecutionProvider"]
        )
        self.engine.prepare(ctx_id=-1, det_size=(640, 640))
        self.people: dict[str, list[np.ndarray]] = {}
        self._train(photos_dir)
        if not self.people:
            raise RuntimeError(f"No faces found in training photos under {photos_dir}")

    def _train(self, photos_dir: Path) -> None:
        supported = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for person_dir in sorted(p for p in photos_dir.iterdir() if p.is_dir()):
            vectors = []
            for path in sorted(p for p in person_dir.rglob("*") if p.suffix.lower() in supported):
                image = cv2.imread(str(path))
                if image is None:
                    print(f"Skipping unreadable image: {path}")
                    continue
                detected = self.engine.get(image)
                if not detected:
                    print(f"No face detected in training image: {path}")
                    continue
                largest = max(detected, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                vectors.append(self._normalize(largest.normed_embedding))
            if vectors:
                self.people[person_dir.name] = vectors
                print(f"Registered {person_dir.name}: {len(vectors)} training image(s)")

    @staticmethod
    def _normalize(vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32)
        return vector / (np.linalg.norm(vector) + 1e-12)

    def identify(self, embedding: np.ndarray) -> tuple[str | None, float]:
        probe = self._normalize(embedding)
        best_name, best_similarity = None, -1.0
        for name, vectors in self.people.items():
            similarity = max(float(np.dot(probe, vector)) for vector in vectors)
            if similarity > best_similarity:
                best_name, best_similarity = name, similarity
        if best_similarity < self.threshold:
            return None, best_similarity
        return best_name, best_similarity

    def detect(self, frame: np.ndarray) -> list[dict]:
        result = []
        for face in self.engine.get(frame):
            name, score = self.identify(face.normed_embedding)
            x1, y1, x2, y2 = [int(v) for v in face.bbox]
            result.append({"name": name, "score": score, "box": (x1, y1, x2, y2)})
        return result
