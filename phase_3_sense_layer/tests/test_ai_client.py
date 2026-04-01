import pytest
from unittest.mock import patch

@patch("google.generativeai.GenerativeModel")
def test_mock_gemini_extraction(mock_model):
    mock_instance = mock_model.return_value
    # Mocking standard valid JSON response from Gemini
    mock_instance.generate_content.return_value.text = '```json\n{"budget": "$100", "preference_type": "wow", "frustrations": ["always loses keys"], "has_relationship_context": true}\n```'
    
    from ai_client import extract_gifting_context
    result = extract_gifting_context("I want a $100 gift that wows my sister who loses keys.")
    assert result["budget"] == "$100"
    assert result["preference_type"] == "wow"
    assert "always loses keys" in result["frustrations"]
    assert result["has_relationship_context"] is True
