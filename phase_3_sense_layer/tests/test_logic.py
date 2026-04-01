from logic import calculate_confidence_score, generate_clarification_prompt

def test_confidence_score_full():
    data = {
        "budget": "$50",
        "preference_type": "utility",
        "frustrations": ["cold coffee", "losing keys"],
        "has_relationship_context": True
    }
    assert calculate_confidence_score(data) == 100

def test_confidence_score_partial():
    data = {
        "budget": None,
        "preference_type": "utility",
        "frustrations": [],
        "has_relationship_context": False
    }
    assert calculate_confidence_score(data) == 30
    
def test_clarification_prompt():
    data = {"budget": None, "preference_type": "utility"}
    prompt = generate_clarification_prompt(data)
    assert "budget" in prompt
    assert "annoyances" in prompt
