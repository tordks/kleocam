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
    output_dir: Path = (
        Path(os.environ["OUTPUT_DIR"]) if "OUTPUT_DIR" in os.environ else None
    )

    # TODO: make these "private". Should not be able to be set at instantiation
    stop_recording: int = 0
    recording: int = 0

    def set_recording_stopped(self, r: Redis):
        self.recording = 0
        self.stop_recording = 0
        self.to_redis(r)

    def to_redis(self, r: Redis):
        if "resolution" not in r:
            r.lpush("resolution", *self.resolution[::-1])
        else:
            r.lset("resolution", 0, self.resolution[0])
            r.lset("resolution", 1, self.resolution[1])

        r.set("framerate", self.framerate)
        r.set("iso", self.iso)
        r.set("recording_time", self.recording_time)
        r.set("output_dir", str(self.output_dir))
        r.set("stop_recording", self.stop_recording)
        r.set("recording", self.recording)

    @staticmethod
    def from_redis(redis_client: Redis):
        return CameraState(
            resolution=redis_client.lrange("resolution", 0, 2),
            framerate=redis_client.get("framerate").decode(),
            iso=redis_client.get("iso").decode(),
            recording_time=redis_client.get("recording_time"),
            output_dir=Path(redis_client.get("output_dir").decode()),
            stop_recording=redis_client.get("stop_recording"),
            recording=redis_client.get("recording"),
        )
