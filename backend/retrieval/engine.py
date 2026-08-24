import json
import os
from typing import List, Dict, Any, Optional

class RetrievalEngine:
    """
    Local-first Field-Aware Knowledge Retrieval Engine for CampusAI.
    Matches queries strictly against local JSON data without external API calls.
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.opportunities: List[Dict[str, Any]] = []
        self.notices: List[Dict[str, Any]] = []
        self.clubs: List[Dict[str, Any]] = []
        self.load_knowledge_base()

    def load_knowledge_base(self):
        possible_dirs = [
            self.data_dir,
            os.path.join(os.getcwd(), "data"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")),
            "/var/task/data"
        ]
        
        target_dir = None
        for p in possible_dirs:
            if p and os.path.exists(os.path.join(p, "opportunities.json")):
                target_dir = p
                break
        
        if not target_dir:
            target_dir = self.data_dir

        opp_path = os.path.join(target_dir, "opportunities.json")
        notices_path = os.path.join(target_dir, "notices.json")
        clubs_path = os.path.join(target_dir, "clubs.json")

        if os.path.exists(opp_path):
            with open(opp_path, "r", encoding="utf-8") as f:
                self.opportunities = json.load(f)

        if os.path.exists(notices_path):
            with open(notices_path, "r", encoding="utf-8") as f:
                self.notices = json.load(f)

        if os.path.exists(clubs_path):
            with open(clubs_path, "r", encoding="utf-8") as f:
                self.clubs = json.load(f)

    def get_opportunity_by_id(self, opp_id: str) -> Optional[Dict[str, Any]]:
        for opp in self.opportunities:
            if opp["id"] == opp_id:
                return opp
        return None

    def search_opportunities(
        self, 
        query: str, 
        entity_ids: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        
        # 1. If explicit entity IDs were parsed, return those first
        if entity_ids:
            results = []
            for eid in entity_ids:
                opp = self.get_opportunity_by_id(eid)
                if opp and opp not in results:
                    results.append(opp)
            if results:
                return results

        # 2. Field-aware scoring search
        query_words = [w.lower() for w in query.split() if len(w) > 2]
        scored_opps = []

        for opp in self.opportunities:
            score = 0
            searchable_text = " ".join([
                opp.get("name", ""),
                opp.get("category", ""),
                opp.get("type", ""),
                opp.get("organization", ""),
                opp.get("theme", ""),
                " ".join(opp.get("domains", [])),
                " ".join(opp.get("eligibility", [])),
                opp.get("notes", "")
            ]).lower()

            for word in query_words:
                if word in searchable_text:
                    score += 2
                if word in opp.get("name", "").lower():
                    score += 5
                if word in opp.get("category", "").lower():
                    score += 3

            if interests:
                for interest in interests:
                    if interest == "ai" and any(k in searchable_text for k in ["ai", "computational intelligence", "machine learning", "r&d"]):
                        score += 4
                    elif interest == "coding" and any(k in searchable_text for k in ["coding", "hackathon", "web dev", "computational"]):
                        score += 4
                    elif interest == "design" and any(k in searchable_text for k in ["design", "creative", "graphics"]):
                        score += 4
                    elif interest == "game" and any(k in searchable_text for k in ["game", "gaming"]):
                        score += 5
                    elif interest == "research" and any(k in searchable_text for k in ["research", "r&d", "curations"]):
                        score += 4
                    elif interest == "leadership" and any(k in searchable_text for k in ["operations", "corporate", "sponsorship", "ambassador"]):
                        score += 4

            if score > 0:
                scored_opps.append((score, opp))

        # Sort by score descending
        scored_opps.sort(key=lambda x: x[0], reverse=True)
        return [opp for score, opp in scored_opps]

    def get_notice_for_opportunity(self, opp_id: str) -> Optional[Dict[str, Any]]:
        for n in self.notices:
            if n.get("opportunity_id") == opp_id:
                return n
        return None

    def get_all_opportunities() -> List[Dict[str, Any]]:
        return self.opportunities
