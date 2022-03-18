import datetime
from loguru import logger

import fastapi
from fastapi import BackgroundTasks

from kleocam.models.camera import CameraState
from kleocam.recorder import Recorder
from redis import Redis

router = fastapi.APIRouter()

# TODO: Use a global camera object?


@router.get("/api/state")
def state() -> CameraState:
    r = Redis()
    return CameraState.from_redis(r)


@router.post("/api/state")
def state(state: CameraState):
    r = Redis()
    state.to_redis(r)


@router.put("/api/start")
async def start(background_tasks: BackgroundTasks):
    """
    Start recording
    """

    def record():
        logger.info("Start recording...")
        try:
            r = Redis()
            state = CameraState.from_redis(r)
            logger.info(f"savefolder: {state.savefolder}")

            with Recorder(state) as rec:
                state.active = 1
                state.to_redis(r)

                filename = (
                    datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".h264"
                )
                logger.info(f"Recording to: {filename}")

                rec.camera.start_recording(str(state.savefolder / filename))
                rec.camera.wait_recording(state.recording_time)

                # TODO: make the recording stop soon after sending stop signal,
                # instead of waiting for recording time.
                while True:
                    state = CameraState.from_redis(r)
                    if not state.active:
                        logger.info("Stopping recording loop")
                        break
                    filename = (
                        datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        + ".h264"
                    )
                    logger.info(f"Recording to: {filename}")
                    rec.camera.split_recording(str(state.savefolder / filename))
                    rec.camera.wait_recording(state.recording_time)

                rec.camera.stop_recording()
                logger.info("Recording stopped")

        except Exception as err:
            logger.error(f"Failed to start recording: {err}")
            r.set("active", 0)

    background_tasks.add_task(record)
    return {"message": "recording started in the background"}


@router.put("/api/stop")
async def stop():
    """
    Stop recording
    """
    r = Redis()
    r.set("active", 0)
    # TODO: use two variables to check whether recording is in progress. active
    # and recording? active is now more a desired state since recording will
    # finish the current file before stopping.
    logger.info("Set record state to inactive")


@router.put("/api/capture")
def capture():
    """
    Capture an image
    """
    logger.info("Capture image")
    r = Redis()
    state = CameraState.from_redis(r)

    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
    with Recorder(state) as rec:
        rec.camera.capture(str(state.savefolder / filename))
