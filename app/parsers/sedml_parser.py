import libsbml
import logging

from defusedxml import ElementTree as ET
from rdflib import Graph, URIRef

from .abstract import ModelObject, ModelMetadata


logger = logging.getLogger(__name__)


class SedMLParsingException(Exception):
    pass


# TODO: Should provide an abstract class that is inherited by
#   the metadata for cellml, sed-ml and sbml files
class SedmlModel(ModelObject):
    def __init__(self, filename: str):
        # Here just retrieve file content to build the CombineModel
        self.content = libsbml.readSBML(filename)
        if self.content.getNumErrors() > 0 and self.content.model is None:
            error_log = [
                f"{self.content.getError(i).getMessage()}\n"
                for i in range(self.content.getNumErrors())
            ]
            raise IOError(
                f"Error(s) occurred while reading the model file: \n{error_log}"
            )

        self.namespaces = dict(
            [node for _, node in ET.iterparse(filename, events=["start-ns"])]
        )

    @property
    def id(self):
        return self.content.model.id

    def dict(self):
        return {
            "id": self.content.model.id,
        }


# TODO: Should provide an abstract metadata class that is inherited by
#   the metadata for cellml, sed-ml and sbml files
class SedmlModelMetadata(ModelMetadata):
    def __init__(self, filename: str):
        super().__init__()
        tree = ET.parse(filename)
        model = tree.find("./{*}model")
        self._id = model.attrib["id"]

        content = model.find("./{*}annotation")
        document_ref = URIRef(f"#{model.attrib['metaid']}")

        all_metadata = content.findall(".//{*}RDF")

        for rdf_tree in all_metadata:
            graph = Graph().parse(data=ET.tostring(rdf_tree), format="xml")
            if (document_ref, None, None) not in graph:
                continue

            self.metadata.append(rdf_tree)
            self.rdf_graphs.append(graph)

            self.parse_metadata_graph(graph, document_ref)

    @property
    def id(self):
        return self._id
