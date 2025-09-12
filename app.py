import os
import asyncio
import logging
from aiohttp import web
from faster_whisper import WhisperModel
import numpy as np

# --- Configuration ---
# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Environment variables for model configuration
MODEL_SIZE = os.environ.get("MODEL_SIZE", "base")
DEVICE = os.environ.get("DEVICE", "cpu")
COMPUTE_TYPE = os.environ.get("COMPUTE_TYPE", "int8")

# --- Whisper Model Loading ---
# This is a global variable to hold the model.
model = None


def load_model():
    """
    Loads the Whisper model into the global 'model' variable.
    """
    global model
    cleaned_model_name = MODEL_SIZE.split('/')[-1].replace('faster-whisper-', '')

    logging.info(f"Loading model: {cleaned_model_name} on device: {DEVICE} with compute_type: {COMPUTE_TYPE}")
    try:
        model = WhisperModel(cleaned_model_name, device=DEVICE, compute_type=COMPUTE_TYPE)
        logging.info("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load Whisper model: {e}")
        exit(1)


# --- Audio Processing ---
async def process_audio_chunk(audio_chunk):
    """
    Processes a single chunk of audio data using FFmpeg and Whisper.
    """
    try:
        # Define the FFmpeg command for audio conversion.
        ffmpeg_command = [
            "ffmpeg", "-f", "wav", "-i", "pipe:0", "-f", "s16le",
            "-ac", "1", "-ar", "16000", "pipe:1"
        ]
        proc = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate(input=audio_chunk)

        if proc.returncode != 0:
            logging.error(f"FFmpeg error: {stderr.decode()}")
            return ""

        audio_np = np.frombuffer(stdout, dtype=np.int16).astype(np.float32) / 32768.0
        segments, _ = model.transcribe(audio_np, vad_filter=True)
        transcription = " ".join(segment.text for segment in segments)
        return transcription.strip()

    except Exception as e:
        logging.error(f"Error in audio processing: {e}")
        return ""


# --- Web Server Handlers ---
async def handle_favicon(request):
    """Handles requests for favicon.ico to prevent 404 errors."""
    return web.Response(status=204)  # 204 No Content


async def handle_http(request):
    """Serves the index.html file."""
    logging.info("HTTP request received, serving index.html.")
    try:
        return web.FileResponse('./index.html')
    except Exception as e:
        logging.error(f"Error serving index.html: {e}")
        return web.Response(status=500, text="Internal Server Error: Could not serve index.html.")


async def handle_websocket(request):
    """Handles the WebSocket connection for audio streaming."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logging.info("WebSocket connection established.")

    last_processed_chunk = None
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.BINARY:
                audio_chunk = msg.data
                if audio_chunk == last_processed_chunk:
                    continue
                last_processed_chunk = audio_chunk

                transcription = await process_audio_chunk(audio_chunk)
                if transcription:
                    await ws.send_str(transcription)
            elif msg.type == web.WSMsgType.ERROR:
                logging.error(f"WebSocket connection closed with exception {ws.exception()}")
    except Exception as e:
        logging.error(f"An error occurred in the WebSocket handler: {e}")
    finally:
        logging.info("WebSocket connection closed.")
        await ws.close()

    return ws


# --- Main Application Setup ---
async def main():
    load_model()
    app = web.Application()
    # Route for the main page, favicon, and the WebSocket endpoint
    app.router.add_get('/', handle_http)
    app.router.add_get('/favicon.ico', handle_favicon)
    app.router.add_get('/ws', handle_websocket)

    host = "0.0.0.0"
    port = 8765

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logging.info(f"Server started at http://{host}:{port}")
    # Keep the server running forever
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down.")

