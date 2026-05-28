from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ultralytics import YOLO

class Model:
    ready: bool = False
    filepath: Optional[Path]
    model: Optional["YOLO"]

    def __init__(self):
        self.ready = False
        self.filepath = None
        self.model = None
    
    def load(self, filepath: Path):
        from ultralytics import YOLO
        self.filepath = filepath
        self.model = YOLO(filepath)
        self.ready = True
    
    def get_model(self) -> "YOLO":
        assert self.ready, "Model has not yet been loaded."
        return self.model # type: ignore

model = Model()