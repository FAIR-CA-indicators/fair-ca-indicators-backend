import re
import requests

#from typing import Optional

from .hsh_helpers import check_route, check_list, is_url_reachable
from app.dependencies.settings import get_settings
#from ... import models

from app.celery.celery_app import app

config = get_settings()

def is_doi(identifier: str):
    doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
    # Use the re.match function to check if the string matches the pattern
    match = bool(re.match(doi_pattern, identifier))
    print("ITS A MATCH? ", match, identifier)
    #return False
    return bool(match)



def incoperate_results(task_dict: dict, result: 'app.models.TaskStatus', test: bool): ## shouldn't app.models.TaskStaus be used without ' ?
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
            #print("---->", response.text, "<----")
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
def hsh_f1_1_persistent_identifier(task_dict: dict, data: dict, test: bool = False):
    """
    check if metadata has: resource > identifier attribute
    """
    identifier = check_route(data, ["resource", "identifier"])
    print("ID: ", identifier)
    if identifier:
        result = "success"
    else:
        result = "failed"

    incoperate_results(task_dict, result, test)


@app.task
def hsh_f1_2_globally_unique_identifier(task_dict: dict, data: dict, test: bool = False):
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

        Common schemes: DOI (is an implementation of Handle, the first part defines the namespace), arXiv (e.g. https://arxiv.org/abs/2404.00156), EISSN (electronic ISSN), Handle, ISTC (standard withdrawn), LISS, LSID (urn:lsid:⟨Authority⟩:⟨Namespace⟩:⟨ObjectID⟩[:⟨Version⟩]; unsure ), PMID, PURL, URN, w3id
        """
        identifier = check_route(data, ["resource", "identifier"])
        print("grabbed identifier: ", identifier)
        #could also retrive "type" from data instead of using .startswith
        if(identifier is False):
            result = "failed"
        elif(is_doi(identifier) and is_url_reachable("https://doi.org/" + identifier)):
            result = "success"
        elif(identifier.startswith("DRKS") and is_url_reachable("https://drks.de/search/de/trial/" + identifier)):
            result = "success"
        elif(identifier.startswith("arxiv") and is_url_reachable("https://arxiv.org/abs/" + identifier)):
            result = "success"
        elif(identifier.startswith("lsid") or identifier.startswith("urn:lsid")):
            if(identifier.startswith("lsid")):
                identifier = "urn:" + identifier
            if(is_url_reachable("http://www.lsid.info/" + identifier)):
                result = "success"
        elif(identifier.startswith("pmid") and is_url_reachable("https://pubmed.ncbi.nlm.nih.gov/" + identifier)):
            result = "success"
        elif(identifier.startswith("NCT") and is_url_reachable("https://clinicaltrials.gov/study/" + identifier)):
            result = "success"
        elif(is_url_reachable(identifier)):
            result = "success"
        else:
            result = "failed"

        incoperate_results(task_dict, result, test)


@app.task
def hsh_f2_rich_metadata_provided(task_dict: dict, data: dict, test: bool = False):
    """
    mandatory:
    resource.identifier
    resource.keywords
    resource.classification
    resource.descriptions.language
    resource.descriptions.text
    resource.contributors
    resource.provenance

    conditional:
    resource.nonStudyDetails
    design
    """

    study_attributes = [
        ["resource", "languages"],
        ["resource", "webpage"],
        ["resource", "nonStudyDetails", "version"],
        ["resource", "nonStudyDetails", "format"],
        ["resource", "contributors", "email"],
        ["resource", "contributors", "affiliations", "address"],
        ["resource", "contributors", "affiliations", "webpage"]
    ]

    document_attributes = [
        ["resource", "languages"],
        ["resource", "webpage"],
        ["resource", "contributors", "email"],
        ["resource", "contributors", "affiliations", "address"],
        ["resource", "contributors", "affiliations", "webpage"],
        ["design", "administrativeInformation", "ethicsCommitteeApproval"],
        ["design", "administrativeInformation", "startDate"],
        ["design", "dataSource", "general"],
        ["design", "dataSource", "description"],
        ["design", "primaryPurpose"],
        ["design", "eligibilityCriteria", "genders"],
        ["design", "eligibilityCriteria", "inclusionCriteria"],
        ["design", "eligibilityCriteria", "exclusionCriteria"],
        ["design", "population", "region"],
        ["design", "population", "obtainedSampleSize"],
        ["design", "interventions", "type"],
        ["design", "interventions", "description"],
        ["design", "dataSharingPlan", "description"],
        ["design", "dataSharingPlan", "requestData"],
        ["design", "dataSharingPlan", "url"],
        ["design", "interventional", "masking", "general"],
        ["design", "interventional", "masking", "description"]
    ]

    check = study_attributes
    if(check_route(data, ["resource", "classification", "type"]) == "study"):
        check = document_attributes


    if(check_list(data, check)):
        result = "success"
    else:
        result = "failed"

    #TODO: handle conditional attributes; waiting for info
    incoperate_results(task_dict, result, test)

@app.task
def hsh_f3_id_of_data_included(task_dict: dict, data: dict, test: bool = False):
    """
    resource.ids.identifier
    resource.ids.scheme
    resource.ids.relationType

    for each ressource id in resource.ids -> check if relationType is “A describes B” or “A is metadata for B”
    """

    result = "failed"

    ids = check_route(data, ["resource", "ids"])

    print("IDS: ----------------------", check_route(data, ["resource", "ids"]))

    if(ids):
        for el in check_route(data, ["resource", "ids"]):
            if 'identifier' not in el or 'scheme' not in el or 'relationType' not in el:
                incoperate_results(task_dict, "failed", test)
            else:
                #TODO: check if its enough to have one relation out of all resources

                if el['relationType'] in ('A describes B', 'A is metadata for B'):
                    result = "success"

    incoperate_results(task_dict, result, test)


# @app.task
# def hsh_f4_metadata_indexed(task_dict: dict, data: dict, test: bool = False):
#     """
#     since the data is send to out tool as a json it clearly is indexed
#     """

#     result = "success"

#     incoperate_results(task_dict, result, test)

@app.task
def hsh_a1_contains_access_information(task_dict: dict, data: dict, test: bool = False):
    """
    1. check if there is a data sharing plan (study_data_sharing_plan_generally)
    2. if yes -> evaluate ‘study_data_sharing_plan_time_frame’ and ‘study_data_sharing_plan_access_criteria’ somehow
    """

    general_plan = check_route(data, ["resource","design","dataSharingPlan","generally"])
    print("INFO - general plan - ", general_plan)

    has_plan = general_plan == "Yes, there is a plan to make data available"

    if has_plan:
        result = "success"
    else:
        result = "failed"

    incoperate_results(task_dict, result, test)

@app.task
def hsh_a1_03_id_resolves_to_record(task_dict: dict, data: dict, test: bool = False):
    """ 1. build URL with base_url + ID
        2. somehow ping URL  """
    record_id = check_route(data, ["resource", "identifier"])
    url = "https://health-study-hub.de/resource/" + record_id

    if is_url_reachable(url):
        result = "success"
    else:
        result = "failed"

    incoperate_results(task_dict, result, test)


@app.task
def hsh_i3_01_ref_other_metadata(task_dict: dict, data: dict, test: bool = False):
    #check if other data is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    #print("INFO - hsh-i3-02")
    result = "not_applicable"
    if(ref_resources != False):
        for el in ref_resources:
            #DOI, URL, arXiv, EAN13, EISSN, Handle, ISBN, ISTC and LISSN.
            if el['relationType'] in ('A continues B', 'A is continued by B'):
                identifier = el['identifier']
                if(identifier is False):
                    result = "failed"
                elif(is_doi(identifier) and is_url_reachable("https://doi.org/" + identifier)):
                    result = "success"
                elif(identifier.startswith("arxiv") and is_url_reachable("https://arxiv.org/abs/" + identifier)):
                    result = "success"
                elif(is_url_reachable(identifier)):
                    result = "success"
                else:
                    result = "warnings" #the implementation guide is incomplete and lacks precision at this point
    incoperate_results(task_dict, result, test)

@app.task
def hsh_i3_02_ref_other_data(task_dict: dict, data: dict, test: bool = False):
    #check if other data is referenced
    ref_resources = check_route(data, ["resource", "ids"])
    print("INFO - hsh-i3-02")
    result = "not_applicable"
    if(ref_resources != False):
        for el in ref_resources:
            if el['relationType'] in ('A describes B', 'A is metadata for B'):
                identifier = el['identifier']
                print("looking for the identifier A DESCRIBES B", identifier)
                if(identifier is False):
                    result = "failed"
                elif(is_doi(identifier) and is_url_reachable("https://doi.org/" + identifier)):
                    result = "success"
                elif(identifier.startswith("arxiv") and is_url_reachable("https://arxiv.org/abs/" + identifier)):
                    result = "success"
                elif(is_url_reachable(identifier)):
                    result = "success"
                else:
                    result = "warnings" #the implementation guide is incomplete and lacks precision at this point
    incoperate_results(task_dict, result, test)

@app.task
def hsh_i3_03_qual_ref_other_metadata(task_dict: dict, data: dict, test: bool = False):
    #check if other metadata is referenced
    ref_resources = check_route(data, ["resource", "ids"])

    result = "not_applicable"
    if ref_resources != False:
        for el in ref_resources:
            rel_type = el['relationType']
            if rel_type in ["A is continued by B", "A continues B", "A has version B", "A is version of B", "A is new version of B", "A is previous version of B", "A is part of B", "A has part B", "A is identical to B"]:
                identifier = el['identifier']
                if identifier is False:
                    result = "failed"
                elif is_doi(identifier) and is_url_reachable("https://doi.org/" + identifier):
                    result = "success"
                elif identifier.startswith("arxiv") and is_url_reachable("https://arxiv.org/abs/" + identifier):
                    result = "success"
                elif is_url_reachable(identifier):
                    result = "success"
                else:
                    result = "warnings" #the implementation guide is incomplete and lacks precision at this point
    incoperate_results(task_dict, result, test)

@app.task
def hsh_i3_04_qual_ref_other_data(task_dict: dict, data: dict, test: bool = False):
    #check if other data is referenced
    ref_resources = check_route(data, ["resource", "ids"])

    result = "not_applicable"
    if(ref_resources != False):
        for el in ref_resources:
            if(el['relationType'] == 'A cites B'):
                identifier = el['identifier']
                if(identifier is False):
                    result = "failed"
                elif(is_doi(identifier) and is_url_reachable("https://doi.org/" + identifier)):
                    result = "success"
                elif(identifier.startswith("arxiv") and is_url_reachable("https://arxiv.org/abs/" + identifier)):
                    result = "success"
                elif(is_url_reachable(identifier)):
                    result = "success"
                else:
                    result = "warnings" #the implementation guide is incomplete and lacks precision at this point
    incoperate_results(task_dict, result, test)

##### Reusability
@app.task
def hsh_r1_1_plurality_of_attributes(task_dict: dict, data: dict, test: bool = False):
    attribute_list = [["resource", "identifier"], ["resource", "keywords"], ["resource", "classification"], ["resource", "descriptions", "language"], ["resource", "descriptions", "text"], ["design", "primaryDesign"], ["resource", "provenance"], ["resource", "nonStudyDetails"]]
    result = "success"
    for attr in attribute_list:
        if not check_route(data, attr):
            result = "failed"
    incoperate_results(task_dict, result, test)

@app.task
def hsh_r1_1_01_has_reuse_license(task_dict: dict, data: dict, test: bool = False):
    attribute_list = [["resource", "nonStudyDetails", "useRights", "label"], ["resource", "nonStudyDetails", "useRights", "link"], ["resource", "nonStudyDetails", "useRights", "description"], ["resource", "nonStudyDetails", "useRights", "confirmations", "terms"], ["resource", "nonStudyDetails", "useRights", "confirmations", "supportByLicensing"], ["resource", "nonStudyDetails", "useRights", "confirmations", "irrevocability"], ["resource", "nonStudyDetails", "useRights", "confirmations", "authority"]]
    result = "success"
    for attr in attribute_list:
        if not check_route(data, attr):
            result = "failed"
    incoperate_results(task_dict, result, test)

@app.task #TODO: verify if this automated task really works since it depends on a parent task
def hsh_r1_1_02_has_standard_reuse_license(task_dict: dict, data: dict, test: bool = False):
    print("INDICATOR RUNNING")
    #check if userights label is a fitting license
    license_label = check_route(data,["resource", "nonStudyDetails", "useRights", "label"])
    license_link = check_route(data, ["resource", "nonStudyDetails", "useRights", "link"])
    if(license_label in ("CC0 1.0 (Creative Commons Zero v1.0 Universal)", "CC BY 4.0 (Creative Commons Attribution 4.0 International)", "CC BY-NC 4.0 (Creative Commons Attribution Non Commercial 4.0 International)", "CC BY-SA 4.0 (Creative Commons Attribution Share Alike 4.0 International)", "CC BY-NC-SA 4.0 (Creative Commons Attribution Non Commercial Share Alike 4.0 International)") and license_link):
        result = "success"
    #elif(license_label == "Other"): # not in the doc
    #    result = "warning"
    else:
        result = "failed"
    incoperate_results(task_dict, result, test)

# Fitting licenses according to indicators: CC0 1.0, CC BY 4.0, CC BY-NC 4.0, CC BY-SA 4.0, CC BY-NC-SA 4.0
""" Allowed values in HSH:
CC0 1.0 (Creative Commons Zero v1.0 Universal)
CC BY 4.0 (Creative Commons Attribution 4.0 International)
CC BY-NC 4.0 (Creative Commons Attribution Non Commercial 4.0 International)
CC BY-SA 4.0 (Creative Commons Attribution Share Alike 4.0 International)
CC BY-NC-SA 4.0 (Creative Commons Attribution Non Commercial Share Alike 4.0 International)
All rights reserved
Other
Not applicable
Not assigned
Unknown
"""
@app.task #TODO: verify if this automated task really works since it depends on a parent task
def hsh_r1_1_03_has_machine_readable_reuse_license(task_dict: dict, data: dict, test: bool = False):
    license_label  = check_route(data,["resource", "nonStudyDetails", "nonStudyDetails", "useRights", "label"])
    if(license_label in ["Creative Commons Zero v1.0 Universal", "Creative Commons Attribution 4.0 International", "Creative Commons Attribution Non Commercial 4.0 International", "Creative Commons Attribution Share Alike 4.0 International", "Creative Commons Attribution Non Commercial Share Alike 4.0 International"]):
        result = "success"
    else:
        result = "failed"
    incoperate_results(task_dict, result, test)

@app.task
def hsh_r1_2_01_has_provenance_information(task_dict: dict, data: dict, test: bool = False):
    attribute_list = [["resource", "provenance", "verificationDate"], ["resource", "provenance", "dataSource"], ["resource", "provenance", "firstSubmittedDate"], ["resource", "provenance", "lastUpdatePostedDate"]]
    result = "success"
    for attr in attribute_list:
        if not check_route(data, attr):
            result = "failed"
    incoperate_results(task_dict, result, test)

# currently the same as the attribute before according to the indicators doc
@app.task
def hsh_r1_2_02_has_standardized_provenance_information(task_dict: dict, data: dict, test: bool = False):
    #provenance_info = check_route(data, ["resource", "provenance"])
    #if(provenance_info):
    #    if(provenance_info.get("verificationDate") and provenance_info.get("dataSource") and provenance_info.get("firstSubmittedDate") and provenance_info.get("lastUpdatePostedDate")):
    #        result = "success"
    #    else:
    #        result = "failed"
    result = "warnings" # the evaluation requires a PROV-O validator. No further information in the document
    incoperate_results(task_dict, result, test)

@app.task
def hsh_r1_3_01_metadata_complies_community_standards(task_dict: dict, data: dict, test: bool = False):
    result = "warnings" # incomplete description
    incoperate_results(task_dict, result, test)

@app.task
def hsh_r1_3_02_metadata_machine_readable_community_standards(task_dict: dict, data: dict, test: bool = False):
    result = "warnings" # incomplete description
    incoperate_results(task_dict, result, test)

#@app.task   ## implicit pass according to indicators doc
#def hsh_r1_3_01_metadata_standardized(task_dict: dict, data: dict, test: bool = False):

#@app.task   ## implicit pass according to indicators doc
#def hsh_r1_3_02_metadata_stadardized_machine_readable(task_dict: dict, data: dict, test: bool = False):

