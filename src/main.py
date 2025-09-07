import logging

from fastapi import Depends, FastAPI

from src.adapters.entrypoints.v1.models.logs import APILog
from src.adapters.entrypoints.v1.models.source import (
    GetAllSourcesResponse,
    map_source_list_to_get_all_sources_response,
)
from src.adapters.entrypoints.v1.models.welcome import WelcomeResponse
from src.configs.dependencies.services import get_source_service
from src.configs.settings import Settings
from src.domain.services.source_service import SourceService

# CONSTANTS
settings: Settings = Settings()


# LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# API
app = FastAPI()


@app.get("/v1")
def welcome():
    message_collection = WelcomeResponse()
    logger.info(
        APILog.WELCOME_SUCCESS,
    )
    return message_collection

@app.get("/v1/sources")
def list_sources(
    source_service: SourceService = Depends(get_source_service) # noqa: B008
):
    source_list = source_service.get_all_sources()
    return GetAllSourcesResponse(
        sources=map_source_list_to_get_all_sources_response(
            source_list=source_list
        )
    )
