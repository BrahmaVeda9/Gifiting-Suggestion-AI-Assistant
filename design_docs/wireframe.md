# Dearly AI: Wireframe & User Flow

The interface is designed to feel like a high-end personal concierge service. It moves away from "cold AI" and into a "warm, boutique" aesthetic.

## High-Fidelity Mockup
![Dearly Boutique UI Mockup](file:///c:/Users/Brahma%20Veda/Desktop/Gifting%20Assistance%20AI/Gifiting-Suggestion-AI-Assistant/design_docs/wireframe.png)

## UI Component Structure

```mermaid
graph TD
    App[Main App Container]
    Sidebar[Sidebar: Boutique Successes]
    ChatArea[Main: Conversation View]
    Input[Chat Input: 'I'm thinking of a gift for...']
    
    subgraph Components
        Sidebar --> Metrics[Gift Tracker & Recent Successes]
        ChatArea --> UserMsg[User: Chat Bubble (Zig-Zag Right)]
        ChatArea --> AIMsg[AI: Chat Bubble (Zig-Zag Left)]
        ChatArea --> GiftCards[Result: 3 Translucent Concept Cards]
    end
    
    subgraph Card UI
        GiftCards --> Title[Title: Playfair Serif Font]
        GiftCards --> Reasoning[Reasoning: Empathetic Text]
        GiftCards --> Actions[Buttons: Note 💌 / Regenerate ✨]
        GiftCards --> Score[Badge: ✨ Match %]
    end
```

## User Journey: "The Golden Path"

1. **Intake**: A warm personalized greeting asking about the recipient.
2. **Context (Sense)**: As user describes the person, the sidebar highlights "Context Found" (Budget, Interests, Frustrations).
3. **Conceptualizing (Think)**: The bot processes and presents 3 *concepts*.
4. **Delivering (Verify)**: User selects an idea, generates a "Gifting Note 💌", and rates the experience.
5. **Success**: The gifted concept appears in the sidebar's "Boutique Successes" list for future reference.
