#!/bin/bash

#TODO: check if on pi or local and run correct compose file
mkdir data
docker-compose -f docker-compose-local.yml up --build -d
tox -r
docker-compose -f docker-compose-local.yml down
