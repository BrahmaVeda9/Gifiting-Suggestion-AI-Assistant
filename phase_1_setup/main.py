from fastapi import FastAPI

app = FastAPI(title="Dearly Phase 1", description="Phase 1 Setup for Dearly API")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Phase 1 setup is running properly."}
