import logging
from aiohttp import web
from faster_whisper import WhisperModel
from . import config
from .handlers import handle_http, handle_favicon, handle_websocket


async def startup_model(app):
    """
    Loads the Whisper model during application startup.

    This function is executed once per worker process when the application starts.
    It initializes the WhisperModel and attaches it to the application instance
    so it can be accessed from request handlers.
    """
    # Clean the model name for faster_whisper.
    model_name = config.MODEL_SIZE.split('/')[-1].replace('faster-whisper-', '')

    logging.info(
        f"Loading model: {model_name} on device: {config.DEVICE} "
        f"with compute_type: {config.COMPUTE_TYPE}"
    )
    try:
        # Initialize the model with settings from the config file.
        model = WhisperModel(
            model_name,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE
        )
        app['whisper_model'] = model
        logging.info("Model loaded and attached to app context successfully.")
    except Exception as e:
        logging.error(f"Failed to load Whisper model: {e}")
        # Exit if the model fails to load, as the app cannot function.
        exit(1)


async def init_app():
    """
    Initializes and configures the aiohttp web-server application.

    This factory function creates the web-server.Application object, registers the
    model loading function to run on startup, and sets up the routes by
    connecting URLs to their respective handlers.
    """
    app = web.Application()

    # Register the model loading function to run at startup.
    app.on_startup.append(startup_model)

    # Add routes from the handlers module.
    app.router.add_get('/', handle_http)
    app.router.add_get('/favicon.ico', handle_favicon)
    app.router.add_get('/ws', handle_websocket)

    return app


if __name__ == "__main__":
    """
    Main execution block to run the application.
    This allows you to start the server directly by running `python app.py`.
    """
    # Create the application instance.
    app = init_app()

    # Run the web-server server with settings from the config file.
    web.run_app(app, host=config.HOST, port=config.PORT)
