import json
from abc import ABC, abstractmethod
from typing import List
from rdflib import URIRef


class ModelObject(ABC):
    @property
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def dict(self):
        pass

    def json(self) -> str:
        return json.dumps(self.dict())


class ModelMetadata(ModelObject, ABC):
    CREATOR_NAME_2001_REF = URIRef("http://www.w3.org/2001/vcard-rdf/3.0#N")
    CREATOR_NAME_2006_REF = URIRef("http://www.w3.org/2006/vcard/ns#n")
    CREATOR_GIVEN_NAME_2001_REF = URIRef("http://www.w3.org/2001/vcard-rdf/3.0#Given")
    CREATOR_GIVEN_NAME_2006_REF = URIRef("http://www.w3.org/2006/vcard/ns#given-name")
    CREATOR_FAMILY_NAME_2001_REF = URIRef("http://www.w3.org/2001/vcard-rdf/3.0#Family")
    CREATOR_FAMILY_NAME_2006_REF = URIRef("http://www.w3.org/2006/vcard/ns#family-name")
    MODIFICATION_DATE_REF = URIRef("http://www.cellml.org/metadata/1.0#modification")

    def __init__(self):
        self._creators = set()
        self._creation_date = ""
        self._modification_dates = set()
        self._alt_ids = set()
        self._versions = set()
        self._properties = set()
        self._taxa = set()
        self._cell_locations = set()
        self._citations = set()
        self._additional_metadata_objects = []

    @staticmethod
    def export_set(items: set) -> List[str]:
        return [str(item) for item in items]

    @property
    def creators(self) -> List[str]:
        creators = self._creators.copy()
        for metadata_object in self._additional_metadata_objects:
            creators.update(metadata_object._creators)

        return self.export_set(creators)

    @property
    def creation_date(self) -> str:
        if not self._creation_date:
            for metadata_object in self._additional_metadata_objects:
                if metadata_object.creation_date:
                    return metadata_object.creation_date

            return ""

        else:
            return str(self._creation_date)

    @property
    def modification_dates(self) -> List[str]:
        dates = self._modification_dates.copy()
        for metadata_object in self._additional_metadata_objects:
            dates.update(metadata_object._modification_dates)

        return self.export_set(dates)

    @property
    def alt_ids(self) -> List[str]:
        alt_ids = self._alt_ids.copy()
        for metadata_object in self._additional_metadata_objects:
            alt_ids.update(metadata_object._alt_ids)
        return self.export_set(alt_ids)

    @property
    def versions(self) -> List[str]:
        versions = self._versions.copy()
        for metadata_object in self._additional_metadata_objects:
            versions.update(metadata_object._versions)

        return self.export_set(versions)

    @property
    def properties(self) -> List[str]:
        properties = self._properties.copy()
        for metadata_object in self._additional_metadata_objects:
            properties.update(metadata_object._properties)
        return self.export_set(properties)

    @property
    def taxa(self) -> List[str]:
        taxa = self._taxa.copy()
        for metadata_object in self._additional_metadata_objects:
            taxa.update(metadata_object._taxa)
        return self.export_set(taxa)

    @property
    def cell_locations(self) -> List[str]:
        cell_locations = self._cell_locations.copy()
        for metadata_object in self._additional_metadata_objects:
            cell_locations.update(metadata_object._cell_locations)
        return self.export_set(cell_locations)

    @property
    def citations(self) -> List[str]:
        citations = self._citations.copy()
        for metadata_object in self._additional_metadata_objects:
            citations.update(metadata_object._citations)
        return self.export_set(citations)

    def add_internal_metadata(self, metadata_object: "ModelMetadata"):
        self._additional_metadata_objects.append(metadata_object)
