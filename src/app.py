import logging
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
from . import config
from .audio_processor import process_audio_chunk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to hold the Whisper model instance
model: WhisperModel | None = None

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Loads the Whisper model into a global variable during application startup.
    This is executed once when the FastAPI application starts.
    """
    global model
    model_name = config.MODEL_SIZE.split('/')[-1].replace('faster-whisper-', '')

    logging.info(
        f"Loading model: {model_name} on device: {config.DEVICE} "
        f"with compute_type: {config.COMPUTE_TYPE}"
    )
    try:
        model = WhisperModel(
            model_name,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE
        )
        logging.info("Model loaded and ready.")
    except Exception as e:
        logging.error(f"Failed to load Whisper model: {e}")
        # Exit if the model fails to load, as the app is non-functional.
        exit(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for real-time audio transcription.
    It accepts a connection, receives audio chunks, processes them,
    and sends back transcriptions.
    """
    await websocket.accept()
    logging.info("WebSocket connection established.")

    last_processed_chunk = None
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()

            # Basic debouncing to avoid processing the same chunk multiple times
            if audio_chunk == last_processed_chunk:
                continue
            last_processed_chunk = audio_chunk

            # Process the audio chunk using the globally loaded model
            transcription = await process_audio_chunk(model, audio_chunk)

            # Send the transcription result back to the client
            if transcription:
                response_data = {
                    "type": "transcription",
                    "source": "user",
                    "data": transcription,
                }
                await websocket.send_text(json.dumps(response_data))


    except WebSocketDisconnect:
        logging.info("WebSocket connection closed.")
    except Exception as e:
        logging.error(f"An error occurred in the WebSocket handler: {e}")

if __name__ == "__main__":
    """
    Allows running the app directly with `python -m src.app` for development.
    """
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)