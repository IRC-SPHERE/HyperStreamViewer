#!/usr/bin/env bash

if [ -e hyperstream_config.json ]; then
    if [ -L hyperstream_config.json ]; then
        rm hyperstream_config.json
    else
        mv hyperstream_config.json hyperstream_config.json.bak_$(date +"%Y%m%d%H%M%S")
    fi
fi
ln -s ../../IRC-SPHERE_private/HyperStream/hyperstream_config_dev.json hyperstream_config.json
