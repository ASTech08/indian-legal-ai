import os
import io
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from PyPDF2 import PdfReader

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
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian legal AI assistant. You help users understand Indian laws, legal procedures, and provide guidance on legal matters. Always cite relevant sections of law when applicable (e.g., IPC, CrPC, CPC, Constitution of India). Be accurate, helpful, and professional. Provide practical advice while reminding users to consult a qualified lawyer for specific legal matters."
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

# Document analysis endpoint with PDF support
@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        text_content = ""
        
        if file.filename.lower().endswith('.pdf'):
            # Extract text from PDF
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PdfReader(pdf_file)
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                    
                if not text_content.strip():
                    text_content = "PDF file appears to be empty or contains only images. Please ensure the PDF contains selectable text."
                    
            except Exception as pdf_error:
                raise HTTPException(status_code=400, detail=f"Error extracting PDF text: {str(pdf_error)}")
                
        elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
            # Try to decode as text
            try:
                text_content = content.decode('utf-8')
            except:
                try:
                    text_content = content.decode('latin-1')
                except:
                    raise HTTPException(status_code=400, detail="Unable to decode text file")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, TXT, DOC, or DOCX file.")
        
        # Limit content to avoid token limits (keep first 10000 characters)
        if len(text_content) > 10000:
            text_content = text_content[:10000] + "\n\n[Document truncated due to length...]"
        
        # Use OpenAI to analyze the document
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert legal document analyzer specializing in Indian law. 
                    Analyze documents and provide:
                    1. Summary of key terms and clauses
                    2. Legal issues and potential risks
                    3. Compliance with Indian laws (Contract Act, Consumer Protection Act, etc.)
                    4. Red flags or concerning provisions
                    5. Recommendations for improvement
                    
                    Be specific, professional, and cite relevant Indian laws when applicable."""
                },
                {
                    "role": "user",
                    "content": f"Please analyze this legal document:\n\nFilename: {file.filename}\nSize: {len(content)} bytes\n\nContent:\n{text_content}"
                }
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "filename": file.filename,
            "size": len(content),
            "pages": len(pdf_reader.pages) if file.filename.lower().endswith('.pdf') else None,
            "analysis": analysis
        }
        
    except HTTPException as he:
        raise he
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
                    "content": """You are an expert on Indian case law and legal precedents. 
                    When asked about legal cases, provide:
                    1. Relevant landmark Supreme Court and High Court cases
                    2. Proper legal citations (e.g., AIR, SCC format)
                    3. Brief facts of the case
                    4. Legal principles established
                    5. Current applicability
                    
                    Focus on Indian judiciary. Be accurate with case names and citations."""
                },
                {
                    "role": "user",
                    "content": f"Find relevant Indian case law and legal precedents related to: {request.query}\n\nProvide specific case names, citations, and key principles."
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
                    "content": f"""You are an expert Indian legal document drafter. 
                    Generate a professional {request.document_type} following:
                    1. Indian legal standards and formats
                    2. Proper legal language and terminology
                    3. All necessary clauses and provisions
                    4. Compliance with Indian laws
                    
                    Format the document professionally with proper sections, numbering, and structure."""
                },
                {
                    "role": "user",
                    "content": f"Generate a {request.document_type} with the following details:\n\n{request.details}\n\nMake it complete, professional, and ready to use."
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        document_text = response.choices[0].message.content
        
        return {
            "document_type": request.document_type,
            "document": document_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
