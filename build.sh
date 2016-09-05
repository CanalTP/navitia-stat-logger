#!/bin/bash
if [ -z "$(ls -A navitia-proto)" ]; then
    git submodule update --init
fi
VERSION=${1:-latest}
docker build -t navitia-stat-logger:$VERSION .
