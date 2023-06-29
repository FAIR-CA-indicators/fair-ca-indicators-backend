import json
import libcombine

from tempfile import NamedTemporaryFile

from app.parsers import (
    SbmlModel,
    SbmlModelMetadata,
    CellMLModel,
    CellMLModelMetadata,
    RDFMetadata,
)


class CombineArchiveException(Exception):
    pass


# TODO:
#   - Find a way to select the main model file, it is not clearcut
#   - Add parsers for cellml and sed-ml files
#   - These parsers have to output the data and metadata in the same formats
#   - If archive contains multiple models, either use the 'master' one (written in manifest.xml), or raise an error
#       and set all model related tasks to manual
class CombineArchive(libcombine.CombineArchive):
    PARSERS = {
        "xml": {"model": SbmlModel, "meta": SbmlModelMetadata},
        "sbml": {"model": SbmlModel, "meta": SbmlModelMetadata},
        "cellml": {"model": CellMLModel, "meta": CellMLModelMetadata},
        "sedml": {},  # FIXME
        "rdf": {"meta": RDFMetadata},
    }

    def __init__(self, filename: str, file_is_archive: bool = True) -> None:
        super().__init__()
        self.is_from_archive = file_is_archive
        self.path = filename
        if not file_is_archive:
            self.locations = []
            self.main_model_location = None

            file_format = filename.split(".")[-1]
            self.main_model_object = self.PARSERS[file_format]["model"](filename)

            self.entries = {filename: self.main_model_object}
            self.entries_metadata = {}
            print(f"Loading {filename} with parser {self.PARSERS[file_format]['meta']}")
            self.main_model_metadata = self.PARSERS[file_format]["meta"](filename)

        else:
            if not self.initializeFromArchive(filename):
                raise IOError(f"An error occurred trying to read {filename}")

            main_file = self.getMasterFile()
            if main_file is None:
                raise CombineArchiveException(
                    "No master file was defined in provided archive manifest. Please set as master the file you "
                    "want this tool to assess."
                )

            model_format = main_file.getFormat()
            if "sed-ml" in model_format or "sedml" in model_format:
                parser = self.PARSERS["sedml"]
            elif "sbml" in model_format:
                parser = self.PARSERS["sbml"]
            elif "cellml" in model_format:
                parser = self.PARSERS["cellml"]
            elif "copasi" in model_format:
                raise CombineArchiveException(
                    "COPASI files are not yet handled by the FairCombine assessment tool. Please convert your file in "
                    "a valid sbml."
                )
            else:
                raise CombineArchiveException(
                    "Master file is in unknown format. The FairCombine assessment tool works with SED-ML, SBML and "
                    f"CELLML files only. Provided format is {model_format}."
                )

            main_file_location = main_file.getLocation()
            self.main_model_metadata = None
            # If archive contained a metadata.rdf file, we read metadata from there
            if self.hasMetadataForLocation(main_file_location):
                with NamedTemporaryFile("w+") as tmp_meta_file:
                    # FIXME: !!! THE EXPORTED METADATA IS NOT THE SAME AS THE CONTENT OF `metadata.rdf`!!!
                    content = self.getMetadataForLocation(main_file_location).toXML()
                    tmp_meta_file.write(content)
                    tmp_meta_file.seek(0)
                    self.main_model_metadata = self.PARSERS["rdf"]["meta"](
                        tmp_meta_file.name, main_file_location
                    )

            with NamedTemporaryFile("w+") as tmp_file:
                content = self.extractEntryToString(main_file.getLocation())
                tmp_file.write(content)
                tmp_file.seek(0)
                self.main_model_object = parser["model"](tmp_file.name)
                self.main_model_location = main_file_location
                # If no metadata was found previously, try to find some in the model itself
                additional_metadata = parser["meta"](tmp_file.name)
                if self.main_model_metadata is None:
                    self.main_model_metadata = additional_metadata
                else:
                    print(
                        f"Currently found modif dates: {self.main_model_metadata.modification_dates}"
                    )
                    self.main_model_metadata.add_internal_metadata(additional_metadata)

            self.locations = [str(loc) for loc in self.getAllLocations()]
            self.entries = {}
            self.entries_metadata = {}

            for i in range(self.getNumEntries()):
                entry = self.getEntry(i)
                loc = entry.getLocation()
                self.entries.update({str(loc): entry})
                self.entries_metadata.update(
                    {str(loc): self.getMetadataForLocation(loc)}
                )

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
