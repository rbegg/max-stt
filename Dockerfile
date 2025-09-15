# Use the official NVIDIA CUDA development image as a base
FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

# Set environment variables for default execution
ENV DEVICE=cuda
ENV COMPUTE_TYPE=float16

# Set the working directory
WORKDIR /app

# Prevent tzdata from asking for input during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies: Python, pip, ffmpeg
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file
COPY requirements.txt .

# Install Python packages into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application src
COPY src/ ./src

# Expose the port the app runs on
EXPOSE 8765

# Run the application
CMD ["python", "src/app.py"]

