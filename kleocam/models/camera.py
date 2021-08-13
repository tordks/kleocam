from pathlib import Path
from pydantic import BaseModel
from redis import Redis


class CameraSettings(BaseModel):
    """
    Settings for the camera. Need to be a subset of the picamera settings.
    """

    # TODO: picamera need to insert resolution, not width/height => need to
    # figure out how to manage dict with list ion redis.
    resolution: tuple[int, int] = (1280, 720)
    framerate: int = 30
    iso: int = 200

    def to_redis(self, r: Redis):
        if "resolution" not in r:
            r.lpush("resolution", *self.resolution)
        else:
            r.lset("resolution", 0, self.resolution[0])
            r.lset("resolution", 1, self.resolution[1])

        r.set("framerate", self.framerate)
        r.set("iso", self.iso)

    @staticmethod
    def from_redis(r: Redis):
        return CameraSettings(
            width=r.get("width").decode(),
            height=r.get("height").decode(),
            framerate=r.get("framerate").decode(),
        )


class CameraState(BaseModel):
    settings: CameraSettings = CameraSettings()
    savefolder: Path = Path(".")
    active: int = 0

    def to_redis(self, r: Redis):
        self.settings.to_redis(r),
        r.set("active", self.active),
        r.set("savefolder", str(self.savefolder))

    @staticmethod
    def from_redis(r: Redis):
        return CameraState(
            settings=CameraSettings.from_redis(r),
            active=r.get("active"),
            savefolder=Path(r.get("savefolder").decode()),
        )