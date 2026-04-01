from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_chat_intake():
    response = client.post("/api/chat/intake", json={
        "user_id": "u1",
        "recipient_id": "r1",
        "message": "My budget is $50 for a gift for my partner complaining about cold coffee.",
        "current_context": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["confidence_score"] == 100

def test_get_strategies():
    response = client.post("/api/strategies", json={
        "context": {"preference_type": "utility", "frustrations": ["cold coffee"]}
    })
    assert response.status_code == 200
    assert len(response.json()["strategies"]) == 3

@patch("main.generate_why_note")
def test_generate_note(mock_note):
    mock_note.return_value = "Hey! Hope this helps with the coffee."
    response = client.post("/api/generate-note", json={
        "recipient_name": "Alex",
        "strategy_name": "Morning Fix",
        "gift_idea": "Ember Mug",
        "context": {"frustrations": ["cold coffee"]}
    })
    assert response.status_code == 200
    assert response.json()["note"] == "Hey! Hope this helps with the coffee."
