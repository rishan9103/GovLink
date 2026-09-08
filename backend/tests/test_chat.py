def test_chat_missing_message(client):
    response = client.post("/api/chat", json={"language": "en"})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INVALID_REQUEST"


def test_chat_valid_message(client):
    response = client.post("/api/chat", json={"message": "Who is eligible for PM-KISAN?", "language": "en"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "answer" in payload
    assert payload["language"] == "en"
    assert "sources" in payload
