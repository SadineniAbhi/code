#!/bin/sh
set -e

if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS" --quiet
fi

exec "$@"
