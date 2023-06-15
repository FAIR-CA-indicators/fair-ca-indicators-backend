from app.dependencies.settings import get_settings


def test_indicators_list(test_client):
    config = get_settings()
    # FIXME: Put this as a setting
    with open(config.indicators_path, "r") as file:
        indicators = [line.split(",")[0].strip('"') for line in file.readlines()]

    indicators_list = indicators[1:]

    res = test_client.get("/indicators")
    assert res.status_code == 200

    indicators_data = res.json()
    for indicator in indicators_data:
        assert indicator["name"] in indicators_list

        res = test_client.get(f"/indicators/{indicator['name']}")
        assert res.status_code == 200
        assert res.json() == indicator
