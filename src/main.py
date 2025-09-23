import uvicorn
import json
import asyncio
import logging
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
from . import config

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    model_name = config.MODEL_SIZE.split('/')[-1].replace('faster-whisper-', '')
    logging.info(f"Loading model: {model_name}...")
    try:
        model = WhisperModel(config.MODEL_SIZE, device=config.DEVICE, compute_type=config.COMPUTE_TYPE)
        app.state.whisper_model = model
        logging.info("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load Whisper model: {e}")
        exit(1)


@app.websocket("/ws")
async def websocket_stt_endpoint(websocket: WebSocket):
    await websocket.accept()
    model = websocket.app.state.whisper_model
    logging.info("STT WebSocket connection established.")
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0

            segments, _ = model.transcribe(audio_np, vad_filter=True, word_timestamps=False)

            segment_list = list(segments)

            if not segment_list:
                await websocket.send_text(json.dumps({"transcript": "", "final": True}))
                continue

            transcript_parts = []
            for i, segment in enumerate(segment_list):
                transcript_parts.append(segment.text)
                current_transcript = "".join(transcript_parts)
                is_final = (i == len(segment_list) - 1)

                response = {"transcript": current_transcript, "final": is_final}
                await websocket.send_text(json.dumps(response))
                await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        logging.info("STT WebSocket connection closed.")
    except Exception as e:
        logging.error(f"STT Error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)