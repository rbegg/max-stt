import logging
from aiohttp import web
from .audio_processor import process_audio_chunk

async def handle_favicon(request):
    """
    Handler to respond to favicon requests with a "No Content" status,
    preventing unnecessary 404 errors in the logs.
    """
    return web.Response(status=204)

async def handle_http(request):
    """
    Serves the main `index.html` file for HTTP GET requests to the root URL.
    """
    logging.info("HTTP request received, serving index.html.")
    try:
        # Note: Ensure the path to index.html is correct based on your project structure.
        # This assumes index.html is in a 'src' directory relative to where you run the app.
        return web.FileResponse('./src/index.html')
    except Exception as e:
        logging.error(f"Error serving index.html: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def handle_websocket(request):
    """
    Manages the WebSocket connection for real-time audio transcription.
    It receives audio chunks, processes them, and sends back the transcription.
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logging.info("WebSocket connection established.")

    last_processed_chunk = None
    try:
        # Asynchronously iterate over messages from the WebSocket client.
        async for msg in ws:
            if msg.type == web.WSMsgType.BINARY:
                audio_chunk = msg.data

                # Avoid reprocessing the same chunk if sent multiple times.
                if audio_chunk == last_processed_chunk:
                    continue
                last_processed_chunk = audio_chunk

                # Call the audio processing function.
                transcription = await process_audio_chunk(request, audio_chunk)

                # Send the transcription back to the client if it's not empty.
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
