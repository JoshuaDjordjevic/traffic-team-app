import os
from pathlib import Path
import threading
import time
import uuid
from flask import Flask, jsonify, render_template, request, send_from_directory

from app.services.video_pipeline import ActiveJobs, JobStatus, process_video
from app.vision.tracker import TrackerProcessResult
from app.vision.yolo import model

ROOT = Path(__file__).parent
UPLOAD_FOLDER = ROOT / "static/process/upload"
OUTPUT_FOLDER = ROOT / "static/process/output"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
MODEL_PATH = ROOT / "models/best-26-04-30.pt"

def create_app():
    app = Flask(__name__)

    # Load model
    model.load(MODEL_PATH)

    active_jobs = ActiveJobs()

    # Background worker
    def run_processing(job_id, input_path, output_path):
        print(f"Job started {job_id}")

        def update_progress(p):
            active_jobs.update_progress(job_id, int(p*100))

        try:
            process_result = process_video(input_path, output_path, update_progress)
            active_jobs.finished(job_id, process_result)

        except Exception as e:
            active_jobs.error(job_id, e)
            print(f"Job {job_id} failed:", e)

    # App routes

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/api/upload", methods=["POST"])
    def upload():
        file = request.files["video"]

        job_id = active_jobs.start_new_job()

        input_path = UPLOAD_FOLDER / f"{job_id}.mp4"
        output_path = OUTPUT_FOLDER / f"{job_id}.mp4"

        file.save(input_path)

        thread = threading.Thread(
            target=run_processing,
            args=(job_id, input_path, output_path)
        )
        thread.start()

        return jsonify({"job_id": job_id})
    
    @app.route("/api/result/<job_id>")
    def result(job_id: str):
        job = active_jobs.get_job(job_id)
        if job is None:
            return jsonify({"status": "unknown"}), 404
    
        return jsonify({
            "status": "ok",
            "video_url": job.video_url,
            "total_cars": job.total_cars,
            "cars_per_min": job.cars_per_min,
            "congestion_rating": job.congestion_rating.name
        })

    # Progress endpoint
    @app.route("/api/progress/<job_id>")
    def progress(job_id: str):
        job = active_jobs.get_job(job_id)

        if job is None:
            return jsonify({
                "progress": 0,
                "status": "unknown"
            }), 404

        if job.status == JobStatus.error: # error state
            return jsonify({
                "progress": 0,
                "status": "error"
            })
        
        return jsonify({
            "progress": job.progress,
            "status": "ok"
        })

    return app