from dataclasses import dataclass
from enum import Enum


class CongestionRating(Enum):
    unknown = -1
    light = 0
    moderate = 1
    heavy = 2

@dataclass
class TrackerProcessResult:
    total_cars: int
    cars_per_min: float
    congestion_rating: CongestionRating