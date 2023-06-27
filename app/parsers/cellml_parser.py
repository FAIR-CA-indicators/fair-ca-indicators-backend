import logging

from rdflib import Graph, URIRef, DCTERMS, DC
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

            # Loading creators
            creator_triples = list(
                graph.triples((document_ref, DC.creator, None))
            ) + list(graph.triples((document_ref, DCTERMS.creator, None)))

            for subject, predicate, target in creator_triples:
                creator_name_id = graph.value(target, self.CREATOR_NAME_2006_REF)
                if creator_name_id is None:
                    creator_name_id = graph.value(target, self.CREATOR_NAME_2001_REF)
                    fullname = (
                        f"{graph.value(creator_name_id, self.CREATOR_GIVEN_NAME_2001_REF)} "
                        f"{graph.value(creator_name_id, self.CREATOR_FAMILY_NAME_2001_REF)}"
                    )
                    if fullname != "None None":
                        self._creators.add(fullname)
                else:
                    fullname = (
                        f"{graph.value(creator_name_id, self.CREATOR_GIVEN_NAME_2006_REF)} "
                        f"{graph.value(creator_name_id, self.CREATOR_FAMILY_NAME_2006_REF)}"
                    )
                    if fullname != "None None":
                        self._creators.add(fullname)

            # Loading creation date
            creation_date_id = graph.value(document_ref, DCTERMS.created, None)
            creation_date = graph.value(creation_date_id, DCTERMS.W3CDTF)
            if not self._creation_date and self._creation_date != creation_date:
                logger.warning(
                    "Multiple creation dates were found. Keeping the last occurring one"
                )
            self._creation_date = creation_date

            # Loading modification dates
            for subject, predicate, target in graph.triples(
                (document_ref, self.MODIFICATION_DATE_REF, None)
            ):
                modified_ref = graph.value(target, DCTERMS.modified)
                date = graph.value(modified_ref, DCTERMS.W3CDTF)
                self._modification_dates.add(date)

            # Loading alternative ids
            # FIXME

            # Loading model versions
            # FIXME

            # Loading model properties
            # FIXME

            # Loading taxa
            # FIXME

            # Loading cell locations
            # FIXME

            # Loading citations
            # FIXME

    @property
    def id(self):
        return self._id

    def dict(self):
        return {
            "alt_ids": self.alt_ids,
            "versions": self.versions,
            "properties": self.properties,
            "taxa": self.taxa,
            "creators": self.creators,
            "creation_date": self.creation_date,
            "modification_dates": self.modification_dates,
            "cell_locations": self.cell_locations,
            "citations": self.citations,
        }
