
def test_update_task(test_client):
    response = test_client.patch("/blabla")
    assert response.status_code == 404




#     path: Union[HttpUrl, FileUrl, FilePath] = None
#     has_archive: Optional[bool]
#     has_model: Optional[bool]
#     has_archive_metadata: Optional[bool]
#     is_model_standard: Optional[bool]
#     is_archive_standard: Optional[bool]
#     is_model_metadata_standard: Optional[bool]
#     is_archive_metadata_standard: Optional[bool]
#     is_biomodel: Optional[bool]
#     is_pmr: Optional[bool]
#     subject_type: SubjectType

