import fastapi
from loguru import logger
from redis import Redis
import uvicorn

from kleocam.api import camera_api
from kleocam.models.camera import CameraSettings

app = fastapi.FastAPI()


def configure():
    configure_routing()
    # TODO: add configuration of API keys
    # configure_api_keys()


def configure_routing():
    ...
    app.include_router(camera_api.router)


@app.on_event("startup")
async def initialize_camera_settings():
    r = Redis()
    r.mset(CameraSettings().dict())
    r.set("active", 0)
    r.set("savefolder", "./")


@app.on_event("shutdown")
async def cleanup():
    ...


if __name__ == "__main__":
    configure()
    uvicorn.run(app, port=8000, host="127.0.0.1")
else:
    configure()