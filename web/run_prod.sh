#!/bin/bash
gunicorn -w 4 -b 0.0.0.0:1851 app:teaw_website