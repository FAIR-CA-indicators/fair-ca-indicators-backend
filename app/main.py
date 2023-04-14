from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.router import base_router
from app.metrics.assessments_lifespan import get_tasks_definitions
from app.dependencies.settings import get_settings


tags_metadata = [
    {
        "name": "Indicators",
        "description": "FAIR Combine assessments. Endpoints to retrieve the descriptions of the assessments done by the application "
                       "to evaluate how FAIR a resource is/"
    },
    {
        "name": "Tasks",
        "description": "FAIR Combine tasks. Endpoints allow to retrieve the details of a specific assessment associated with a session, "
                       "to update an assessment status or to retrieve the documentation of FAIR Combine assessments."
    },
    {
        "name": "Sessions",
        "description": "FAIR Combine assessment session. Endpoints to create a new session, to load a previously exported session, "
                       "or to display the details of an existing session."
    },

]

description = """
FAIR Combine is a web application designed to help users assess how FAIR their
their Combine resources are.

Users may submit their Combine model, and the application will create a list
of assessments following the FAIR principle. Some of these assessments will run
in the background while others will need to be filled by the users.

Once all assessments are completed, the application returns a set of scores
describing how FAIR their model is.
"""


app = FastAPI(
    title="FAIR Combine API",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
    lifespan=get_tasks_definitions,
)
app.include_router(base_router)

config = get_settings()
origins = config.allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
