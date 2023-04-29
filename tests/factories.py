import factory
import tempfile

from uuid import uuid4

from app.models import (
    SessionSubjectIn,
    Session,
    Task,
    TaskPriority,
    Indicator,
)


class ManualSessionSubjectFactory(factory.Factory):
    class Meta:
        model = SessionSubjectIn

    subject_type = "manual"
    has_archive = False
    has_model = False
    has_archive_metadata = False
    is_model_standard = False
    is_archive_standard = False
    is_model_metadata_standard = False
    is_archive_metadata_standard = False
    is_biomodel = False
    is_pmr = False


class UrlSessionSubjectFactory(factory.Factory):
    class Meta:
        model = SessionSubjectIn

    subject_type = "url"
    path = factory.Faker("url")


class FileSessionSubjectFactory(factory.Factory):
    class Meta:
        model = SessionSubjectIn

    subject_type = "file"

    # FIXME: The tmp file is not deleted after use
    @factory.lazy_attribute
    def path(self):
        tmp = tempfile.NamedTemporaryFile("r", delete=False)
        return tmp.name


class SessionFactory(factory.Factory):
    class Meta:
        model = Session

    id = str(uuid4())
    session_subject = factory.SubFactory(ManualSessionSubjectFactory)


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Iterator(
        [
            "CA-RDA-F1-01Archive",
            "CA-RDA-F1-01Model",
            "CA-RDA-F1-01MA",
            "CA-RDA-F1-01MM",
            "CA-RDA-F1-02Archive",
            "CA-RDA-F1-02Model",
            "CA-RDA-F1-02MA",
            "CA-RDA-F1-02MM",
            "CA-RDA-F2-01MA",
            "CA-RDA-F2-01MM",
            "CA-RDA-F3-01MA",
            "CA-RDA-F3-01MM",
            "CA-RDA-F4-01MA",
            "CA-RDA-F4-01MM",
            "CA-RDA-A1-01MA",
            "CA-RDA-A1-01MM",
            "CA-RDA-A1-02Archive",
            "CA-RDA-A1-02Model",
            "CA-RDA-A1-02MA",
            "CA-RDA-A1-02MM",
            "CA-RDA-A1-03Archive",
            "CA-RDA-A1-03Model",
            "CA-RDA-A1-03MA",
            "CA-RDA-A1-03MM",
            "CA-RDA-A1-04Archive",
            "CA-RDA-A1-04Model",
            "CA-RDA-A1-04MA",
            "CA-RDA-A1-04MM",
            "CA-RDA-A1-05Archive",
            "CA-RDA-A1-05Model",
            "CA-RDA-A1.1-01Archive",
            "CA-RDA-A1.1-01Model",
            "CA-RDA-A1.1-01MA",
            "CA-RDA-A1.1-01MM",
            "CA-RDA-A1.2-01Archive",
            "CA-RDA-A1.2-01Model",
            "CA-RDA-A2-01MA",
            "CA-RDA-A2-01MM",
            "CA-RDA-I1-01Archive",
            "CA-RDA-I1-01Model",
            "CA-RDA-I1-01MA",
            "CA-RDA-I1-01MM",
            "CA-RDA-I1-02Archive - to check if needed for archive",
            "CA-RDA-I1-02Model",
            "CA-RDA-I1-02MA",
            "CA-RDA-I1-02MM",
            "CA-RDA-I2-01Archive",
            "CA-RDA-I2-01Model",
            "CA-RDA-I2-01MA",
            "CA-RDA-I2-01MM",
            "CA-RDA-I3-01Archive",
            "CA-RDA-I3-01Model",
            "CA-RDA-I3-01MA",
            "CA-RDA-I3-01MM",
            "CA-RDA-I3-02Archive",
            "CA-RDA-I3-02Model",
            "CA-RDA-I3-02MA",
            "CA-RDA-I3-02MM",
            "CA-RDA-I3-03MA",
            "CA-RDA-I3-03MM",
            "CA-RDA-I3-04MA",
            "CA-RDA-I3-04MM",
            "CA-RDA-R1-01MA",
            "CA-RDA-R1-01MM",
            "CA-RDA-R1.1-01MA",
            "CA-RDA-R1.1-01MM",
            "CA-RDA-R1.1-02MA",
            "CA-RDA-R1.1-02MM",
            "CA-RDA-R1.1-03MA",
            "CA-RDA-R1.1-03MM",
            "CA-RDA-R1.2-01MA",
            "CA-RDA-R1.2-01MM",
            "CA-RDA-R1.2-02MA",
            "CA-RDA-R1.2-02MM",
            "CA-RDA-R1.3-01Archive",
            "CA-RDA-R1.3-01Model",
            "CA-RDA-R1.3-01MA",
            "CA-RDA-R1.3-01MM",
            "CA-RDA-R1.3-02Archive",
            "CA-RDA-R1.3-02Model",
            "CA-RDA-R1.3-02MA",
            "CA-RDA-R1.3-02MM",
            "CA-RDA-R1.3-03MA",
            "CA-RDA-R1.3-03MM",
        ]
    )
    session_id = str(uuid4())


class IndicatorFactory(factory.Factory):
    class Meta:
        model = Indicator

    name = factory.Iterator(
        [
            "CA-RDA-F1-01Archive",
            "CA-RDA-F1-01Model",
            "CA-RDA-F1-01MA",
            "CA-RDA-F1-01MM",
            "CA-RDA-F1-02Archive",
            "CA-RDA-F1-02Model",
            "CA-RDA-F1-02MA",
            "CA-RDA-F1-02MM",
            "CA-RDA-F2-01MA",
            "CA-RDA-F2-01MM",
            "CA-RDA-F3-01MA",
            "CA-RDA-F3-01MM",
            "CA-RDA-F4-01MA",
            "CA-RDA-F4-01MM",
            "CA-RDA-A1-01MA",
            "CA-RDA-A1-01MM",
            "CA-RDA-A1-02Archive",
            "CA-RDA-A1-02Model",
            "CA-RDA-A1-02MA",
            "CA-RDA-A1-02MM",
            "CA-RDA-A1-03Archive",
            "CA-RDA-A1-03Model",
            "CA-RDA-A1-03MA",
            "CA-RDA-A1-03MM",
            "CA-RDA-A1-04Archive",
            "CA-RDA-A1-04Model",
            "CA-RDA-A1-04MA",
            "CA-RDA-A1-04MM",
            "CA-RDA-A1-05Archive",
            "CA-RDA-A1-05Model",
            "CA-RDA-A1.1-01Archive",
            "CA-RDA-A1.1-01Model",
            "CA-RDA-A1.1-01MA",
            "CA-RDA-A1.1-01MM",
            "CA-RDA-A1.2-01Archive",
            "CA-RDA-A1.2-01Model",
            "CA-RDA-A2-01MA",
            "CA-RDA-A2-01MM",
            "CA-RDA-I1-01Archive",
            "CA-RDA-I1-01Model",
            "CA-RDA-I1-01MA",
            "CA-RDA-I1-01MM",
            "CA-RDA-I1-02Archive - to check if needed for archive",
            "CA-RDA-I1-02Model",
            "CA-RDA-I1-02MA",
            "CA-RDA-I1-02MM",
            "CA-RDA-I2-01Archive",
            "CA-RDA-I2-01Model",
            "CA-RDA-I2-01MA",
            "CA-RDA-I2-01MM",
            "CA-RDA-I3-01Archive",
            "CA-RDA-I3-01Model",
            "CA-RDA-I3-01MA",
            "CA-RDA-I3-01MM",
            "CA-RDA-I3-02Archive",
            "CA-RDA-I3-02Model",
            "CA-RDA-I3-02MA",
            "CA-RDA-I3-02MM",
            "CA-RDA-I3-03MA",
            "CA-RDA-I3-03MM",
            "CA-RDA-I3-04MA",
            "CA-RDA-I3-04MM",
            "CA-RDA-R1-01MA",
            "CA-RDA-R1-01MM",
            "CA-RDA-R1.1-01MA",
            "CA-RDA-R1.1-01MM",
            "CA-RDA-R1.1-02MA",
            "CA-RDA-R1.1-02MM",
            "CA-RDA-R1.1-03MA",
            "CA-RDA-R1.1-03MM",
            "CA-RDA-R1.2-01MA",
            "CA-RDA-R1.2-01MM",
            "CA-RDA-R1.2-02MA",
            "CA-RDA-R1.2-02MM",
            "CA-RDA-R1.3-01Archive",
            "CA-RDA-R1.3-01Model",
            "CA-RDA-R1.3-01MA",
            "CA-RDA-R1.3-01MM",
            "CA-RDA-R1.3-02Archive",
            "CA-RDA-R1.3-02Model",
            "CA-RDA-R1.3-02MA",
            "CA-RDA-R1.3-02MM",
            "CA-RDA-R1.3-03MA",
            "CA-RDA-R1.3-03MM",
        ]
    )
    sub_group = factory.LazyAttribute(lambda obj: obj.name.split("-")[2])
    group = factory.LazyAttribute(lambda obj: obj.sub_group[0])
    priority = factory.LazyFunction(lambda: TaskPriority.essential)
    question = factory.Faker("paragraph", nb_sentences=1)
    short = factory.Faker("paragraph", nb_sentences=2)
    description = factory.Faker("paragraph", nb_sentences=4)
