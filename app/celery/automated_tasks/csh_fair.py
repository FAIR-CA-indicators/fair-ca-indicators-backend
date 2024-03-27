import re
import requests

#from typing import Optional

from .csh_helpers import check_route
from app.dependencies.settings import get_settings
#from ... import models

from app.celery.celery_app import app

config = get_settings()

def is_doi(identifier: str):
    doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
    # Use the re.match function to check if the string matches the pattern
    print("identifier: ", identifier)
    match = re.match(doi_pattern, identifier)
    print("?? match")
    print("doi match: ", match)
    return False
    #return bool(re.match(doi_pattern, identifier))



def incoperate_results(task_dict: dict, result: 'app.models.TaskStatus', test: bool):
    import app.models #dynamic import
 
    session_id = task_dict["session_id"]
    task_id = task_dict["id"]

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
        print(f"--Patching {url}", status.dict())
        try:
            # Send PATCH request
            response = requests.patch(
                url,
                json=status.dict(),
            )
            response.raise_for_status()  # Raise exception for non-2xx response status codes
            print("---->", response.text, "<----")
            print("PATCH request successful")

        except requests.RequestException as e:
            # Handle request-related exceptions
            print(f"Error sending PATCH request: {e}")

            # Optionally, raise the exception to propagate it further
            # raise

        except Exception as e:
            # Handle other types of exceptions
            print(f"An unexpected error occurred: {e}")

            # Optionally, raise the exception to propagate it further
            # raise

    
    # Does not work because celery does not have access to fair_indicators
    # routers.update_task(session_id, task_id, status)

    # Works, but does not trigger updating of children
    # redis_app.json().set(f"session:{session_id}", f".tasks.{task_id}.status", obj=result)

@app.task
def csh_f1_2_globally_unique_identifier(task_dict: dict, data: dict, test: bool = False):
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

        print("CHECK!! globally uni ")
        identifier = check_route(data, ["resource", "resource_identifier"])
        print("grabbed identifier: ", identifier)
        #could also retrive "type" from data instead of using .startswith
        if(identifier is False):
            result = "failed"
        elif(is_doi(identifier)):
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
    print("working?")

@app.task
def csh_i3_01_ref_other_metadata(task_dict: dict, data: dict, test: bool = False):
    #check if other metadata is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    print("INFO - csh-i3-01")
    result = "not_applicable"
    if(ref_resources != False):
        print("IDs: ", ref_resources, type(ref_resources))
        for res in ref_resources:
            print(res, type(res))
            print(res.get('typeGeneral'))
            if(res.get('typeGeneral') != 'Dataset'):
                result = "success"
    incoperate_results(task_dict, result, test)

@app.task
def csh_i3_02_ref_other_data(task_dict: dict, data: dict, test: bool = False):
    #check if other data is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    print("INFO - csh-i3-02")
    result = "not_applicable"
    if(ref_resources != False):
        for res in ref_resources:
            print(res)
            print(res.get('typeGeneral'))
            if(res.get('typeGeneral') == 'Dataset'):
                result = "success"
    incoperate_results(task_dict, result, test)

@app.task
def csh_i3_03_qual_ref_other_metadata(task_dict: dict, data: dict, test: bool = False):
    #check if other metadata is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    print("INFO - csh-i3-03")
    result = "not_applicable"
    if(ref_resources != False):
        for res in ref_resources:
            if(res.get('typeGeneral') != 'Dataset'):
                #set to fail if ONE refed metadata has no relationType
                if(result == "not_applicable"):
                    result = "success"
                if(res.get('relationType') == None):
                    result = "failed"
    print("sollte jetzt das ergebnis in die session schreiben")
    incoperate_results(task_dict, result, test)

@app.task
def csh_i3_04_qual_ref_other_data(task_dict: dict, data: dict, test: bool = False):
    #check if other data is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    print("INFO - csh-i3-04")
    result = "not_applicable"
    if(ref_resources != False):
        for res in ref_resources:
            if(res.get('typeGeneral') == 'Dataset'):
                #set to fail if ONE refed metadata has no relationType
                if(result == "not_applicable"):
                    result = "success"
                if(res.get('relationType') == None):
                    result = "failed"
    incoperate_results(task_dict, result, test)

##### Reusability
@app.task
def csh_r1_1_01_has_reuse_license(task_dict: dict, data: dict, test: bool = False):
    print("CHECK! has reuse license")
    resource_type = check_route(data, ["resource", "classification", "type"])
    if(resource_type == False): resource_type = check_route(data, ["resource", "resource_classification", "resource_type"])
    if(resource_type in ["Study", "Substudy/Data collection event"]):
        result = "warning" #TODO: Ask others to specify how this can be checked
    else:
        license_info = check_route(data, ["resource", "nonStudyDetails", "useRights"])
        if(license_info != False):
            result = "success"
        else:
            result = "failed"
    incoperate_results(task_dict, result, test)

@app.task #TODO: verify if this automated task really works since it depends on a parent task
def csh_r1_1_02_has_standard_reuse_license(task_dict: dict, data: dict, test: bool = False):
    #check if userights label is a fitting license
    license_label  = check_route(data,["resource", "nonStudyDetails", "nonStudyDetails", "useRights"])
    if(license_label in ["Creative Commons Zero v1.0 Universal", "Creative Commons Attribution 4.0 International", "Creative Commons Attribution Non Commercial 4.0 International", "Creative Commons Attribution Share Alike 4.0 International", "Creative Commons Attribution Non Commercial Share Alike 4.0 International"]):
        result = "success"
    elif(license_label == "Other"):
        result = "warning"
    else:
        result = "failed"
    incoperate_results(task_dict, result, test)

