def test_get_services(client):
    response = client.get("/api/services")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "services" in payload

    response_category = client.get("/api/categories")
    assert response_category.status_code == 200
    payload_category = response_category.get_json()
    assert payload_category["success"] is True
    assert "categories" in payload_category
