import logging

logger = logging.getLogger(__name__)


def test_main(test_client):
    response = test_client.get("/", follow_redirects=True)
    assert response.status_code == 200
