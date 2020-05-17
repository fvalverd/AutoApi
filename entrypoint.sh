#!/usr/bin/env bash

export AUTH=False

# Check for authentication configuration
if [ -n "$MONGO_ADMIN" ] && [ -n "$MONGO_ADMIN_PASS" ]; then
	AUTH=True
  echo "MONGO_ADMIN and MONGO_ADMIN_PASS env vars detected!"
  echo "Updating MongoDB admin..."
  autoapi update-admin --port "$MONGO_PORT"
  echo "MongoDB admin updated!"
  echo "Running AutoApi with authentication..."
else
	echo "Running AutoApi without authentication..."
fi

gunicorn "auto_api:AutoApi(auth=$AUTH)" "$@"
