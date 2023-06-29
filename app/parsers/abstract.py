import json
import logging
from abc import ABC, abstractmethod
from typing import List, Union, TYPE_CHECKING
from rdflib import URIRef, Graph, DCTERMS, DC, RDF, BNode

if TYPE_CHECKING:
    from rdflib.term import Node

logger = logging.getLogger(__name__)


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


# TODO The parsing of the annotation needs to handle a lot of possible terms
#   These are not implemented yet, but will need to be in the future
#   All terms used are defined at the following locations:
#     - RDF terms: http://www.w3.org/1999/02/22-rdf-syntax-ns
#     - Biomodel model qualifiers: http://biomodels.net/model-qualifiers/
#     - Biomodel biology qualifier: http://biomodels.net/biology-qualifiers/
#     - Visit Card web standard http://www.w3.org/2001/vcard-rdf/3.0#
#     - Dublin Core Metadata Identifiers: http://purl.org/dc/elements/1.1/
#     - Dublin Core Metadata Terms: http://purl.org/dc/terms/
#     - COPASI Terms: http://www.copasi.org/RDF/MiriamTerms
class ModelMetadata(ModelObject, ABC):
    CREATOR_VCARD_REFERENCES = [
        {
            "N": URIRef("http://www.w3.org/2001/vcard-rdf/3.0#N"),
            "Given": URIRef("http://www.w3.org/2001/vcard-rdf/3.0#Given"),
            "Family": URIRef("http://www.w3.org/2001/vcard-rdf/3.0#Family"),
        },
        {
            "N": URIRef("http://www.w3.org/2006/vcard/ns#n"),
            "Given": URIRef("http://www.w3.org/2006/vcard/ns#given-name"),
            "Family": URIRef("http://www.w3.org/2006/vcard/ns#family-name"),
        },
        {
            # Does not exist in vcard spec, but libcombine saves creators under that reference
            "N": URIRef("http://www.w3.org/2006/vcard/ns#hasName"),
            "Given": URIRef("http://www.w3.org/2006/vcard/ns#given-name"),
            "Family": URIRef("http://www.w3.org/2006/vcard/ns#family-name"),
        },
    ]
    IS_VERSION_OF_REFERENCES = [
        URIRef("http://biomodels.net/biology-qualifiers/isVersionOf"),
        URIRef("http://www.copasi.org/RDF/MiriamTerms#isVersionOf"),
    ]
    OCCURS_IN_REFERENCES = [
        URIRef("http://biomodels.net/biology-qualifiers/occursIn"),
    ]
    IS_DESCRIBED_BY_REFERENCES = [
        URIRef("http://biomodels.net/biology-qualifiers/isDescribedBy"),
        URIRef("http://biomodels.net/model-qualifiers/isDescribedBy"),
        URIRef("http://www.copasi.org/RDF/MiriamTerms#isDescribedBy"),
        DCTERMS.bibliographicCitation,
    ]
    ALT_ID_REFERENCES = [
        URIRef("http://biomodels.net/model-qualifiers/is"),
        URIRef("http://biomodels.net/biology-qualifiers/is"),
    ]
    HAS_TAXON_REFERENCES = [
        URIRef("http://biomodels.net/biology-qualifiers/hasTaxon"),
    ]
    HAS_PROPERTY_REFERENCES = [
        URIRef("http://biomodels.net/biology-qualifiers/hasProperty")
    ]

    def __init__(self):
        self._id = None
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
        self._additional_metadata_objects = []

    def parse_metadata_graph(self, graph: Graph, model_uri: URIRef):
        self.extract_creation_date(graph, model_uri)
        self.extract_modification_dates(graph, model_uri)
        self.extract_creators(graph, model_uri)
        self.extract_alternative_ids(graph, model_uri)
        self.extract_cell_locations(graph, model_uri)
        self.extract_versions(graph, model_uri)
        self.extract_taxa(graph, model_uri)
        self.extract_citations(graph, model_uri)
        self.extract_properties(graph, model_uri)

    def parse_bnode_for_resource(self, graph: Graph, bnode: BNode, resource_name: str):
        return {
            "creators": self.extract_creators,
            "creation_date": self.extract_creation_date,
            "modification_dates": self.extract_modification_dates,
            "alt_ids": self.extract_alternative_ids,
            "cell_locations": self.extract_cell_locations,
            "versions": self.extract_versions,
            "taxa": self.extract_taxa,
            "citations": self.extract_citations,
            "properties": self.extract_properties,
        }[resource_name](graph, bnode)

    def extract_creation_date(self, graph: Graph, model_uri: Union[URIRef, BNode]):
        date_ref_id = graph.value(subject=model_uri, predicate=DCTERMS.created)
        creation_date = graph.value(date_ref_id, DCTERMS.W3CDTF)
        if creation_date:
            if not self._creation_date and self._creation_date != creation_date:
                logger.warning(
                    f"Multiple creation dates were found. Keeping the last occurring one ({creation_date})"
                )
            self._creation_date = creation_date

    def extract_versions(self, graph: Graph, model_uri: URIRef):
        for ref in self.IS_VERSION_OF_REFERENCES:
            self._versions.update(
                self.retrieve_resources(model_uri, ref, graph, "versions")
            )

    def extract_creators(self, graph: Graph, model_uri: URIRef):
        def parse_vcard_object(vcard_node: "Node", ref: dict):
            name_triple_ref = graph.value(vcard_node, ref["N"])
            if name_triple_ref is not None:
                fullname = (
                    f"{graph.value(name_triple_ref, ref['Given'])} "
                    f"{graph.value(name_triple_ref, ref['Family'])}"
                )
                self._creators.add(fullname)

        creator_triples = list(graph.triples((model_uri, DC.creator, None))) + list(
            graph.triples((model_uri, DCTERMS.creator, None))
        )

        for triple in creator_triples:
            # If triple target is a bag, we need to go over the list
            if graph.value(subject=triple[2], predicate=RDF.type) == RDF.Bag:
                for bag_triple in graph.triples((triple[2], None, None)):
                    if bag_triple[1] == RDF.type:
                        continue

                    # Checking all possible VCard references
                    for vcard_ref in self.CREATOR_VCARD_REFERENCES:
                        parse_vcard_object(bag_triple[2], vcard_ref)

            # Else, we just get the name
            else:
                for vcard_ref in self.CREATOR_VCARD_REFERENCES:
                    parse_vcard_object(triple[2], vcard_ref)

    def extract_modification_dates(self, graph: Graph, model_uri: URIRef):
        for triple in graph.triples((model_uri, DCTERMS.modified, None)):
            date = graph.value(subject=triple[2], predicate=DCTERMS.W3CDTF)
            self._modification_dates.add(date)

    def extract_alternative_ids(self, graph: Graph, model_uri: URIRef):
        for ref in self.ALT_ID_REFERENCES:
            self._alt_ids.update(
                self.retrieve_resources(model_uri, ref, graph, "alt_ids")
            )

    def extract_properties(self, graph: Graph, model_uri: URIRef):
        for ref in self.HAS_PROPERTY_REFERENCES:
            self._properties.update(
                self.retrieve_resources(model_uri, ref, graph, "properties")
            )

    def extract_taxa(self, graph: Graph, model_uri: URIRef):
        for ref in self.HAS_TAXON_REFERENCES:
            self._taxa.update(self.retrieve_resources(model_uri, ref, graph, "taxa"))

    def extract_cell_locations(self, graph: Graph, model_uri: URIRef):
        for ref in self.OCCURS_IN_REFERENCES:
            self._cell_locations.update(
                self.retrieve_resources(model_uri, ref, graph, "cell_locations")
            )

    def extract_citations(self, graph: Graph, model_uri: URIRef):
        for ref in self.IS_DESCRIBED_BY_REFERENCES:
            self._citations.update(
                self.retrieve_resources(model_uri, ref, graph, "citations")
            )

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

    def retrieve_resources(
        self, subject: URIRef, predicate: URIRef, graph: Graph, resource_name: str
    ):
        resources = []
        for triple in graph.triples((subject, predicate, None)):
            # If multiple values available, they are probably stored in a Bag
            if graph.value(subject=triple[2], predicate=RDF.type) == RDF.Bag:
                for bag_triple in graph.triples((triple[2], None, None)):
                    if bag_triple[1] == RDF.type:
                        continue
                    if bag_triple[2] not in resources:
                        resources.append(bag_triple[2])
            # Else, we just get the name
            elif isinstance(triple[2], BNode):
                self.parse_bnode_for_resource(graph, triple[2], resource_name)
            else:
                if triple[2] not in resources:
                    resources.append(triple[2])

        return resources

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