from pathlib import Path
from pydantic import BaseModel
from redis import Redis


class CameraSettings(BaseModel):
    """
    Settings for the camera.
    """

    width: int = 1280
    height: int = 720
    framerate: int = 30

    def to_redis(self, r: Redis):
        r.set("width", self.width)
        r.set("height", self.height)
        r.set("framerate", self.framerate)

    @staticmethod
    def from_redis(r: Redis):
        return CameraSettings(
            width=r.get("width"),
            height=r.get("height"),
            framerate=r.get("framerate"),
        )


class CameraState(BaseModel):
    settings: CameraSettings
    savefolder: Path = "."
    active: int = 0

    def to_redis(self, r: Redis):
        self.settings.to_redis(r),
        r.set("active", self.active),
        r.set("savefolder", self.savefolder)

    @staticmethod
    def from_redis(r: Redis):
        return CameraState(
            settings=CameraSettings.from_redis(r),
            active=r.get("active"),
            savefolder=r.get("savefolder")
        )