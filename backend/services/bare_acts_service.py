from typing import List, Dict

class BareActsService:
    """Service for searching Indian Bare Acts"""
    
    async def search_sections(self, query: str, topics: List[str]) -> List[Dict]:
        """Search for relevant bare act sections"""
        # Simplified version - returns mock data for now
        return [
            {
                "act_name": "Indian Penal Code",
                "section": "420",
                "text": "Cheating and dishonestly inducing delivery of property",
                "url": "https://www.indiacode.nic.in/",
                "relevance": 0.9
            }
        ]

bare_acts_service = BareActsService()
