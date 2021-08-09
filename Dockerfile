FROM python:3.9.6-slim

ADD . /kleocam

RUN apt-get update -qq \
&& apt-get install -y --no-install-recommends curl \
# TODO: avoid using poetry in this way. Upload package to private pypi instead?
&& pip install poetry==1.1.7 \
&& cd /kleocam && poetry install && cd


# TODO: How to set up entrypoint?
# ENTRYPOINT ["uvicorn", "--reload", "kleocam.main:app"]