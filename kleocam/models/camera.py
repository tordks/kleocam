from pydantic import BaseModel
from redis import Redis


class CameraSettings(BaseModel):
    """
    Settings for the camera. These have to be a subset of the picamera settings.
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
    active: int = 0

    @staticmethod
    def from_redis(r: Redis):
        settings = CameraSettings.from_redis(r)
        active = r.get("active")

        return CameraState(settings=settings, active=active)