import os
import logging

# --- Logging Configuration ---
# Sets up the basic logging format and level for the application.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Model Configuration ---
# These environment variables control which model is loaded and how it's run.
MODEL_SIZE = os.environ.get("MODEL_SIZE", "base")
DEVICE = os.environ.get("DEVICE", "cpu")
COMPUTE_TYPE = os.environ.get("COMPUTE_TYPE", "int8")

# --- Server Configuration ---
# Defines the host and port for the web-server.
HOST = "0.0.0.0"
PORT = 80
