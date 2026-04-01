import pytest
from unittest.mock import patch
from rag_pipeline import get_strategy_cards

@patch("rag_pipeline.generate_embedding")
@patch("rag_pipeline.match_strategies")
def test_mock_rag_pipeline(mock_match, mock_embed):
    mock_embed.return_value = [0.1] * 768
    mock_match.return_value = [
        {"name": "Morning Routine Fix", "description": "Gifts that fix morning rush hour.", "similarity": 0.95},
        {"name": "Clutter Buster", "description": "Organize small spaces.", "similarity": 0.88}
    ]
    
    context = {"preference_type": "utility", "frustrations": ["coffee gets cold"]}
    results = get_strategy_cards(context)
    
    assert len(results) == 2
    assert results[0]["name"] == "Morning Routine Fix"
    mock_embed.assert_called_once()
    mock_match.assert_called_once()
