#!/bin/bash

# --- Function to create a Docker volume if it doesn't exist ---
create_docker_volume() {
  local volume_name="$1"
  if ! docker volume ls -q | grep -q "^${volume_name}$"; then
    echo "Volume '${volume_name}' not found. Creating it now..."
    docker volume create "${volume_name}"
    echo "Volume '${volume_name}' created successfully."
  else
    echo "Volume '${volume_name}' already exists. Skipping creation."
  fi
}

# --- Main execution ---
echo "Setting up required Docker volumes..."
create_docker_volume "model_cache"
create_docker_volume "ollama_models" # As seen in your docker-compose.yaml

echo "Setup complete. You can now run 'make dev' or 'make prod' etc."