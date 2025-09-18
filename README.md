# Real-time Speech-to-Text Server

This project provides a real-time speech-to-text (STT) service using the `faster-whisper` library. The application is
built with Python, utilizing `aiohttp` for an asynchronous web server and websockets for real-time communication. The
entire application is containerized with Docker for easy setup, development, and deployment.

## Features

- **Real-time Transcription**: Transcribes audio streams in real-time through a WebSocket connection.
- **High-Performance Model**: Powered by `faster-whisper`, a fast and efficient implementation of OpenAI's Whisper
  model.
- **Containerized**: Fully containerized with Docker and Docker Compose, providing consistent environments for
  development and production.
- **GPU Support**: Optimized for NVIDIA GPUs (CUDA) for high-performance transcription, with a fallback to CPU.
- **Simple Web Interface**: Includes a basic web client for demonstrating and testing the real-time transcription.
- **Easy Management**: A `Makefile` is included with commands to simplify building, running, and managing the
  application stacks.

## How It Works

1. **Client-Side**: A web page (`index.html`) uses JavaScript and the `vad-web` library for Voice Activity Detection (
   VAD). When the user speaks, audio chunks are captured, encoded as WAV, and sent to the server via a WebSocket.
2. **Backend Server**: The `aiohttp` server listens for WebSocket connections. When an audio chunk is received, it's
   processed by the `audio_processor`.
3. **Audio Processing**: The audio is resampled to a 16kHz mono channel format using `ffmpeg`.
4. **Transcription**: The processed audio is then passed to the pre-loaded `faster-whisper` model for transcription.
5. **Response**: The resulting text is sent back to the client through the WebSocket and displayed on the page.

## Project Structure

## Getting Started

### Prerequisites

- Docker and Docker Compose
- `make` (optional, for convenience)
- NVIDIA drivers installed on the host machine (for GPU support)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create the model cache volume:**
   This script creates a Docker volume to cache the downloaded Whisper model, preventing re-downloads every time the
   container starts. Beware that cache is shared between dev and production containers, the cache should be cleared in a
   final production environment.
   ```bash
   bash setup.sh
   ```

### Development Environment

The development environment uses a bind-mount for the source code. The container starts without running the application,
allowing you to attach to it and run the server manually.

1. **Build and start the container:**
   ```bash
   make dev
   ```

2. **Access the application:**
   In a new terminal, run the following command to get an interactive shell:
   ```bash
   make dev-shell
   ```

3. **Run the application:**
   Once inside the container's shell, you have two options to run the server:

    * **Standard execution:**
      ```bash
      python src/app.py
      ```

    * **With hot-reloading (`adev`):** For a better development experience, `aiohttp-devtools` is included. You can use
      `adev` to automatically restart the server when code changes are detected.
      ```bash
      adev runserver src/app.py
      ```

4. **Access the application:**
   Once the server is running, open your browser and navigate to `http://localhost:8765`.

5. **Stop the services:**
   When you are done, run this command from your host machine (not inside the container shell):
   ```bash
   make dev-down
   ```

### Using the Dev Container with an IDE (Optional)

This project is configured with a [Dev Container](https://containers.dev/), allowing you to develop inside a Docker
container with your IDE. This provides a consistent and fully-configured development environment.

#### Visual Studio Code

1. Make sure you have
   the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   installed.
2. Open the project folder in VS Code.
3. A notification will appear asking if you want to "Reopen in Container." Click it.
4. VS Code will build the dev container and connect to it. Your terminal, debugger, and all other tools will now run
   inside the containerized environment. You can then run the application as described in the "Development Environment"
   section from the integrated terminal.

#### PyCharm Professional

The `devcontainer.json` is also configured for use with PyCharm Professional.

1. Open the project folder in PyCharm.
2. PyCharm should automatically detect the `.devcontainer/devcontainer.json` file and suggest creating a Dev Container
   interpreter.
3. Follow the prompts to let PyCharm build the environment based on the `docker-compose.dev.yaml` service.
4. Once the interpreter is set up, you can create a new "Python" Run/Debug Configuration for `src/app.py` and run or
   debug your application directly from the IDE.

### Production Environment

The production environment builds a self-contained, optimized image and runs it in detached mode.

1. **Build and start the services:**
   ```bash
   make prod
   ```

2. **Access the application:**
   Open your browser and navigate to `http://localhost:80`.

3. **View logs:**
   ```bash
   make prod-logs
   ```

4. **Stop the services:**
   ```bash
   make prod-down
   ```

## Configuration

The application can be configured using environment variables set in the `docker-compose.yaml` file.

- `MODEL_SIZE`: The Whisper model to use (e.g., `tiny.en`, `base`, `small`, `medium`, `large-v3`).
- `DEVICE`: The device to run the model on (`cuda` or `cpu`).
- `COMPUTE_TYPE`: The computation type for the model (e.g., `float16`, `int8`).

To switch to a CPU-only setup, comment out the `deploy` section in `docker-compose.yaml` and update the environment
variables:

## Makefile Commands

The following commands are available in the `Makefile`:

- `make dev`: Builds and starts the development containers.
- `make dev-down`: Stops the development containers.
- `make dev-shell`: Opens an interactive shell in the running `app` container.
- `make prod`: Builds and starts the production containers in detached mode.
- `make prod-down`: Stops the production containers.
- `make prod-logs`: Tails the logs of the production container.
- `make prod-shell`: Opens an interactive shell in the production `app` container.
- `make clean`: Stops all containers and removes associated volumes (useful for a fresh start).

## OpenAI Real-time Client

The project also includes `realtime_transcription_client.py`, which is an example client for connecting to OpenAI's
real-time transcription API. It is separate from the main `faster-whisper` application and demonstrates an alternative
approach to real-time STT. It requires `sounddevice` and the `openai` library.