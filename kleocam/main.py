import fastapi
from loguru import logger
from redis import Redis
import uvicorn

from kleocam.api import camera_api
from kleocam.models.camera import CameraState

app = fastapi.FastAPI()


def configure():
    configure_routing()


def configure_routing():
    app.include_router(camera_api.router)


@app.on_event("startup")
async def initialize_camera_settings():
    r = Redis()
    CameraState().to_redis(r)


@app.on_event("shutdown")
async def cleanup():
    ...


if __name__ == "__main__":
    configure()
    uvicorn.run(app, port=8000, host="127.0.0.1")
else:
    configure()