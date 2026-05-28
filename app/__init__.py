import os
from pathlib import Path
import threading
import time
import uuid
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).parent
UPLOAD_FOLDER = ROOT / "static/process/upload"
OUTPUT_FOLDER = ROOT / "static/process/output"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

def process_video(path: str, out: str, func):
    print(f"Processing {path}...")
    for i in range(15):
        time.sleep(0.25)
        func(i/15)

def create_app():
    app = Flask(__name__)

    progress_dict = {}

    # Background worker
    def run_processing(job_id, input_path, output_path):
        print(f"Job started {job_id}")

        def update_progress(p):
            progress_dict[job_id] = int(p * 100)

        try:
            process_video(input_path, output_path, update_progress)
            progress_dict[job_id] = 100
        except Exception as e:
            progress_dict[job_id] = -1 # error state
            print(f"Job {job_id} failed:", e)

    # App routes

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/api/upload", methods=["POST"])
    def upload():
        file = request.files["video"]

        job_id = str(uuid.uuid4())

        input_path = UPLOAD_FOLDER / f"{job_id}.mp4"
        output_path = OUTPUT_FOLDER / f"{job_id}.mp4"

        file.save(input_path)

        progress_dict[job_id] = 0

        thread = threading.Thread(
            target=run_processing,
            args=(job_id, input_path, output_path)
        )
        thread.start()

        return jsonify({"job_id": job_id})
    
    # Progress endpoint
    @app.route("/api/progress/<job_id>")
    def progress(job_id):
        value = progress_dict.get(job_id, None)

        if value is None:
            return jsonify({"progress": 0, "status": "unknown"}), 404

        if value == -1:
            # error state
            return jsonify({"progress": 0, "status": "error"})
        return jsonify({"progress": value, "status": "ok"})

    return app