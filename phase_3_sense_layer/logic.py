def calculate_confidence_score(extracted_data: dict) -> int:
    """
    Calculates the confidence score (0 to 100) based on the completeness of the data.
    The goal is to push users toward providing highly detailed context for perfect 'Relationship Intelligence'.
    """
    score = 0
    if extracted_data.get("budget"):
        score += 30
    if extracted_data.get("preference_type") in ["wow", "utility"]:
        score += 30
    if extracted_data.get("frustrations") and len(extracted_data["frustrations"]) > 0:
        score += 20
    if extracted_data.get("has_relationship_context"):
        score += 20
    return score

def generate_clarification_prompt(extracted_data: dict) -> str:
    """Returns exactly what questions the AI needs to ask the user to fill the gaps if score < 100."""
    missing = []
    if not extracted_data.get("budget"):
        missing.append("an estimated budget")
    if not extracted_data.get("preference_type"):
        missing.append("whether you prefer a 'wow factor' or a practical 'utility factor'")
    if not extracted_data.get("frustrations"):
        missing.append("any small daily annoyances or habits the recipient faces")
        
    if missing:
        return f"To give the most thoughtful recommendation, I still need to know about: {', '.join(missing)}."
    return 'Great! I have all the "Relationship Intelligence" info I need to create a strategy.'
