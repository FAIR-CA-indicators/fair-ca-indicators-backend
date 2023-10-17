from fastapi import APIRouter
import json
from app.models.csh import evaluate

csh_router = APIRouter()





@csh_router.get("/csh/study", tags=["Study"])
def csh_study() -> str: #metadata, schema_version
    """
    **Parameters:**
        - *metadata*: json containing the metadata of a CSH entry
    **Returns:**
    A string for testing
    """
    #### stuff for testeing
    #### loads local json 
    json_file_path = "app/csh_schemas/examples/DRKS00027974.json"

    # Open and read the JSON file
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)


    print(json_data)

    ####----------------####

    schema_version = "3.1"
    evaluate(json_data, schema_version)

    return "checkiiii" 

print("Checki-di-check-check")