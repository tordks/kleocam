import time

from kleocam.models.camera import CameraSettings, CameraState
from kleocam.recorder import Recorder
from redis import Redis
import fastapi

router = fastapi.APIRouter()

# TODO: Use a global camera object?

@router.get("/api/state")
def state() -> CameraState:
    # TODO: return state (settings + active, recording mode, ...)
    r = Redis()
    return CameraState.from_redis(r)


@router.put("/api/start")
def start():
    """
    Start video recording
    """
    ...
    # r = Redis()
    # from picamera import PiCamera
    # camera = PiCamera(**CameraSettings.from_redis(r).dict())



@router.put("/api/stop")
def stop():
    """
    Stop video recording
    """
    ...


@router.put("/api/capture")
def capture():
    """
    Capture an image
    """
    from picamera import PiCamera
    r = Redis()

    with Recorder(CameraState.from_redis(r).dict()) as rec:
        rec.camera.capture()