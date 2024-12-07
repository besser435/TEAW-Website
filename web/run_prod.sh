#!/bin/bash
gunicorn --workers 4 --bind 0.0.0.0:1851 --name gunicorn_teaw_webserver app:teaw_webserver