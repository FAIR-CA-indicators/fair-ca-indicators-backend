import logging

from rdflib import URIRef, Graph
from defusedxml import ElementTree as ET

from app.parsers.abstract import ModelMetadata


logger = logging.getLogger(__name__)


class RDFMetadataException(Exception):
    pass


class RDFMetadata(ModelMetadata):
    def __init__(self, filename: str, document_location: str):
        super().__init__()

        tree = ET.parse(filename)
        document_ref = URIRef(document_location)

        all_metadata = tree.getroot()
        self._id = document_location

        graph = Graph().parse(data=ET.tostring(all_metadata), format="xml")
        if (document_ref, None, None) not in graph:
            return

        self.metadata.append(all_metadata)
        self.rdf_graphs.append(graph)
        self.parse_metadata_graph(graph, document_ref)

    @property
    def id(self):
        return self._id
