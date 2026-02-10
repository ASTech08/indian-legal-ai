"""
Case Law Service
Searches and retrieves case laws from Indian Kanoon and other public sources
"""

from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import re
from loguru import logger
from utils.config import settings

class CaseLawService:
    """Service for searching and retrieving case laws"""
    
    def __init__(self):
        self.indiankanoon_base = settings.INDIANKANOON_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_cases(
        self,
        query: str,
        topics: List[str],
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for relevant case laws
        
        Args:
            query: Search query
            topics: Legal topics identified
            limit: Maximum number of results
            
        Returns:
            List of case law dictionaries
        """
        try:
            logger.info(f"Searching case laws for: {query[:100]}")
            
            # Search Indian Kanoon
            indiankanoon_results = await self._search_indiankanoon(query, limit)
            
            # Enhance with topics
            enhanced_results = self._enhance_with_topics(indiankanoon_results, topics)
            
            # Rank by relevance
            ranked_results = self._rank_by_relevance(enhanced_results, query)
            
            return ranked_results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching case laws: {e}", exc_info=True)
            return []
    
    async def find_similar_cases(
        self,
        case_facts: str,
        legal_issues: List[str],
        jurisdiction: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Find similar cases for outcome prediction
        
        Args:
            case_facts: Facts of the case
            legal_issues: Legal questions
            jurisdiction: Court jurisdiction
            limit: Maximum results
            
        Returns:
            Similar cases with outcomes
        """
        try:
            logger.info("Finding similar cases...")
            
            # Construct search query from facts and issues
            search_query = self._construct_similarity_query(case_facts, legal_issues)
            
            # Search with jurisdiction filter
            results = await self._search_indiankanoon(
                search_query,
                limit,
                jurisdiction=jurisdiction
            )
            
            # Extract outcomes
            cases_with_outcomes = []
            for case in results:
                outcome = await self._extract_outcome(case)
                case['outcome'] = outcome
                cases_with_outcomes.append(case)
            
            return cases_with_outcomes
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}", exc_info=True)
            return []
    
    async def get_case_details(self, case_id: str) -> Optional[Dict]:
        """
        Get full details of a specific case
        
        Args:
            case_id: Unique identifier for the case
            
        Returns:
            Complete case details
        """
        try:
            url = f"{self.indiankanoon_base}/doc/{case_id}/"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch case {case_id}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract case details
            details = {
                'id': case_id,
                'title': self._extract_title(soup),
                'court': self._extract_court(soup),
                'date': self._extract_date(soup),
                'judges': self._extract_judges(soup),
                'full_text': self._extract_full_text(soup),
                'citations': self._extract_citations(soup),
                'url': url
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error fetching case details: {e}", exc_info=True)
            return None
    
    async def _search_indiankanoon(
        self,
        query: str,
        limit: int,
        jurisdiction: Optional[str] = None
    ) -> List[Dict]:
        """Search Indian Kanoon"""
        try:
            # Clean and prepare query
            clean_query = self._clean_query(query)
            
            # Construct search URL
            search_url = f"{self.indiankanoon_base}/search/"
            params = {
                'formInput': clean_query,
                'pagenum': 0
            }
            
            if jurisdiction:
                params['jurisdictions'] = jurisdiction
            
            response = await self.client.get(search_url, params=params)
            
            if response.status_code != 200:
                logger.warning("Indian Kanoon search failed")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:limit]:
                try:
                    result = self._parse_search_result(div)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Error parsing result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Indian Kanoon: {e}", exc_info=True)
            return []
    
    def _parse_search_result(self, result_div) -> Optional[Dict]:
        """Parse individual search result"""
        try:
            # Extract title and link
            title_tag = result_div.find('a', class_='cite_tag')
            if not title_tag:
                return None
            
            title = title_tag.get_text(strip=True)
            link = title_tag.get('href', '')
            
            # Extract case ID from link
            case_id_match = re.search(r'/doc/(\d+)/', link)
            case_id = case_id_match.group(1) if case_id_match else ''
            
            # Extract snippet/summary
            snippet_div = result_div.find('div', class_='snippets')
            summary = snippet_div.get_text(strip=True) if snippet_div else ''
            
            # Extract metadata
            meta_div = result_div.find('div', class_='metadata')
            court = ''
            date = ''
            year = ''
            
            if meta_div:
                meta_text = meta_div.get_text()
                # Parse court, date, etc.
                court_match = re.search(r'([A-Z][a-z]+ (?:High )?Court)', meta_text)
                court = court_match.group(1) if court_match else ''
                
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', meta_text)
                date = date_match.group(1) if date_match else ''
                
                year_match = re.search(r'\((\d{4})\)', meta_text)
                year = year_match.group(1) if year_match else ''
            
            return {
                'id': case_id,
                'title': title,
                'summary': summary,
                'court': court,
                'date': date,
                'year': year,
                'url': f"{self.indiankanoon_base}{link}",
                'relevance': 0.0  # Will be calculated later
            }
            
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
            return None
    
    def _enhance_with_topics(
        self,
        results: List[Dict],
        topics: List[str]
    ) -> List[Dict]:
        """Enhance results with topic matching"""
        for result in results:
            # Count topic matches in title and summary
            matches = 0
            combined_text = f"{result['title']} {result['summary']}".lower()
            
            for topic in topics:
                if topic.lower() in combined_text:
                    matches += 1
            
            result['topic_matches'] = matches
        
        return results
    
    def _rank_by_relevance(
        self,
        results: List[Dict],
        query: str
    ) -> List[Dict]:
        """Rank results by relevance score"""
        query_terms = set(query.lower().split())
        
        for result in results:
            score = 0.0
            
            # Base score from topic matches
            score += result.get('topic_matches', 0) * 2.0
            
            # Score from query term matches
            combined_text = f"{result['title']} {result['summary']}".lower()
            term_matches = sum(1 for term in query_terms if term in combined_text)
            score += term_matches * 1.0
            
            # Bonus for Supreme Court cases
            if 'Supreme Court' in result.get('court', ''):
                score += 1.5
            
            # Bonus for recent cases
            year = result.get('year', '')
            if year and year.isdigit():
                year_int = int(year)
                if year_int >= 2020:
                    score += 1.0
                elif year_int >= 2015:
                    score += 0.5
            
            result['relevance'] = score
        
        # Sort by relevance
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
    
    def _construct_similarity_query(
        self,
        case_facts: str,
        legal_issues: List[str]
    ) -> str:
        """Construct search query from case facts"""
        # Extract key terms from facts
        # Simplified - in production, use NLP for better extraction
        query_parts = legal_issues[:3]  # Top 3 issues
        
        # Add key terms from facts
        fact_terms = case_facts.split()[:20]  # First 20 words
        query_parts.extend(fact_terms)
        
        return ' '.join(query_parts)
    
    async def _extract_outcome(self, case: Dict) -> str:
        """Extract case outcome (Plaintiff/Defendant/Settled)"""
        # Fetch full case text if needed
        summary = case.get('summary', '').lower()
        
        # Simple keyword matching
        # In production, use ML model for better accuracy
        if any(word in summary for word in ['dismissed', 'rejected', 'no merit']):
            return 'Defendant'
        elif any(word in summary for word in ['allowed', 'granted', 'favor of plaintiff']):
            return 'Plaintiff'
        elif any(word in summary for word in ['settled', 'compromise']):
            return 'Settled'
        
        return 'Unknown'
    
    def _clean_query(self, query: str) -> str:
        """Clean and prepare search query"""
        # Remove special characters
        clean = re.sub(r'[^\w\s]', ' ', query)
        # Remove extra spaces
        clean = ' '.join(clean.split())
        return clean
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract case title"""
        title_tag = soup.find('h1')
        return title_tag.get_text(strip=True) if title_tag else ''
    
    def _extract_court(self, soup: BeautifulSoup) -> str:
        """Extract court name"""
        # Look for court in metadata or heading
        court_pattern = r'(Supreme Court|High Court|District Court)'
        text = soup.get_text()
        match = re.search(court_pattern, text)
        return match.group(1) if match else ''
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract case date"""
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        text = soup.get_text()
        match = re.search(date_pattern, text)
        return match.group(1) if match else ''
    
    def _extract_judges(self, soup: BeautifulSoup) -> List[str]:
        """Extract judge names"""
        # Look for BEFORE or BENCH section
        judges = []
        text = soup.get_text()
        
        before_match = re.search(r'BEFORE:?\s*(.+?)(?:\n\n|JUDGMENT)', text, re.IGNORECASE)
        if before_match:
            judges_text = before_match.group(1)
            judges = [j.strip() for j in judges_text.split(',')]
        
        return judges
    
    def _extract_full_text(self, soup: BeautifulSoup) -> str:
        """Extract full case text"""
        # Get main content div
        content_div = soup.find('div', class_='judgments')
        if content_div:
            return content_div.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_citations(self, soup: BeautifulSoup) -> List[str]:
        """Extract case citations"""
        citations = []
        # Look for citation patterns like [2020] 5 SCC 123
        citation_pattern = r'\[(\d{4})\]\s+\d+\s+[A-Z]+\s+\d+'
        text = soup.get_text()
        matches = re.findall(citation_pattern, text)
        return list(set(matches))  # Unique citations
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Singleton instance
case_law_service = CaseLawService()
