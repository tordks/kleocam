# Kleocam

Kleocam is a project for monitoring our dog (Kleo) while we are away. The goal
is to have a system that registers when the dog moves and identifies whether she
has been in locations a she should not (read: the sofa).


## Features
* record through API
    * image capture
    * start/stop video recording


## Architecture
* FastAPI for API
* redis to hold state
* mocking picamera for local development
* containerized services
    * local dev + prod using docker-compose

## Future features
* motion detection using camera stream
* dog-in-sofa detection using image classification
* slack integration for remote monitor and notification