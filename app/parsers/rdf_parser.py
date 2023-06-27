import logging

from rdflib import URIRef, Graph, RDF, DCTERMS, DC
from defusedxml import ElementTree as ET

from app.parsers.abstract import ModelMetadata


logger = logging.getLogger(__name__)


class RDFMetadataException(Exception):
    pass


class RDFMetadata(ModelMetadata):
    IS_VERSION_OF_REF = URIRef("http://biomodels.net/biology-qualifiers/isVersionOf")
    IS_VERSION_OF_COPASI_REF = URIRef(
        "http://www.copasi.org/RDF/MiriamTerms#isVersionOf"
    )
    OCCURS_IN_REF = URIRef("http://biomodels.net/biology-qualifiers/occursIn")
    IS_DESCRIBED_BY_BIOLOGY_REF = URIRef(
        "http://biomodels.net/biology-qualifiers/isDescribedBy"
    )
    IS_DESCRIBED_BY_MODEL_REF = URIRef(
        "http://biomodels.net/model-qualifiers/isDescribedBy"
    )
    IS_DESCRIBED_BY_COPASI_REF = URIRef(
        "http://www.copasi.org/RDF/MiriamTerms#isDescribedBy"
    )
    ALT_ID_MODEL_REF = URIRef("http://biomodels.net/model-qualifiers/is")
    ALT_ID_BIOLOGY_REF = URIRef("http://biomodels.net/biology-qualifiers/is")
    HAS_TAXON_REF = URIRef("http://biomodels.net/biology-qualifiers/hasTaxon")
    HAS_PROPERTY_REF = URIRef("http://biomodels.net/biology-qualifiers/hasProperty")

    # TODO The parsing of the annotation needs to handle a lot of possible terms
    #   These are not implemented yet, but will need to be in the future
    #   All terms used are defined at the following locations:
    #     - RDF terms: http://www.w3.org/1999/02/22-rdf-syntax-ns
    #     - Biomodel model qualifiers: http://biomodels.net/model-qualifiers/
    #     - Biomodel biology qualifier: http://biomodels.net/biology-qualifiers/
    #     - Visit Card web standard http://www.w3.org/2001/vcard-rdf/3.0#
    #     - Dublin Core Metadata Identifiers: http://purl.org/dc/elements/1.1/
    #     - Dublin Core Metadata Terms: http://purl.org/dc/terms/
    def __init__(self, filename: str, document_location: str):
        super().__init__()

        tree = ET.parse(filename)
        document_ref = URIRef(document_location)

        all_metadata = tree.getroot()
        self._id = document_location
        self.metadata = []
        self.rdf_graphs = []
        self._creation_date = ""
        self._modification_dates = set()
        self._creators = set()
        self._alt_ids = set()
        self._taxa = set()
        self._properties = set()
        self._versions = set()
        self._cell_locations = set()
        self._citations = set()

        graph = Graph().parse(data=ET.tostring(all_metadata), format="xml")
        if (document_ref, None, None) not in graph:
            return

        self.metadata.append(all_metadata)
        self.rdf_graphs.append(graph)

        # Loading creation date
        date_ref_id = graph.value(subject=document_ref, predicate=DCTERMS.created)
        creation_date = graph.value(date_ref_id, DCTERMS.W3CDTF)
        if creation_date:
            if not self._creation_date and self._creation_date != creation_date:
                logger.warning(
                    f"Multiple creation dates were found. Keeping the last occurring one ({creation_date})"
                )
            self._creation_date = creation_date

        # Loading modification dates
        for triple in graph.triples((document_ref, DCTERMS.modified, None)):
            date = graph.value(subject=triple[2], predicate=DCTERMS.W3CDTF)
            self._modification_dates.add(date)

        # Loading creator names
        creator_triples = list(graph.triples((document_ref, DC.creator, None))) + list(
            graph.triples((document_ref, DCTERMS.creator, None))
        )

        for triple in creator_triples:
            # If triple target is a bag, we need to go over the list
            if graph.value(subject=triple[2], predicate=RDF.type) == RDF.Bag:
                for bag_triple in graph.triples((triple[2], None, None)):
                    if bag_triple[1] == RDF.type:
                        continue
                    name_triple_ref = graph.value(
                        subject=bag_triple[2], predicate=self.CREATOR_NAME_2006_REF
                    )
                    if name_triple_ref is None:
                        name_triple_ref = graph.value(
                            subject=bag_triple[2], predicate=self.CREATOR_NAME_2001_REF
                        )
                        fullname = (
                            f"{graph.value(name_triple_ref, self.CREATOR_GIVEN_NAME_2001_REF)} "
                            f"{graph.value(name_triple_ref, self.CREATOR_FAMILY_NAME_2001_REF)}"
                        )
                        if fullname != "None None":
                            self._creators.add(fullname)
                    else:
                        fullname = (
                            f"{graph.value(name_triple_ref, self.CREATOR_GIVEN_NAME_2006_REF)} "
                            f"{graph.value(name_triple_ref, self.CREATOR_FAMILY_NAME_2006_REF)}"
                        )
                        if fullname != "None None":
                            self._creators.add(fullname)

            # Else, we just get the name
            else:
                name_triple_ref = graph.value(
                    subject=triple[2], predicate=self.CREATOR_NAME_2006_REF
                )
                if name_triple_ref is None:
                    name_triple_ref = graph.value(
                        subject=triple[2], predicate=self.CREATOR_NAME_2001_REF
                    )
                    fullname = (
                        f"{graph.value(name_triple_ref, self.CREATOR_GIVEN_NAME_2001_REF)} "
                        f"{graph.value(name_triple_ref, self.CREATOR_FAMILY_NAME_2001_REF)}"
                    )
                    if fullname != "None None":
                        self._creators.add(fullname)
                else:
                    fullname = (
                        f"{graph.value(name_triple_ref, self.CREATOR_GIVEN_NAME_2006_REF)} "
                        f"{graph.value(name_triple_ref, self.CREATOR_FAMILY_NAME_2006_REF)}"
                    )
                    if fullname != "None None":
                        self._creators.add(fullname)

        # Loading alternative ids
        self._alt_ids.update(
            self.extract_resource(document_ref, self.ALT_ID_MODEL_REF, graph)
        )

        self._alt_ids.update(
            self.extract_resource(document_ref, self.ALT_ID_BIOLOGY_REF, graph)
        )

        # Loading taxa data
        self._taxa.update(
            self.extract_resource(document_ref, self.HAS_TAXON_REF, graph)
        )

        # Loading model properties
        self._properties.update(
            self.extract_resource(document_ref, self.HAS_PROPERTY_REF, graph)
        )

        # Loading model versions
        self._versions.update(
            self.extract_resource(document_ref, self.IS_VERSION_OF_REF, graph)
        )

        self._versions.update(
            self.extract_resource(document_ref, self.IS_VERSION_OF_COPASI_REF, graph)
        )

        # Loading cell locations
        self._cell_locations.update(
            self.extract_resource(document_ref, self.OCCURS_IN_REF, graph)
        )

        # Loading citations
        self._citations.update(
            self.extract_resource(document_ref, self.IS_DESCRIBED_BY_BIOLOGY_REF, graph)
        )

        self._citations.update(
            self.extract_resource(document_ref, self.IS_DESCRIBED_BY_MODEL_REF, graph)
        )

        for triple in graph.triples(
            (document_ref, DCTERMS.bibliographicCitation, None)
        ):
            citation = graph.value(triple[2], self.IS_DESCRIBED_BY_COPASI_REF)
            if citation not in self._citations:
                self._citations.add(citation)

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

    @staticmethod
    def extract_resource(subject: URIRef, predicate: URIRef, graph: Graph):
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
            else:
                if triple[2] not in resources:
                    resources.append(triple[2])

        return resources
