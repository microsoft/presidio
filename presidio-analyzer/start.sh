#!/bin/bash

if [ "${NLP_ENGINE}" = "transformers" ]; then 
    poetry run python app.py --host 0.0.0.0; 
else 
    poetry run gunicorn -w ${WORKERS} -b 0.0.0.0:${PORT} 'app:create_app()'; 
fi