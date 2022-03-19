from pathlib import Path
import platform
import time
from unittest.mock import MagicMock

def on_arm_machine():
    return "arm" in platform.machine()

def picamera_mock(resolution, framerate):
    camera_mock = MagicMock(
        resolution=resolution, framerate=framerate
    )
    camera_mock.wait_recording.side_effect = lambda rec_time: time.sleep(
        rec_time
    )
    camera_mock.split_recording.side_effect = lambda fpath: Path(
        fpath
    ).touch()
    camera_mock.capture.side_effect = lambda fpath: Path(fpath).touch()
    return camera_mock