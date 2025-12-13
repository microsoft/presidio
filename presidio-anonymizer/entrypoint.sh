#!/bin/sh
exec poetry run gunicorn -w "$WORKERS" -b "0.0.0.0:$PORT" "app:create_app()"
