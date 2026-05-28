from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Optional
import uuid

from app.types import CongestionRating
from app.vision.tracker import TrackerProcessResult, run_tracking


class JobStatus(Enum):
    processing = 1
    finished = 2
    error = 3


@dataclass
class Job:
    id: str

    progress: int = 0
    status: JobStatus = JobStatus.processing

    total_cars: int = 0
    cars_per_min: float = 0.0
    congestion_rating: CongestionRating = CongestionRating.unknown

    video_url: Optional[str] = None
    error: Optional[str] = None

class ActiveJobs:
    jobs: Dict[str, Job]

    def __init__(self):
        self.jobs = {}
    
    def start_new_job(self) -> str:
        """
        Start a new job and return the unique job id.
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id)
        self.jobs[job_id] = job
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id, None)
    
    def update_progress(self, job_id: str, progress: int):
        job = self.get_job(job_id)
        if job is None:
            return
        job.progress = progress
    
    def get_progress(self, job_id: str) -> Optional[int]:
        job = self.get_job(job_id)
        if job is None:
            return
        return job.progress

    def finished(self, job_id: str, process_result: TrackerProcessResult):
        job = self.get_job(job_id)
        if job is None:
            return
        
        # Set progress to 100% and mark the job as finished
        job.progress = 100
        job.status = JobStatus.finished

        # Set the video url
        job.video_url = f"/static/process/output/{job_id}.mp4"

        # Copy results
        job.total_cars = process_result.total_cars
        job.cars_per_min = process_result.cars_per_min
        job.congestion_rating = process_result.congestion_rating

    def error(self, job_id: str, error: Exception):
        job = self.jobs.get(job_id, None)
        if job is None:
            return
        job.progress = -100
        job.error = str(error)
        job.status = JobStatus.error


def process_video(
        input_path: Path,
        output_path: Path,
        progress_callback: Callable):
    """
    
    """
    return run_tracking(
        input_path=input_path,
        output_path=output_path,
        progress_callback=progress_callback
    )