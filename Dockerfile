FROM python:3.9.6-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.13

WORKDIR /app

RUN python -m venv /venv
RUN /venv/bin/pip install "poetry==$POETRY_VERSION"

# TODO: dont copy entire repo?
COPY . /app
RUN /venv/bin/poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin
RUN /venv/bin/poetry build && /venv/bin/pip install dist/*.whl

CMD cd kleocam && /venv/bin/uvicorn main:app