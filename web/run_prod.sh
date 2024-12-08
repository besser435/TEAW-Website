#!/bin/bash
gunicorn --workers 4 --bind 0.0.0.0:1852 --name gunicorn_teaw teaw_webserver:app