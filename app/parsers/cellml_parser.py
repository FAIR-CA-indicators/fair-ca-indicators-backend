import logging

from rdflib import Graph, URIRef, DCTERMS
from libcellml import Parser
from defusedxml import ElementTree as ET

from .abstract import ModelObject, ModelMetadata


logger = logging.getLogger(__name__)


class CellMLParsingException(Exception):
    pass


class CellMLModel(ModelObject):
    def __init__(self, filename):
        super().__init__()

        try:
            model_string = open(filename, "r").read()
        except IOError as e:
            raise IOError(
                f"An error occurred while trying to read {filename}: {str(e)}"
            )

        parser = Parser()
        model = parser.parseModel(model_string)
        if parser.errorCount() > 0:
            parser.setStrict(False)
            model = parser.parseModel(model_string)
            if parser.errorCount() > 0:
                error_log = ""
                for i in range(parser.errorCount()):
                    error_log += parser.error(i).description + "\n"

                raise CellMLParsingException(error_log)

        self.model = model

    @property
    def id(self) -> str:
        return self.model.id()

    @property
    def name(self) -> str:
        return self.model.name()

    def dict(self) -> dict:
        return {"id": self.id, "name": self.name}


class CellMLModelMetadata(ModelMetadata):
    CELLML_MODICATION_DATE_REF = URIRef(
        "http://www.cellml.org/metadata/1.0#modification"
    )

    def __init__(self, filename):
        super().__init__()

        model_tree = ET.parse(filename)
        self._id = model_tree.getroot().attrib[
            "{http://www.cellml.org/metadata/1.0#}id"
        ]

        document_ref = URIRef("")
        all_metadata = model_tree.findall(".//{*}RDF")
        self.metadata = []
        self.rdf_graphs = []
        self._creators = set()
        self._creation_date = ""
        self._modification_dates = set()
        self._alt_ids = set()
        self._versions = set()
        self._properties = set()
        self._taxa = set()
        self._cell_locations = set()
        self._citations = set()

        for tree in all_metadata:
            graph = Graph().parse(data=ET.tostring(tree), format="xml")
            if (document_ref, None, None) not in graph:
                continue
            self.metadata.append(tree)
            self.rdf_graphs.append(graph)
            self.parse_metadata_graph(graph, document_ref)

    def extract_modification_dates(self, graph: Graph, model_uri: URIRef):
        for triple in graph.triples((model_uri, self.CELLML_MODICATION_DATE_REF, None)):
            modified_ref = graph.value(triple[2], DCTERMS.modified)
            date = graph.value(modified_ref, DCTERMS.W3CDTF)
            self._modification_dates.add(date)

    @property
    def id(self):
        return self._id
