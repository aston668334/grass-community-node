#!/bin/sh

if [ "$USE_PROXY" = "true" ]; then
    exec python3 grass_community_proxy_docker.py
else
    exec python3 grass_community_no_proxy.py
fi
