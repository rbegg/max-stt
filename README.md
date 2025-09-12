# **Streaming Speech-to-Text with faster-whisper**

This project sets up a real-time speech-to-text server using faster-whisper. 
It is configured by default to run on a compatible NVIDIA GPU for high performance and serves its own web client, 
making it fully self-contained.

## **Prerequisites**

* Docker and Docker Compose  
* **For GPU operation (default):** NVIDIA drivers and the 
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) 
installed on the host machine.

## **How to Run (GPU \- Default)**

1. Check `docker-compose.yml`:  
   Ensure your `docker-compose.yml` is configured for your GPU. The default is `float16` compute type, 
   which is ideal for modern GPUs. You may want to change the `MODEL_SIZE` environment variable to a different model.  
```yaml
   environment:
     - DEVICE=cuda  
     - COMPUTE_TYPE=float16  
     - MODEL_SIZE=large-v3
```
2. **Build and run the container:**  
   `docker-compose up \--build`

3. Open the application:  
   Navigate to `http://localhost:8765` in your web browser.

## **How to Run (CPU-Only)**

If you don't have a compatible GPU, you can easily switch to CPU mode.

1. **Modify docker-compose.yml:**  
   * Comment out the `deploy` section.  
   * Change the `environment` variables to use the CPU settings.
   * Your `docker-compose.yml` should look like this for a CPU setup:
```yaml
  services:
    streaming-asr-app:  
    build: .  
    ports:  
      \- "8765:8765"  
    environment:  
      # \--- CPU Configuration \---  
      - DEVICE=cpu  
      - COMPUTE\_TYPE=int8  
      - MODEL\_SIZE=base \# Using a smaller model is recommended for CPU
    
    volumes:  
      - ./model\_cache:/root/.cache/huggingface/hub
    
    # --- GPU Deployment (Commented out for CPU) ---  
    # deploy:  
    #   resources:  
    #     reservations:  
    #       devices:  
    #         \- driver: nvidia  
    #           count: 1  
    #           capabilities: \[gpu\]
```

2. **Rebuild and run:**  
```yaml
   docker-compose up \--build
```
   The application will now run in CPU-only mode. Access it at the same address: http://localhost:8765.

## **Persisting the Model Cache**

The model is automatically cached in a local ./model\_cache folder, thanks to the volumes configuration in docker-compose.yml. This prevents re-downloading the model on subsequent builds.