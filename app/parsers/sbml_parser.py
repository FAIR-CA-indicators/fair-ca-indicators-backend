import libsbml
import logging

from defusedxml import ElementTree as ET
from rdflib import Graph, URIRef

from .abstract import ModelObject, ModelMetadata


logger = logging.getLogger(__name__)


class SBMLParsingException(Exception):
    pass


# TODO: Should provide an abstract class that is inherited by
#   the metadata for cellml, sed-ml and sbml files
class SbmlModel(ModelObject):
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
class SbmlModelMetadata(ModelMetadata):

    # TODO The parsing of the annotation needs to handle a lot of possible terms
    #   These are not implemented yet, but will need to be in the future
    #   All terms used are defined at the following locations:
    #     - RDF terms: http://www.w3.org/1999/02/22-rdf-syntax-ns
    #     - Biomodel model qualifiers: http://biomodels.net/model-qualifiers/
    #     - Biomodel biology qualifier: http://biomodels.net/biology-qualifiers/
    #     - Visit Card web standard http://www.w3.org/2001/vcard-rdf/3.0#
    #     - Dublin Core Metadata Identifiers: http://purl.org/dc/elements/1.1/
    #     - Dublin Core Metadata Terms: http://purl.org/dc/terms/
    def __init__(self, filename: str):
        super().__init__()

        tree = ET.parse(filename)
        model = tree.find("./{*}model")

        self._id = model.attrib["id"]
        annotation = model.find("./{*}annotation")
        document_ref = URIRef(f"#{model.attrib['metaid']}")

        all_metadata = annotation.findall(".//{*}RDF")

        for rdf_tree in all_metadata:
            graph = Graph().parse(data=ET.tostring(rdf_tree), format="xml")
            if (document_ref, None, None) not in graph:
                continue

            self.metadata.append(rdf_tree)
            self.rdf_graphs.append(graph)

            # Should load all the metadata we want to retrieve
            self.parse_metadata_graph(graph, document_ref)

    @property
    def id(self):
        return self._id
