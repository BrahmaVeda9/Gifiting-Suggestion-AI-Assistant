import httpx
import json

API_BASE = "http://localhost:8001/api"

def run_e2e_flow():
    print("\n=============================================")
    print("      DEARLY E2E PIPELINE EXECUTION          ")
    print("=============================================\n")
    
    with httpx.Client() as client:
        # 1. Chat Intake
        print(">>> 1. SENSE LAYER: Sending Chat Intake")
        intake_payload = {
            "user_id": "giver_123",
            "recipient_id": "recip_456",
            "message": "My budget is $100 for a gift for my partner. They prefer practical things. Frustrated by constantly losing their keys and phones.",
            "current_context": {}
        }
        print(f"User Input: '{intake_payload['message']}'\n")
        
        response = client.post(f"{API_BASE}/chat/intake", json=intake_payload)
        data = response.json()
        if "confidence_score" not in data:
            print(f"[API ERROR] Status: {response.status_code}, Response: {data}")
            return
        print(f"[API Response] Confidence Score: {data['confidence_score']}%")
        print(f"[API Response] Extracted Traits: {json.dumps(data['extracted_data'], indent=2)}")
        
        context = data['extracted_data']
        
        # 2. Get Strategies
        print("\n>>> 2. THINK LAYER: Fetching Strategies from Vector RAG")
        strategy_payload = {"context": context}
        response = client.post(f"{API_BASE}/strategies", json=strategy_payload)
        strategies = response.json()["strategies"]
        
        print("[API Response] Found top strategies:")
        for idx, strategy in enumerate(strategies):
            print(f"  {idx+1}. {strategy['name']} - {strategy['description']}")
        
        chosen_strategy = strategies[0]['name']
        print(f"\n[Decision] Synthesizing based on chosen strategy: {chosen_strategy}")
        
        # 3. Generate Note
        print("\n>>> 3. ACT LAYER: Generating the 'Why' Note via Gemini")
        note_payload = {
            "recipient_name": "Jamie",
            "strategy_name": chosen_strategy,
            "gift_idea": "Bluetooth Key and Phone Trackers",
            "context": context
        }
        response = client.post(f"{API_BASE}/generate-note", json=note_payload)
        note = response.json()["note"]
        
        print(f"\n[API Response] Final Generated Note:\n----------------------------------------\n{note}\n----------------------------------------\n")
        
    print("================ E2E PIPELINE COMPLETE =================\n")

if __name__ == "__main__":
    run_e2e_flow()
