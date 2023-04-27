def test_update_task(test_client):
    response = test_client.patch("/blabla")
    assert response.status_code == 404
