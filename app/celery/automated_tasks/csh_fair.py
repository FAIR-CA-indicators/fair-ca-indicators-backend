import re
import requests

#from typing import Optional

from .csh_helpers import check_route
from app.dependencies.settings import get_settings
#from ... import models

from app.celery.celery_app import app

config = get_settings()

def is_doi(identifier):
    doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
    # Use the re.match function to check if the string matches the pattern
    return bool(re.match(doi_pattern, identifier))



def incoperate_results(task_dict: dict, result: 'app.models.TaskStatus', test: bool):
    import app.models #dynamic import

    print("incoperate results!")
    session_id = task_dict["session_id"]
    task_id = task_dict["id"]

    print(config.celery_key)
    status = app.models.TaskStatusIn(
        status= app.models.TaskStatus(result), force_update=config.celery_key
    )

    print(f"Task status computed: {result}")
    # Needs to send a request for the task to be updated
    if test:
        print("test is true")
        return app.models.TaskStatus(result)
    else:
        url = f"http://{config.backend_url}:{config.backend_port}/session/{session_id}/tasks/{task_id}"
        print(f"Patching {url}")
        requests.patch(
            url,
            json=status.dict(),
        )

    # Does not work because celery does not have access to fair_indicators
    # routers.update_task(session_id, task_id, status)

    # Works, but does not trigger updating of children
    # redis_app.json().set(f"session:{session_id}", f".tasks.{task_id}.status", obj=result)



@app.task
def csh_f1_2_globally_unique_identifier(
    task_dict: dict, data: dict, test: bool = False
):
        print("f1_2_glob")
        """
        Representation of celery task to evaluate an assessment.
        These celery tasks should be in the format:
        ```
        def assessment_task(task_dict: dict, data: dict) -> None:
            session_id = task_dict["session_id"]
            task_id = task_dict["id"]

            # Code to get the final TaskStatus
            ...

            status = models.TaskStatusIn(status=models.TaskStatus(result), force_update=config.celery_key)
            requests.patch(
                f"http://localhost:8000/session/{session_id}/tasks/{task_id},
                json=status
            )

        :param task_dict: Task dict representation
        :param data: (Meta)Data to evaluate
        :return: None
        """


        identifier = check_route(data, ["resource", "resource_identifier"])

        #could also retrive "type" from data instead of using .startswith

        if(is_doi(identifier)):
            result = "success"
        elif(identifier.startswith("DRKS")):
            result = "success"    
        else:
            result = "failed"
        
        incoperate_results(task_dict, result, test)


# @app.task
# def csh_f1_1_persistent_identifier(task_dict: dict, data: dict, test: bool = False):
    
#     """
#     Task to test weather an identifier is persistent.
#     Since the identifier is either unique for CSH, it is persistent
#     """

#     result = "success"

#     incoperate_results(task_dict, result, test)

# @app.task
# def csh_f2_rich_metadata_provided(task_dict: dict, data: dict, test: bool = False):
#     """
#     The nature of the CSH with all its mandatory fields implies a success
#     """

#     result = "success"

#     incoperate_results(task_dict, result, test)

# @app.task
# def csh_f3_id_of_do_included(task_dict: dict, data: dict, test: bool = False):
#     """
#     we are unsure about this indicator. At the moment we consider it as a fail
#     """

#     result = "success"

#     incoperate_results(task_dict, result, test)


# @app.task
# def csh_f4_metadata_indexed(task_dict: dict, data: dict, test: bool = False):
#     """
#     since the data is send to out tool as a json it clearly is indexed
#     """

#     result = "success"

#     incoperate_results(task_dict, result, test)

@app.task
def csh_a1_contains_access_information(task_dict: dict, data: dict, test: bool = False):
    """
    1. check if there is a data sharing plan (study_data_sharing_plan_generally)
    2. if yes -> evaluate ‘study_data_sharing_plan_time_frame’ and ‘study_data_sharing_plan_access_criteria’ somehow
    """
    general_plan = check_route(data, ["resource","study_design","study_data_sharing_plan","study_data_sharing_plan_description"])
    print("INFO - general plan - ", general_plan)

    has_plan = general_plan == "Yes, there is a plan to make data available"

    if has_plan:
        print("TODO: implent a check of the actual data sharing plan")
        result = "success"
    else:
        result = "failed"

    incoperate_results(task_dict, result, test)