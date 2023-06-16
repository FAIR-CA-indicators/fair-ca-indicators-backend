import libcombine
import libsbml

from tempfile import NamedTemporaryFile


class CombineArchive(libcombine.CombineArchive):
    def __init__(self, filename: str, file_is_archive: bool = True) -> None:
        super().__init__()
        self.is_from_archive = file_is_archive
        if not file_is_archive:
            self.locations = []

            self.model = CombineSbml(filename)
            try:
                assert self.model.content.model is not None
            except AssertionError:
                raise ValueError("The provided SBML file does not contain any model")

            self.model_metadata = None
            self.entries = {filename: self.model}
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
                            break

                    self.main_model_metadata = self.entries_metadata[str(loc)]


class CombineSbml:
    def __init__(self, filename: str):
        # Here just retrieve file content to build the CombineModel
        self.content = libsbml.readSBML(filename)
        print(f"Model recovered from tempfile:\n{self.content.model.id}")

        pass
