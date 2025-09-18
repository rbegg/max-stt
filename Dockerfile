# syntax=docker/dockerfile:1
# This first line enables the BuildKit features like cache mounts.

# Expects PYTHON_VERSION to be set in a compose file
ARG PYTHON_VERSION
ARG BASE_IMAGE=nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

# ---- Base Stage ----
# Use the official NVIDIA CUDA development image as a base
FROM ${BASE_IMAGE} as base
ARG PYTHON_VERSION
RUN echo "The Python version is set to: python${PYTHON_VERSION}"

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set environment variables for default execution
ENV DEVICE=cuda
ENV COMPUTE_TYPE=float16

# Set the working directory
WORKDIR /app

## Copy the entrypoint script into a known location
## and ensure it's owned by the correct user.
#COPY --chown=appuser:appuser entrypoint.sh /usr/local/bin/
#
## Set the script as the entrypoint for the container
#ENTRYPOINT ["entrypoint.sh"]

# Prevent tzdata from asking for input during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies: Python, pip, ffmpeg
RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a standard symlink for the python executable for robustness
RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

# Create a non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

#Define volume used for model cache
VOLUME /home/appuser/.cache
# Create the directory and then change its ownership in one step
RUN mkdir -p /home/appuser/.cache && chown -R appuser:appuser /home/appuser/.cache

# ---- Builder Stage ----
# This stage installs dependencies into a temporary venv.
# The result is cached and reused by dev and prod, speeding up builds.
FROM base as builder
ARG PYTHON_VERSION
# Copy the requirements file
COPY --chown=appuser:appuser requirements.txt .

# Set the PATH to include the workspace venv for this stage
ENV PATH="/app/.venv/bin:$PATH"

# Use a cache mount to speed up pip installs across builds
# Create the venv at its final destination and install packages
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /app/.venv && \
    pip install --no-cache-dir -r requirements.txt



# ---- Development Stage ----
# Sets up a container for interactive development with tools and mounted source code.
FROM base as dev
ARG PYTHON_VERSION

USER root

# Install system dependencies for dev only
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*


# Set the PATH to include the workspace venv
ENV PATH="/app/.venv/bin:$PATH"

# Create the venv and copy pre-installed packages from the builder stage
RUN python${PYTHON_VERSION} -m venv /app/.venv
COPY --chown=appuser:appuser --from=builder /app/.venv /app/.venv

USER appuser

# Install development-specific dependencies
#RUN pip install --no-cache-dir "pylint" "pytest" "black"

# Activate the venv by default in the bash shell
RUN echo "source /app/.venv/bin/activate" >> /home/appuser/.bashrc

# Keep the container running to allow for interactive development
CMD ["sleep", "infinity"]


# ---- Production Stage ----
# Create and activate a virtual environment
FROM base as prod
ENV PATH="/opt/venv/bin:$PATH"

# Copy the pre-built and correctly configured venv from the builder stage
COPY --chown=appuser:appuser --from=builder /app/.venv /opt/venv

# Copy the application src
COPY --chown=appuser:appuser src/ ./src

RUN mkdir -p /etc/letsencrypt

# Expose the port the app runs on
EXPOSE 8765

USER appuser

# Run the application
CMD ["python", "src/app.py"]

