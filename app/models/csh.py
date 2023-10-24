import re
from pydantic import BaseModel

class Score(BaseModel):
    overall: int =0
    F: int = 0
    A: int = 0
    I: int = 0
    R: int = 0

class study_evaluation: 
    def __init__(self, json_data, schema):
        print("+++++++++++ INSIDE study_evaluation")
        self.schema = schema
        self.metadata = json_data
        self.score = Score()
        
    


    def evaluate(self):
        print("the schema is: ")
        print(self.schema)
        if(self.schema == "3.1"):
            ###### here will be the list of assessments for schema 3.1
            #check identifier
            #
            identifier = self.check_route(["resource", "resource_identifier"])
            self.score.F += self.check_identifier(identifier)

            ######
        print(self.score)
        return self.score 

    def check_route(self, route_keys):
        current_position = self.metadata

        for key in route_keys:
            if key in current_position:
                current_position = current_position[key]
            else:
                #if a key is missing return false
                return False
        #if the route exists return the value
        return current_position

    # function to check the identifier for uniqueness and persistancy
    def check_identifier(self, identifier):
        if(self.is_doi(identifier)):
            return 1
        elif(identifier.startswith("DRKS")):
            return 1

    @staticmethod
    def is_doi(doi):
        doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
        # Use the re.match function to check if the string matches the pattern
        return bool(re.match(doi_pattern, doi))