# Dearly AI: System Design

Dearly is built on a "Sense-Think-Verify" architecture designed to provide deeply personalized gifting recommendations through a conversational interface.

## Architecture Overview

```mermaid
graph TD
    User([User]) <--> Frontend[Streamlit / React Frontend]
    Frontend <--> API[FastAPI Orchestrator]
    
    subgraph AI Layer (Sense-Think-Verify)
        API --> Sense[Sense Layer: Context Extraction]
        Sense -->|User Context| Think[Think Layer: RAG & Reasoning]
        Think -->|Gift Concepts| API
    end
    
    subgraph Data Layer
        API <--> DB[(Supabase PostgreSQL)]
        Think <--> VectorDB[(pgvector: Strategy Store)]
        Sense <--> LLM[Gemini / Groq LLM]
        Think <--> LLM
    end
    
    API --> Verify[Verify Layer: User Feedback]
    Verify -->|Ratings & Copies| DB
```

## The Three Pillars

### 1. Sense (Context Extraction)
The **Sense Layer** identifies the core drivers behind a gift. It doesn't just look for "a watch"; it extracts:
- **Who & Occasion**: The recipient and the event.
- **Passions & Challenges**: What they love or what's annoying them daily.
- **Budget & Value**: The financial limit and the preference for "Utility vs. WOW".

### 2. Think (RAG & Reasoning)
The **Think Layer** uses the extracted context to find or generate the perfect *concept*.
- **RAG Pipeline**: Retrieves proven gifting strategies from a vector database (pgvector) based on the recipient's profile.
- **LLM Reasoning**: Synthesizes the strategies into 3 unique, personalized gift ideas with a confidence score and reasoning.

### 3. Verify (Feedback Loop)
The **Verify Layer** ensures the system learns and improves.
- **User Ratings**: Users provide star ratings on suggested ideas.
- **Success Tracking**: When a user copies a "Gifting Note", it's marked as a successful recommendation in the database.

## Technology Stack
- **Languages**: Python (Backend), SQL (Database)
- **Frameworks**: FastAPI, Streamlit
- **AI**: Gemini API / Groq (Llama Model)
- **Database**: Supabase (PostgreSQL + pgvector)
