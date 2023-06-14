import libcombine


class CombineArchive(libcombine.CombineArchive):
    # TODO
    #   Need to set the model(s)
    #   Need to set the model(s) metadata
    #   Need to set the archive metadata (from manifest.xml)

    def __init__(self, filename: str, file_is_archive: bool = True) -> None:
        super().__init__()
        self.is_from_archive = file_is_archive
        if not file_is_archive:
            self.locations = []

            self.model = CombineModel(filename)
            self.model_metadata = None
            self.entries = {filename: self.model}
            self.entries_metadata = {}

        else:
            if not self.initializeFromArchive(filename):
                raise IOError(f"An error occurred trying to read {filename}")

            self.locations = [str(loc) for loc in self.getAllLocations()]
            self.entries = {}
            self.entries_metadata = {}
            self.model = None
            self.model_metadata = None

            for i in range(self.getNumEntries()):
                entry = self.getEntry(i)
                loc = entry.getLocation()
                self.entries.update({str(loc): entry})
                self.entries_metadata.update(
                    {str(loc): self.getMetadataForLocation(loc)}
                )

                if loc.endswith(".xml") and self.model is None:
                    # Here make tmp files to read for CombineModel and CombineMetadata
                    self.model = entry
                    self.model_metadata = self.entries_metadata[str(loc)]


class CombineModel:
    def __init__(self, filename: str):
        pass


class CombineMetadata:
    pass
