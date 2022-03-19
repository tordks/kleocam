import os
from pathlib import Path

from pydantic import BaseModel
from redis import Redis


class CameraState(BaseModel):
    resolution: tuple[int, int] = (1640, 1232)
    framerate: int = 30
    iso: int = 300
    recording_time = 300

    # TODO: add validation for output_dir
    output_dir: Path = Path(os.environ["OUTPUT_DIR"])
    active: int = 0

    def to_redis(self, r: Redis):
        if "resolution" not in r:
            r.lpush("resolution", *self.resolution)
        else:
            r.lset("resolution", 0, self.resolution[0])
            r.lset("resolution", 1, self.resolution[1])

        r.set("framerate", self.framerate)
        r.set("iso", self.iso)
        r.set("recording_time", self.recording_time)
        r.set("savefolder", str(self.output_dir))
        r.set("active", self.active)

    @staticmethod
    def from_redis(r: Redis):
        return CameraState(
            resolution=r.lrange("resolution", 0, 2),
            framerate=r.get("framerate").decode(),
            iso=r.get("iso").decode(),
            recording_time=r.get("recording_time"),
            savefolder=Path(r.get("savefolder").decode()),
            active=r.get("active"),
        )
