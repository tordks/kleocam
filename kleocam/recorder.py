import time
from picamera import PiCamera

# TODO: create dummy picamera class to be able to test on desktop
# TODO: Change into initialize_camera function? Factory class?
class Recorder:
    """
    Class for taking images and recording video
    """

    def __init__(self, **camera_settings):

        """
        initialize camera settings
        """

        self.camera = PiCamera(**camera_settings)

        # Capturing consistent images: https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images.
        # Set ISO to the desired value
        self.camera.iso = 50
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

    def __del__(self):
        self.camera.close()


if __name__ == "__main__":
    recorder = Recorder()

    recorder.camera.capture("image.jpg")

    recorder.camera.start_recording("recording.h264")
    recorder.camera.wait_recording(60)
    recorder.camera.stop_recording()
