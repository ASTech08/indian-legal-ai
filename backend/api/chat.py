"""
Chat API Endpoints
Handles conversational legal AI interactions
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
import asyncio
from loguru import logger

from services.legal_ai_service import legal_ai_service
from services.document_processor import document_processor
from utils.auth import get_current_user
from models.user import User
from models.conversation import Conversation, Message
from utils.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    include_sources: bool = True
    stream: bool = False

class ChatResponse(BaseModel):
    message_id: str
    response: str
    sources: List[dict] = []
    conversation_id: str
    metadata: dict = {}

class DocumentUploadRequest(BaseModel):
    conversation_id: str
    analysis_type: str = "comprehensive"

# Endpoints

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the legal AI
    
    Handles:
    - Legal queries
    - Document analysis requests
    - Drafting requests
    - Research questions
    """
    try:
        logger.info(f"User {current_user.id} sent message: {request.message[:100]}")
        
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=request.message[:100]  # First message as title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get conversation history
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        history_list = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Generate AI response
        ai_response = await legal_ai_service.generate_response(
            query=request.message,
            conversation_history=history_list,
            include_sources=request.include_sources
        )
        
        # Save AI message
        ai_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response['response'],
            sources=ai_response.get('sources', []),
            metadata=ai_response.get('metadata', {})
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Update conversation
        conversation.updated_at = ai_message.created_at
        db.commit()
        
        return ChatResponse(
            message_id=str(ai_message.id),
            response=ai_response['response'],
            sources=ai_response.get('sources', []),
            conversation_id=str(conversation.id),
            metadata=ai_response.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message with streaming response
    Returns Server-Sent Events (SSE) stream
    """
    try:
        async def generate_stream():
            """Generate streaming response"""
            try:
                # Get conversation history
                if request.conversation_id:
                    history = db.query(Message).filter(
                        Message.conversation_id == request.conversation_id
                    ).order_by(Message.created_at).all()
                    
                    history_list = [
                        {"role": msg.role, "content": msg.content}
                        for msg in history
                    ]
                else:
                    history_list = []
                
                # Stream response in chunks
                # Note: This is a simplified version
                # In production, implement proper streaming with LangChain
                
                response = await legal_ai_service.generate_response(
                    query=request.message,
                    conversation_history=history_list,
                    include_sources=request.include_sources
                )
                
                # Simulate streaming by chunking response
                words = response['response'].split()
                chunk_size = 5
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size])
                    yield f"data: {chunk}\n\n"
                    await asyncio.sleep(0.05)  # Small delay for effect
                
                # Send sources at the end
                if response.get('sources'):
                    yield f"data: [SOURCES]{response['sources']}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                yield f"data: [ERROR]{str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = None,
    analysis_type: str = "comprehensive",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a legal document
    
    Supported formats: PDF, DOCX, DOC, TXT, JPG, PNG
    """
    try:
        logger.info(f"User {current_user.id} uploading document: {file.filename}")
        
        # Validate file
        if not document_processor.is_valid_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(document_processor.allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        processed = await document_processor.process_document(
            file_content,
            file.filename,
            current_user.id
        )
        
        # Determine document type
        document_type = document_processor.detect_document_type(processed['text'])
        
        # Analyze document
        analysis = await legal_ai_service.analyze_document(
            document_text=processed['text'],
            document_type=document_type,
            analysis_type=analysis_type
        )
        
        # Create conversation if not exists
        if not conversation_id:
            conversation = Conversation(
                user_id=current_user.id,
                title=f"Analysis: {file.filename}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = str(conversation.id)
        
        # Save document message
        doc_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=f"[Uploaded document: {file.filename}]",
            metadata={
                "file_name": file.filename,
                "file_size": len(file_content),
                "document_type": document_type
            }
        )
        db.add(doc_message)
        
        # Save analysis message
        analysis_content = f"""**Document Analysis**

**Type**: {document_type}

**Analysis**:
{analysis['analysis']}

**Key Points**:
{chr(10).join('- ' + point for point in analysis['key_points'])}

**Risks Identified**:
{chr(10).join('- ' + risk['description'] for risk in analysis['risks'])}

**Suggestions**:
{chr(10).join('- ' + suggestion for suggestion in analysis['suggestions'])}
"""
        
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=analysis_content,
            metadata=analysis['metadata']
        )
        db.add(ai_message)
        db.commit()
        
        return {
            "message": "Document analyzed successfully",
            "conversation_id": conversation_id,
            "document_type": document_type,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversation history"""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).all()
        
        return [
            {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific conversation with messages"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "sources": msg.sources,
                    "metadata": msg.metadata,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
