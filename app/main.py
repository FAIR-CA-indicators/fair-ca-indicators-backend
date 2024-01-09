from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers.router import base_router
from app.metrics.assessments_lifespan import get_tasks_definitions
from app.dependencies.settings import get_settings


tags_metadata = [
    {
        "name": "Indicators",
        "description": "FAIR assessments. Endpoints to retrieve the descriptions of the assessments done by "
        "the application "
        "to evaluate how FAIR a resource is/",
    },
    {
        "name": "Tasks",
        "description": "FAIR Combine tasks. Endpoints allow to retrieve the details of a specific assessment "
        "associated with a session, "
        "to update an assessment status or to retrieve the documentation of FAIR Combine assessments.",
    },
    {
        "name": "Sessions",
        "description": "FAIR Combine assessment session. Endpoints to create a new session, to load a previously "
        "exported session, "
        "or to display the details of an existing session.",
    },
]

description = """
FAIR Eval is a web application designed to help users assess how FAIR their
their scientific resources are. Currently supported are FAIR Combine and CSH resources.

Users may submit their Combine model, and the application will create a list
of assessments following the FAIR principle. Some of these assessments will run
in the background while others will need to be filled by the users.
Users may also make API requests to evalutate the metadata of a CSH resource.

Once all assessments are completed, the application returns a set of scores
describing how FAIR their resource is.
"""


app = FastAPI(
    title="FAIR Eval API",
    description=description,
    version="0.1.0",
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


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse("/redoc")
