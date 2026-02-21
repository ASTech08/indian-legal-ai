import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Initialize FastAPI app
app = FastAPI(title="Indian Legal AI API")

# Get CORS origins from environment variable
cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
)

# Split the comma-separated string into a list
allowed_origins = [origin.strip() for origin in cors_origins_str.split(",")]

# Add the specific Vercel preview URL explicitly
allowed_origins.append("https://indian-legal-ai-frontend-y8gem6i2w-ashus-projects-918909e4.vercel.app")

# Remove duplicates
allowed_origins = list(set(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class SearchRequest(BaseModel):
    query: str

class DocumentRequest(BaseModel):
    document_type: str
    details: str

# Root endpoint
@app.get("/")
def root():
    return {"message": "Indian Legal AI API", "status": "running"}

# Health check
@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

# Test endpoint
@app.get("/api/test")
def test():
    return {"message": "API is working!"}

# Chat endpoint with OpenAI integration
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian legal AI assistant. You help users understand Indian laws, legal procedures, and provide guidance on legal matters. Always cite relevant sections of law when applicable. Be accurate, helpful, and professional."
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the AI response
        ai_response = response.choices[0].message.content
        
        return {"response": ai_response}
        
    except openai.AuthenticationError:
        raise HTTPException(status_code=500, detail="OpenAI API key is invalid or missing")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded. Please try again later.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Document analysis endpoint
@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        
        # Decode if it's a text file
        try:
            text_content = content.decode('utf-8')
        except:
            text_content = f"Binary file ({len(content)} bytes)"
        
        # Use OpenAI to analyze the document
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert legal document analyzer for Indian law. Analyze the provided document and provide insights on legal issues, risks, and recommendations."
                },
                {
                    "role": "user",
                    "content": f"Please analyze this legal document:\n\n{text_content[:4000]}"  # Limit to avoid token limits
                }
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "filename": file.filename,
            "size": len(content),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Case law search endpoint
@app.post("/api/search-cases")
async def search_cases(request: SearchRequest):
    try:
        # Use OpenAI to provide case law information
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert on Indian case law. When asked about legal cases, provide relevant landmark cases from Indian courts (Supreme Court, High Courts) with proper citations, facts, and legal principles established."
                },
                {
                    "role": "user",
                    "content": f"Find relevant Indian case law related to: {request.query}"
                }
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        cases_info = response.choices[0].message.content
        
        return {
            "query": request.query,
            "results": cases_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document generation endpoint
@app.post("/api/generate-document")
async def generate_document(request: DocumentRequest):
    try:
        # Use OpenAI to generate legal document
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert Indian legal document drafter. Generate a professional {request.document_type} document following Indian legal standards and formats."
                },
                {
                    "role": "user",
                    "content": f"Generate a {request.document_type} with the following details:\n\n{request.details}"
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        document_text = response.choices[0].message.content
        
        return {
            "document_type": request.document_type,
            "document": document_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
