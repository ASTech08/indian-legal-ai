"""
Core AI Service for Legal Intelligence
Handles legal reasoning, case law search, and document analysis
"""

from typing import List, Dict, Optional, Any
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import chromadb
from loguru import logger

from utils.config import settings
from services.case_law_service import CaseLawService
from services.bare_acts_service import BareActsService

class LegalAIService:
    """Main AI service for legal intelligence"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize vector store
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name="legal_knowledge",
            embedding_function=self.embeddings
        )
        
        # Initialize external services
        self.case_law_service = CaseLawService()
        self.bare_acts_service = BareActsService()
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Legal reasoning prompt
        self.legal_prompt = PromptTemplate(
            template="""You are an expert Indian legal AI assistant with deep knowledge of Indian laws, 
case precedents, and judicial reasoning. Your role is to provide accurate, well-sourced legal information.

Context from Indian Legal Database:
{context}

Conversation History:
{chat_history}

User Question: {question}

Instructions:
1. Analyze the question carefully to understand the legal issue
2. Search for relevant Bare Act sections and case laws
3. Provide clear explanation with proper legal reasoning
4. Cite specific sections and case references
5. If applicable, mention conflicting judgments
6. Provide practical implications
7. Include a disclaimer that this is informational, not legal advice

Response Format:
- Start with a direct answer
- Explain relevant legal provisions
- Cite case laws with proper references
- Mention any important caveats or exceptions
- End with practical next steps

Important:
- NEVER fabricate case laws or sections
- If unsure, say so clearly
- Always cite sources
- Distinguish between different courts' interpretations

Answer:""",
            input_variables=["context", "chat_history", "question"]
        )
    
    async def generate_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI response for legal query
        
        Args:
            query: User's legal question
            conversation_history: Previous messages
            include_sources: Whether to include source citations
            
        Returns:
            Dict with response, sources, and metadata
        """
        try:
            logger.info(f"Processing legal query: {query[:100]}...")
            
            # Step 1: Identify legal topics and entities
            topics = await self._extract_legal_topics(query)
            logger.info(f"Identified topics: {topics}")
            
            # Step 2: Search for relevant bare acts
            bare_acts = await self.bare_acts_service.search_sections(query, topics)
            
            # Step 3: Search for relevant case laws
            case_laws = await self.case_law_service.search_cases(query, topics)
            
            # Step 4: Retrieve from vector store
            vector_docs = self.vectorstore.similarity_search(query, k=5)
            
            # Step 5: Combine context
            context = self._build_context(bare_acts, case_laws, vector_docs)
            
            # Step 6: Format conversation history
            chat_history = self._format_chat_history(conversation_history)
            
            # Step 7: Generate response
            response = await self.llm.apredict(
                self.legal_prompt.format(
                    context=context,
                    chat_history=chat_history,
                    question=query
                )
            )
            
            # Step 8: Extract and format sources
            sources = []
            if include_sources:
                sources = self._extract_sources(bare_acts, case_laws)
            
            # Step 9: Add disclaimer
            response_with_disclaimer = self._add_disclaimer(response)
            
            return {
                "response": response_with_disclaimer,
                "sources": sources,
                "topics": topics,
                "metadata": {
                    "bare_acts_found": len(bare_acts),
                    "case_laws_found": len(case_laws),
                    "model": settings.OPENAI_MODEL
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            raise
    
    async def analyze_document(
        self,
        document_text: str,
        document_type: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze legal document
        
        Args:
            document_text: Full text of document
            document_type: Type (contract, fir, notice, etc.)
            analysis_type: Type of analysis needed
            
        Returns:
            Analysis results with insights and recommendations
        """
        try:
            logger.info(f"Analyzing {document_type} document...")
            
            # Create document-specific prompt
            analysis_prompt = self._get_analysis_prompt(document_type, analysis_type)
            
            # Split document into chunks if too large
            chunks = self.text_splitter.split_text(document_text)
            
            # Analyze each chunk
            chunk_analyses = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Analyzing chunk {i+1}/{len(chunks)}")
                analysis = await self.llm.apredict(
                    analysis_prompt.format(document=chunk)
                )
                chunk_analyses.append(analysis)
            
            # Combine analyses
            combined_analysis = self._combine_analyses(chunk_analyses)
            
            # Extract key points
            key_points = await self._extract_key_points(combined_analysis)
            
            # Identify risks
            risks = await self._identify_risks(document_text, document_type)
            
            # Suggest improvements
            suggestions = await self._suggest_improvements(
                document_text,
                document_type,
                risks
            )
            
            return {
                "analysis": combined_analysis,
                "key_points": key_points,
                "risks": risks,
                "suggestions": suggestions,
                "document_type": document_type,
                "metadata": {
                    "chunks_analyzed": len(chunks),
                    "total_length": len(document_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}", exc_info=True)
            raise
    
    async def draft_document(
        self,
        document_type: str,
        parameters: Dict[str, Any],
        style: str = "formal"
    ) -> Dict[str, Any]:
        """
        Draft legal document using AI
        
        Args:
            document_type: Type of document to draft
            parameters: Document-specific parameters
            style: Writing style (formal, citizen-friendly, court-ready)
            
        Returns:
            Generated document with metadata
        """
        try:
            logger.info(f"Drafting {document_type} document...")
            
            # Get drafting template
            template = self._get_drafting_template(document_type, style)
            
            # Search for relevant formats and precedents
            precedents = await self._search_document_precedents(document_type)
            
            # Generate document
            draft = await self.llm.apredict(
                template.format(
                    precedents=precedents,
                    **parameters
                )
            )
            
            # Add legal citations if applicable
            draft_with_citations = await self._add_legal_citations(
                draft,
                document_type
            )
            
            # Format document
            formatted_draft = self._format_document(
                draft_with_citations,
                document_type,
                style
            )
            
            return {
                "draft": formatted_draft,
                "document_type": document_type,
                "style": style,
                "metadata": {
                    "precedents_used": len(precedents),
                    "word_count": len(formatted_draft.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Error drafting document: {e}", exc_info=True)
            raise
    
    async def predict_outcome(
        self,
        case_facts: str,
        legal_issues: List[str],
        jurisdiction: str
    ) -> Dict[str, Any]:
        """
        Predict case outcome based on past precedents
        
        Args:
            case_facts: Facts of the case
            legal_issues: Legal questions involved
            jurisdiction: Court jurisdiction
            
        Returns:
            Prediction with confidence and reasoning
        """
        try:
            logger.info("Predicting case outcome...")
            
            # Search for similar past cases
            similar_cases = await self.case_law_service.find_similar_cases(
                case_facts,
                legal_issues,
                jurisdiction
            )
            
            # Analyze judicial trends
            trends = self._analyze_judicial_trends(similar_cases)
            
            # Generate prediction
            prediction_prompt = f"""Based on the following case facts and similar past cases, 
predict the likely outcome. Consider judicial trends and reasoning.

Case Facts:
{case_facts}

Legal Issues:
{', '.join(legal_issues)}

Similar Past Cases:
{self._format_cases_for_prediction(similar_cases)}

Judicial Trends:
{trends}

Provide:
1. Most likely outcome (Plaintiff/Defendant favor)
2. Confidence level (Low/Medium/High)
3. Key reasoning factors
4. Important precedents
5. Possible alternative outcomes

Remember: This is a probabilistic prediction, not a guarantee."""

            prediction = await self.llm.apredict(prediction_prompt)
            
            return {
                "prediction": prediction,
                "similar_cases": similar_cases[:5],  # Top 5
                "trends": trends,
                "disclaimer": "This prediction is based on past cases and should not be considered as legal advice or guaranteed outcome."
            }
            
        except Exception as e:
            logger.error(f"Error predicting outcome: {e}", exc_info=True)
            raise
    
    # Helper methods
    
    async def _extract_legal_topics(self, query: str) -> List[str]:
        """Extract legal topics from query"""
        topic_prompt = f"""Extract the main legal topics from this query. 
Return as comma-separated list.

Query: {query}

Topics (e.g., "criminal law, Section 138 NI Act, cheque bounce"):"""

        topics_str = await self.llm.apredict(topic_prompt)
        return [t.strip() for t in topics_str.split(',')]
    
    def _build_context(
        self,
        bare_acts: List[Dict],
        case_laws: List[Dict],
        vector_docs: List[Document]
    ) -> str:
        """Build context from multiple sources"""
        context_parts = []
        
        # Bare Acts
        if bare_acts:
            context_parts.append("Relevant Bare Act Sections:")
            for act in bare_acts[:3]:  # Top 3
                context_parts.append(
                    f"- {act['act_name']}, Section {act['section']}: {act['text']}"
                )
        
        # Case Laws
        if case_laws:
            context_parts.append("\nRelevant Case Laws:")
            for case in case_laws[:3]:  # Top 3
                context_parts.append(
                    f"- {case['title']} ({case['year']}): {case['summary']}"
                )
        
        # Vector store documents
        if vector_docs:
            context_parts.append("\nAdditional Context:")
            for doc in vector_docs[:2]:  # Top 2
                context_parts.append(f"- {doc.page_content[:200]}...")
        
        return "\n".join(context_parts)
    
    def _format_chat_history(
        self,
        history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Format conversation history"""
        if not history:
            return "No previous conversation"
        
        formatted = []
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)
    
    def _extract_sources(
        self,
        bare_acts: List[Dict],
        case_laws: List[Dict]
    ) -> List[Dict[str, str]]:
        """Extract and format sources"""
        sources = []
        
        for act in bare_acts[:5]:
            sources.append({
                "type": "bare_act",
                "title": f"{act['act_name']}, Section {act['section']}",
                "url": act.get('url', ''),
                "relevance": act.get('relevance', 0.0)
            })
        
        for case in case_laws[:5]:
            sources.append({
                "type": "case_law",
                "title": f"{case['title']} ({case['year']})",
                "url": case.get('url', ''),
                "court": case.get('court', ''),
                "relevance": case.get('relevance', 0.0)
            })
        
        return sources
    
    def _add_disclaimer(self, response: str) -> str:
        """Add legal disclaimer to response"""
        disclaimer = "\n\n---\n**Disclaimer**: This information is for educational purposes only and does not constitute legal advice. Please consult a qualified lawyer for specific legal matters."
        return response + disclaimer
    
    def _get_analysis_prompt(self, document_type: str, analysis_type: str) -> PromptTemplate:
        """Get document-specific analysis prompt"""
        templates = {
            "contract": """Analyze this contract thoroughly:

{document}

Provide:
1. Summary of key terms
2. Rights and obligations of each party
3. Potential risks or ambiguities
4. Missing clauses or provisions
5. Compliance with Indian Contract Act
6. Recommendations for improvement

Analysis:""",
            
            "fir": """Analyze this FIR:

{document}

Provide:
1. Alleged offenses and applicable sections
2. Strength of the complaint
3. Evidence mentioned
4. Procedural compliance
5. Possible defenses
6. Next steps

Analysis:""",
            
            "notice": """Analyze this legal notice:

{document}

Provide:
1. Nature of dispute
2. Legal claims made
3. Demands and deadlines
4. Strength of claims
5. Recommended response
6. Potential outcomes

Analysis:"""
        }
        
        template_text = templates.get(
            document_type,
            "Analyze this legal document:\n\n{document}\n\nAnalysis:"
        )
        
        return PromptTemplate(template=template_text, input_variables=["document"])
    
    async def _extract_key_points(self, analysis: str) -> List[str]:
        """Extract key points from analysis"""
        prompt = f"""Extract 5-7 key points from this analysis as bullet points:

{analysis}

Key Points:"""
        
        points_str = await self.llm.apredict(prompt)
        return [p.strip() for p in points_str.split('\n') if p.strip()]
    
    async def _identify_risks(
        self,
        document_text: str,
        document_type: str
    ) -> List[Dict[str, Any]]:
        """Identify legal risks in document"""
        risk_prompt = f"""Identify legal risks in this {document_type}:

{document_text[:2000]}

For each risk, provide:
- Description
- Severity (Low/Medium/High)
- Legal basis
- Mitigation suggestion

Risks:"""
        
        risks_str = await self.llm.apredict(risk_prompt)
        # Parse and structure risks
        # Simplified for now
        return [{"description": risks_str, "severity": "Medium"}]
    
    async def _suggest_improvements(
        self,
        document_text: str,
        document_type: str,
        risks: List[Dict]
    ) -> List[str]:
        """Suggest document improvements"""
        prompt = f"""Based on these risks, suggest improvements for this {document_type}:

Identified Risks:
{risks}

Suggestions:"""
        
        suggestions_str = await self.llm.apredict(prompt)
        return [s.strip() for s in suggestions_str.split('\n') if s.strip()]
    
    def _combine_analyses(self, analyses: List[str]) -> str:
        """Combine multiple chunk analyses"""
        return "\n\n".join(analyses)
    
    def _get_drafting_template(self, document_type: str, style: str) -> PromptTemplate:
        """Get document drafting template"""
        # Simplified - in production, use comprehensive templates
        return PromptTemplate(
            template=f"Draft a {style} {document_type} with the following details:\n\n{{precedents}}\n\nParameters: {{parameters}}\n\nDocument:",
            input_variables=["precedents", "parameters"]
        )
    
    async def _search_document_precedents(self, document_type: str) -> str:
        """Search for document format precedents"""
        # Query vector store for similar documents
        results = self.vectorstore.similarity_search(
            f"format template for {document_type}",
            k=2
        )
        return "\n\n".join([doc.page_content for doc in results])
    
    async def _add_legal_citations(self, draft: str, document_type: str) -> str:
        """Add appropriate legal citations"""
        # For now, return as-is
        # In production, parse and add citations
        return draft
    
    def _format_document(
        self,
        draft: str,
        document_type: str,
        style: str
    ) -> str:
        """Format document with proper structure"""
        # Add headers, footers, formatting
        return draft
    
    def _analyze_judicial_trends(self, cases: List[Dict]) -> str:
        """Analyze trends from similar cases"""
        if not cases:
            return "No similar cases found"
        
        # Simple trend analysis
        outcomes = [c.get('outcome', 'Unknown') for c in cases]
        plaintiff_wins = outcomes.count('Plaintiff')
        defendant_wins = outcomes.count('Defendant')
        
        return f"Out of {len(cases)} similar cases: Plaintiff won {plaintiff_wins}, Defendant won {defendant_wins}"
    
    def _format_cases_for_prediction(self, cases: List[Dict]) -> str:
        """Format cases for prediction prompt"""
        formatted = []
        for case in cases[:5]:
            formatted.append(
                f"- {case['title']}: {case['summary']} (Outcome: {case.get('outcome', 'N/A')})"
            )
        return "\n".join(formatted)

# Singleton instance
legal_ai_service = LegalAIService()
