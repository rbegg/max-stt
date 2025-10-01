import asyncio
import logging
import numpy as np
from faster_whisper import WhisperModel


async def process_audio_chunk(model: WhisperModel, audio_chunk: bytes) -> str:
    """
    Processes a single chunk of audio data with an assumed format of 32bit float pcm.

    This function takes a raw audio chunk, creates a numpy array and then
    transcribes it using the provided Whisper model instance.

    Args:
        model: The pre-loaded faster_whisper model.
        audio_chunk: The binary audio data to process.

    Returns:
        A string containing the transcribed text, or an empty string on error.
    """
    if not model:
        logging.error("Model is not loaded.")
        return ""
    try:

        logging.info(f"Processing audio chunk len = {len(audio_chunk)}.")
        audio_np = np.frombuffer(audio_chunk, dtype=np.float32)

        # Transcribe the audio using the Whisper model.
        segments, _ = model.transcribe(audio_np, vad_filter=True)
        transcription = ""
        for segment in segments:
            logging.debug(f"Segment: {segment}")
            transcription += segment.text

        return transcription.strip()

    except Exception as e:
        logging.error(f"Error in audio processing: {e}")
        return ""
