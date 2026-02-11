from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Indian Legal AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://indian-legal-ai-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Indian Legal AI API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/test")
def test():
    return {"message": "API is working!"}
