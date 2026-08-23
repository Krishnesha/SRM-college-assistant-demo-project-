from typing import List, Dict, Any

class OpportunityRecommender:
    """
    Recommendation Engine for CampusAI.
    Maps natural language student interests to college opportunities based STRICTLY on ground truth metadata.
    """

    @classmethod
    def recommend(cls, interests: List[str], opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        matched_opps = []

        for opp in opportunities:
            opp_id = opp["id"]
            matched_domains = []
            reasons = []

            domains = opp.get("domains", [])
            cat = opp.get("category", "")
            name = opp.get("name", "")

            if "ai" in interests:
                if opp_id == "edgenova-26":
                    matched_domains.append("Computational Intelligence & ACM SIGAI association")
                    reasons.append("National 24-hr hackathon organized with ACM SIGAI focusing on AI and software.")
                elif opp_id == "siggraph-srm-ktr":
                    matched_domains.append("R&D Domain")
                    reasons.append("Focuses on Research, Innovation, and building future-oriented AI/graphics projects.")
                elif opp_id == "ai-game-jam":
                    matched_domains.append("AI Game Integration")
                    reasons.append("Focuses on AI game design and showcase.")

            if "coding" in interests:
                if opp_id == "edgenova-26":
                    matched_domains.append("Hackathon Coding")
                    reasons.append("24-hour national hackathon for building coding projects.")
                elif opp_id == "siggraph-srm-ktr":
                    matched_domains.append("Web Dev Domain")
                    reasons.append("Focuses on coding, web development, and connecting systems.")
                elif opp_id == "microsoft-student-ambassadors-srm":
                    matched_domains.append("Technical Mentorship & Cloud Coding")
                    reasons.append("Student ambassador program empowering peers through coding and technology.")

            if "design" in interests:
                if opp_id == "tedx-srmist":
                    matched_domains.append("Creatives Domain")
                    reasons.append("Design, visual media, and creative branding for TEDxSRMIST.")
                elif opp_id == "siggraph-srm-ktr":
                    matched_domains.append("Creative Domain")
                    reasons.append("Design, visualization, and inspiring visual change.")

            if "game" in interests:
                if opp_id == "ai-game-jam":
                    matched_domains.append("Game Design & Development")
                    reasons.append("Dedicated 3-day competition to design, develop, and showcase games.")

            if "research" in interests:
                if opp_id == "siggraph-srm-ktr":
                    matched_domains.append("R&D Domain")
                    reasons.append("Research and innovating for future technologies.")
                elif opp_id == "tedx-srmist":
                    matched_domains.append("Curations Domain")
                    reasons.append("Researching ideas worth spreading and talk content.")

            if "leadership" in interests:
                if opp_id == "tedx-srmist":
                    matched_domains.append("Operations & Sponsorship")
                    reasons.append("Leadership in event operations, logistics, and corporate partnerships.")
                elif opp_id == "microsoft-student-ambassadors-srm":
                    matched_domains.append("Community Leadership")
                    reasons.append("Leading student tech initiatives and organizing events.")
                elif opp_id == "siggraph-srm-ktr":
                    matched_domains.append("Corporate Domain")
                    reasons.append("Planning, collaborating, and organizational management.")

            if "prize" in interests:
                if opp.get("prize_numeric", 0) > 0:
                    matched_domains.append(f"Prize Pool: {opp['prize_pool']}")
                    reasons.append(f"Offers substantial reward ({opp['prize_pool']}).")

            if matched_domains:
                matched_opps.append({
                    "opportunity": opp,
                    "matched_domains": matched_domains,
                    "reasons": reasons
                })

        # Default fallback if no specific interest keyword matched
        if not matched_opps:
            for opp in opportunities[:3]:
                matched_opps.append({
                    "opportunity": opp,
                    "matched_domains": ["General Campus Opportunity"],
                    "reasons": [f"Popular active opportunity in college: {opp['name']}."]
                })

        return {
            "interests_searched": interests,
            "recommendations": matched_opps
        }
