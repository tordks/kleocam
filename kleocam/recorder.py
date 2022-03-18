import time
from pathlib import Path
from unittest.mock import MagicMock

from kleocam.utils import on_arm_machine
from kleocam.models.camera import CameraState

# Assume we are on a raspberry pi if we are on an arm machine. If not we are in
# development mode without access to the picamera module
if on_arm_machine():
    from picamera import PiCamera
else:
    PiCamera = MagicMock()
    Picamera.wait_recording.side_effect = lambda time: time.sleep(time)
    Picamera.split_recording.side_effect = lambda fpath: Path(fpath).touch()


# TODO: Force singleton + share object?
# TODO: Currently calling camera object directly, make wrapper to handle everything here?
class Recorder:
    """
    Class for taking images and recording video
    """

    def __init__(self, state: CameraState, consistent_img: bool = True):
        self.camera = PiCamera(
            resolution=state.resolution, framerate=state.framerate
        )

        # Capturing consistent images: https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images.
        if consistent_img:
            # Set ISO to the desired value
            self.camera.iso = state.iso
            # Wait for the automatic gain control to settle
            time.sleep(2)
            # Now fix the values
            self.camera.shutter_speed = self.camera.exposure_speed
            self.camera.exposure_mode = "off"
            g = self.camera.awb_gains
            self.camera.awb_mode = "off"
            self.camera.awb_gains = g

        # camera warmup time
        self.camera.start_preview()
        time.sleep(2)
        self.camera.stop_preview()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__del__()

    def __del__(self):
        self.camera.close()

    def update_state(self, state: CameraState):
        ...


if __name__ == "__main__":
    recorder = Recorder(CameraState())

    recorder.camera.capture("image.jpg")

    recorder.camera.start_recording("recording.h264")
    recorder.camera.wait_recording(60)
    recorder.camera.stop_recording()
