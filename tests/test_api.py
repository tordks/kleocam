import json
import os
from pathlib import Path
import time

from redis import Redis
import requests

from kleocam.models.camera import CameraState
from kleocam.recorder import Camera

# TODO: one client per test? Then the app should be restarted for each test.
# TODO: start redis from docker compose and API from tox/pytest?
#    * live with two instances running?
redis_client = Redis()

# NOTE: assumption that this is the output_dir in the app. Needed to initiate
# CameraState which is sued to initialize state and to read state from Redis.
# TODO: Set as env variable instead in test script
OUTPUT_DIR = Path("/data")
LOCAL_OUTPUT_DIR = Path("./data")


def test_get_state():
    init_state = CameraState(output_dir=OUTPUT_DIR)

    response = requests.get("http://localhost:8000/api/state")
    assert response.status_code == 200

    state = CameraState(**json.loads(response.content.decode()))

    assert state.dict() == init_state.dict()
    assert state == init_state


def test_set_state():
    try:
        state_to_set = CameraState(
            recording_time=120, framerate=24, iso=150, output_dir=OUTPUT_DIR
        )

        response = requests.post(
            f"http://localhost:8000/api/state", data=state_to_set.json()
        )
        assert response.status_code == 200

        state = CameraState.from_redis(redis_client)
        assert state.dict() == state_to_set.dict()
    finally:
        requests.put("http://localhost:8000/api/reset_state")


def test_capture():
    capture_dir = LOCAL_OUTPUT_DIR / "capture"
    requests.put("http://localhost:8000/api/capture")
    time.sleep(Camera.max_warmup_time + 0.5)
    assert capture_dir.exists()
    assert len(list(capture_dir.iterdir())) == 1


def test_recording():
    try:
        state = CameraState.from_redis(redis_client)
        # TODO: adjust recording_time to as short as possible
        recording_time = 5
        state.recording_time = recording_time
        state.to_redis(redis_client)
        requests.put("http://localhost:8000/api/start")

        time.sleep(Camera.max_warmup_time + 0.5)
        state = CameraState.from_redis(redis_client)
        assert state.recording == 1
        assert state.stop_recording == 0

        time.sleep(recording_time * 2)
        requests.put("http://localhost:8000/api/stop")
        state = CameraState.from_redis(redis_client)
        assert state.stop_recording == 1
        assert state.recording == 1

        time.sleep(recording_time)
        state = CameraState.from_redis(redis_client)
        assert state.stop_recording == 0
        assert state.recording == 0

        recording_dir = LOCAL_OUTPUT_DIR / "recording"
        assert recording_dir.exists()

        recordings = list(recording_dir.iterdir())
        assert len(recordings) == 1

        recording = recordings[0]
        recording_parts = list(recording.iterdir())
        assert len(recording_parts) == 3

    finally:
        requests.put("http://localhost:8000/api/reset_state")
