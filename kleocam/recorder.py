import time

from kleocam.utils import on_arm_machine, picamera_mock
from kleocam.models.camera import CameraState

# Assume we are on a raspberry pi if we are on an arm machine. If not we are in
# development mode without access to the picamera module
if on_arm_machine():
    from picamera import PiCamera
else:
    PiCamera = picamera_mock


# TODO: Force singleton + share object?
# TODO: Currently calling camera object directly, make wrapper to handle everything here?
# TODO: Convert this to function that just returns camera object?
class Camera:
    """
    Class that wraps a PiCamera and initiaites it with sensible settings. If not
    developing on a RPi it will instead of a PiCamera set up a mock
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
        return self.camera

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__del__()

    def __del__(self):
        self.camera.close()


if __name__ == "__main__":
    recorder = Camera(CameraState())

    recorder.camera.capture("image.jpg")

    recorder.camera.start_recording("recording.h264")
    recorder.camera.wait_recording(5)
    recorder.camera.stop_recording()
