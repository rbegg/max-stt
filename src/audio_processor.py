import asyncio
import logging
import numpy as np
from faster_whisper import WhisperModel


async def process_audio_chunk(model: WhisperModel, audio_chunk: bytes) -> str:
    """
    Processes a single chunk of audio data using FFmpeg and the Whisper model.

    This function takes a raw audio chunk, resamples it using FFmpeg, and then
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
        # Command to convert incoming audio to 16-bit mono PCM at 16kHz.
        ffmpeg_command = [
            "ffmpeg", "-f", "wav", "-i", "pipe:0", "-f", "s16le",
            "-ac", "1", "-ar", "16000", "pipe:1"
        ]

        # Execute the FFmpeg command as a subprocess.
        proc = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Pipe the audio chunk to FFmpeg and get the processed output.
        stdout, stderr = await proc.communicate(input=audio_chunk)

        if proc.returncode != 0:
            # Log any errors from FFmpeg.
            logging.error(f"FFmpeg error: {stderr.decode()}")
            return ""

        # Convert the raw audio buffer to a NumPy array suitable for the model.
        audio_np = np.frombuffer(stdout, dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe the audio using the Whisper model.
        segments, _ = model.transcribe(audio_np, vad_filter=True)
        transcription = " ".join(segment.text for segment in segments)

        return transcription.strip()

    except Exception as e:
        logging.error(f"Error in audio processing: {e}")
        return ""
