import json
import libcombine
import libsbml

from tempfile import NamedTemporaryFile


class CombineArchive(libcombine.CombineArchive):
    def __init__(self, filename: str, file_is_archive: bool = True) -> None:
        super().__init__()
        self.is_from_archive = file_is_archive
        self.path = filename
        if not file_is_archive:
            self.locations = []
            self.main_model_location = None

            self.main_model_object = CombineSbml(filename)

            try:
                assert self.main_model_object.content.model is not None
            except AssertionError:
                raise ValueError("An error occurred while parsing provided file")

            self.entries = {filename: self.main_model_object}
            self.entries_metadata = {}
            self.main_model_metadata = CombineModelMetadata(self.main_model_object)

        else:
            if not self.initializeFromArchive(filename):
                raise IOError(f"An error occurred trying to read {filename}")

            self.locations = [str(loc) for loc in self.getAllLocations()]
            self.entries = {}
            self.entries_metadata = {}
            self.main_model_object = None
            self.main_model_location = None
            self.main_model_metadata = None

            for i in range(self.getNumEntries()):
                entry = self.getEntry(i)
                loc = entry.getLocation()
                self.entries.update({str(loc): entry})
                self.entries_metadata.update(
                    {str(loc): self.getMetadataForLocation(loc)}
                )

                if (
                    loc.endswith(".xml")
                    and not loc.endswith("manifest.xml")
                    and self.main_model_object is None
                ):
                    # Here make tmp files to read for CombineModel and CombineMetadata
                    with NamedTemporaryFile("w+") as file:
                        content = self.extractEntryToString(entry.getLocation())
                        file.write(content)
                        sbml_object = CombineSbml(file.name)
                        if sbml_object.content.model is not None:
                            self.main_model_object = sbml_object
                            self.main_model_location = str(loc)
                            self.main_model_metadata = CombineModelMetadata(
                                self.main_model_object
                            )
                            break

    def dict(self):
        return {
            "path": self.path,
            "locations": self.locations,
            "main_model_object": self.main_model_object.dict(),
            "main_model_location": self.main_model_location,
            "main_model_metadata": self.main_model_metadata.dict(),
        }

    def json(self):
        return json.dumps(self.dict())


class CombineSbml:
    def __init__(self, filename: str):
        # Here just retrieve file content to build the CombineModel
        self.content = libsbml.readSBML(filename)

    def dict(self):
        return {
            "id": self.content.model.id,
        }


class CombineModelMetadata:
    # TODO
    def __init__(self, model_object: CombineSbml):
        self.content = (
            model_object.content.model.getAnnotation()
            if model_object.content.model.isSetAnnotation()
            else None
        )

        self.taxa = []
        self.properties = []
        self.versions = []
        self.alt_ids = []

        description = None
        for i in range(self.content.getNumChildren()):
            child = self.content.getChild(i)
            if child.getName() == "RDF":
                for j in range(child.getNumChildren()):
                    rdf_child = child.getChild(j)
                    if rdf_child.getName() == "Description":
                        description = rdf_child
                        break
                if description is not None:
                    break

        if description is None:
            return

        for i in range(description.getNumChildren()):
            child = description.getChild(i)
            if child.getName() == "hasProperty":
                self.properties.append(child.getAttrValue(0))
            if child.getName() == "hasTaxons":
                self.taxa.append(child.getAttrValue(0))
            if child.getName() == "is":
                bag = child.getChild(0)
                for j in range(bag.getNumChildren()):
                    self.alt_ids.append(bag.getChild(0).getAttrValue(0))

    # TODO
    def dict(self):
        if self.content:
            return {
                "alt_ids": self.alt_ids,
                "versions": self.versions,
                "properties": self.properties,
                "taxa": self.taxa,
            }
        else:
            return {}
