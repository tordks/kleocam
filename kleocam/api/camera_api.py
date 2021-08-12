import time

from kleocam.models.camera import CameraSettings, CameraState
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
    r = Redis()
    from picamera import PiCamera
    camera = PiCamera(**CameraSettings.from_redis(r).dict())



@router.put("/api/stop")
def stop():
    ...


@router.put("/api/capture")
def capture():
    from picamera import PiCamera
    camera = PiCamera(**CameraSettings.from_redis(r).dict())
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    camera.capture('foo.jpg')