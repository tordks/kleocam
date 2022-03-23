import datetime
from pathlib import Path
from loguru import logger

import fastapi
from fastapi import BackgroundTasks

from kleocam.models.camera import CameraState
from kleocam.recorder import Camera
from redis import Redis

router = fastapi.APIRouter()


def create_recording_output_dir(output_dir: Path):
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return output_dir / now


def create_recording_filepath(recording_output_dir: Path, suffix: str):
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return recording_output_dir / (now + suffix)


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

            recording_output_dir = create_recording_output_dir(state.output_dir)
            recording_output_dir.mkdir(parents=True)
            suffix = ".h264"

            with Camera(state) as camera:
                state.recording = 1
                state.to_redis(r)

                # TODO: abstract out recording folder management to be reused in
                # other recording calls, eg. capture.
                filepath = create_recording_filepath(
                    recording_output_dir, suffix
                )
                logger.info(f"Recording to: {filepath.absolute()}")

                camera.start_recording(str(state.output_dir / filepath))
                camera.wait_recording(state.recording_time)

                # TODO: make the recording stop soon after sending stop signal,
                # instead of waiting for recording time.
                while True:
                    state = CameraState.from_redis(r)
                    if state.stop_recording:
                        logger.info("Stopping recording loop")
                        break
                    filepath = create_recording_filepath(
                        recording_output_dir, suffix
                    )
                    logger.info(f"Recording to: {filepath}")
                    camera.split_recording(str(filepath))
                    camera.wait_recording(state.recording_time)

                camera.stop_recording()
                state.set_recording_stopped(r)
                logger.info("Recording stopped")

        except Exception as err:
            logger.error(f"Failed to start recording: {err}")
            state.set_recording_stopped(r)

    background_tasks.add_task(record)
    return {"message": "recording started in the background"}


@router.put("/api/stop")
async def stop():
    """
    Stop recording
    """
    r = Redis()
    r.set("stop_recording", 1)
    logger.info("Set signal to stop recording")


@router.put("/api/capture")
def capture():
    """
    Capture an image
    """
    r = Redis()
    state = CameraState.from_redis(r)

    filepath = create_recording_filepath(state.output_dir, ".jpg")
    logger.info(f"Capture image to {filepath}")
    with Camera(state) as camera:
        camera.capture(str(filepath))
