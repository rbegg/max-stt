#!/bin/bash

# Define the name of the shared volume
VOLUME_NAME="model_cache"

# Check if the volume already exists
if ! docker volume ls -q | grep -q "^${VOLUME_NAME}$"; then
  echo "Volume '${VOLUME_NAME}' not found. Creating it now..."
  # Create the volume
  docker volume create "${VOLUME_NAME}"
  echo "Volume '${VOLUME_NAME}' created successfully."
else
  echo "Volume '${VOLUME_NAME}' already exists. Skipping creation."
fi

echo "Setup complete. You can now run 'make dev' or 'make prod' etc."