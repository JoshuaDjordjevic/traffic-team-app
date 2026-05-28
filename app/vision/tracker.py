from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import typing

import cv2

from app.types import CongestionRating, TrackerProcessResult
from app.vision.yolo import model
from deep_sort_realtime.deepsort_tracker import DeepSort


def get_congestion(cars_per_min: float) -> CongestionRating:
    if cars_per_min < 60:
        return CongestionRating.light
    elif cars_per_min < 160:
        return CongestionRating.moderate
    else:
        return CongestionRating.heavy

def run_tracking(
        input_path: Path,
        output_path: Path,
        progress_callback: Callable) -> TrackerProcessResult:
    """
    ...
    """

    tracker = DeepSort(
        max_age=30,
        n_init=20,
        nms_max_overlap=0.6
    )
    yolo_model = model.get_model()

    cap = cv2.VideoCapture(input_path)

    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"avc1"),
        fps,
        (width, height)
    )
    
    frame_index = 0

    seen_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = yolo_model(frame, conf=0.4)

        detections = []

        # Add all results as bounding boxes to the detections list
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                w_box = x2 - x1
                h_box = y2 - y1

                detections.append(([x1, y1, w_box, h_box], conf, cls))

        # Update deepsort tracker
        tracks = tracker.update_tracks(detections, frame=frame)

        # Draw each tracked bounding box on the output video
        for track in tracks:
            if not track.is_confirmed():
                continue

            l, t, r, b = map(int, track.to_ltrb())
            track_id = track.track_id
            seen_ids.add(track_id)

            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

            label = f"ID {track_id}"
            cv2.putText(
                frame, label, (l, t - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 255, 0), 2
            )

        out.write(frame)

        # Update progress
        frame_index += 1
        progress_callback(frame_index / num_frames)

    # Finish up with the video files and release them
    cap.release()
    out.release()

    # Compute metrics
    total_cars = len(seen_ids)
    duration_minutes = (frame_index / fps) / 60
    cars_per_min = total_cars / duration_minutes if duration_minutes > 0 else 0 # zero-division safe

    # Return the result
    return TrackerProcessResult(
        total_cars=total_cars,
        cars_per_min=cars_per_min,
        congestion_rating=get_congestion(cars_per_min)
    )