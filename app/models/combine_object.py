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
            self.main_model_metadata = None

            self.main_model_object = CombineSbml(filename)
            try:
                assert self.main_model_object.content.model is not None
            except AssertionError:
                raise ValueError("The provided SBML file does not contain any model")

            self.entries = {filename: self.main_model_object}
            self.entries_metadata = {}

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
                    # Here make tmp files to read for CombineModel and CombineMetada
                    with NamedTemporaryFile("w+") as file:
                        content = self.extractEntryToString(entry.getLocation())
                        file.write(content)
                        sbml_object = CombineSbml(file.name)
                        if sbml_object.content.model is not None:
                            self.main_model_object = sbml_object
                            self.main_model_location = str(loc)
                            self.main_model_metadata = self.entries_metadata[str(loc)]
                            break

    def dict(self):
        return {
            "path": self.path,
            "locations": self.locations,
            "main_model_object": self.main_model_object.dict(),
            "main_model_location": self.main_model_location,
            "main_model_metadata": CombineSbmlMetadata(self.main_model_metadata).dict(),
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


class CombineSbmlMetadata:
    # TODO
    def __init__(self, omex_description: libcombine.OmexDescription):
        self.metadata = omex_description or None

    # TODO
    def dict(self):
        return {"found": True}
