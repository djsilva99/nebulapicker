import logging

from fastapi import FastAPI

from .adapters.entrypoints.v1.models.logs import APILog
from .adapters.entrypoints.v1.models.welcome import WelcomeResponse
from .settings import Settings

# CONSTANTS
settings: Settings = Settings()


# LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# API
app = FastAPI()


@app.get("/")
def welcome():
    message_collection = WelcomeResponse()
    logger.info(
        APILog.WELCOME_SUCCESS,
    )
    return message_collection
