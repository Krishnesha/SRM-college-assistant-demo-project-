import re

class QueryParser:
    """
    Query Parser for CampusAI.
    Handles intent detection, typo normalization, entity extraction, and query cleaning.
    """
    
    TYPO_MAP = {
        "ambassdor": "ambassador",
        "ambasador": "ambassador",
        "edgenova": "edgenova",
        "edgenova'26": "edgenova",
        "siggraph": "siggraph",
        "tedx": "tedx",
        "gamejam": "game jam",
        "hackthon": "hackathon",
        "hackaton": "hackathon",
        "eligiblity": "eligibility",
        "deline": "deadline",
        "dead line": "deadline",
        "dead-line": "deadline",
        "fee": "fee",
        "prizepool": "prize pool",
        "prize": "prize"
    }

    ENTITY_ALIASES = {
        "edgenova-26": ["edgenova", "edgenova'26", "edgenova 26", "edge nova"],
        "ai-game-jam": ["ai game jam", "game jam", "gamejam", "game competition", "gaming event", "game event"],
        "tedx-srmist": ["tedx", "tedxsrmist", "tedx srmist"],
        "siggraph-srm-ktr": ["siggraph", "siggraph srm", "siggraph ktr"],
        "microsoft-student-ambassadors-srm": [
            "microsoft", "microsoft student ambassadors", "microsoft ambassador", 
            "microsoft ambassadors", "msa", "microsoft last date"
        ]
    }

    INTENT_PATTERNS = [
        (r"\bsummariz(e|ation)|summary\b", "NOTICE_SUMMARY"),
        (r"\bcompar(e|ison)|vs|better|cheaper|highest prize|biggest prize\b", "COMPARISON"),
        (r"\bdeadline|due|last date|last day|when is .* due|closing date\b", "DEADLINE_QUERY"),
        (r"\bfee|cost|price|ticket|screening fee|registration fee|how much\b", "FEE_QUERY"),
        (r"\bprize|money|reward|highest prize|cash|pool\b", "PRIZE_QUERY"),
        (r"\beligib(le|ility)|can (ug|pg|i|students)|who can\b", "ELIGIBILITY_QUERY"),
        (r"\bdate|when|schedule|timing|timeline|what day\b", "DATE_QUERY"),
        (r"\bvenue|where|location|hall|room\b", "VENUE_QUERY"),
        (r"\bcontact|phone|number|who to call|organizer|coordinator|faculty\b", "CONTACT_QUERY"),
        (r"\b(like|interested in|want to join|recommend|suggest|what can i|options for)\b", "RECOMMENDATION"),
        (r"\bclub|organization|chapter|recruit|join\b", "CLUB_RECOMMENDATION"),
        (r"\bevent|hackathon|competition|opportunity|what's there|what's happening|upcoming\b", "EVENT_SEARCH"),
    ]

    @classmethod
    def normalize_text(cls, text: str) -> str:
        text = text.lower().strip()
        # Replace common typos
        for typo, correction in cls.TYPO_MAP.items():
            text = re.sub(r'\b' + re.escape(typo) + r'\b', correction, text)
        return text

    @classmethod
    def parse(cls, raw_query: str) -> dict:
        normalized = cls.normalize_text(raw_query)
        
        # 1. Detect Intent
        detected_intent = "GENERAL_INFORMATION"
        for pattern, intent in cls.INTENT_PATTERNS:
            if re.search(pattern, normalized):
                detected_intent = intent
                break

        # Check for vague query e.g. "what's there?", "hi", "hello", "what is available?"
        if len(normalized.split()) <= 3 and any(w in normalized for w in ["what's there", "what is there", "available", "events", "anything"]):
            detected_intent = "VAGUE_QUERY"

        # 2. Extract Mentioned Entities
        mentioned_entities = []
        for entity_id, aliases in cls.ENTITY_ALIASES.items():
            for alias in aliases:
                if alias in normalized:
                    if entity_id not in mentioned_entities:
                        mentioned_entities.append(entity_id)

        # Special check for "siggraph deadline" or "faculty coordinator"
        is_siggraph_deadline = "siggraph" in normalized and ("deadline" in normalized or "last date" in normalized or "due" in normalized)
        is_faculty_coordinator = "faculty" in normalized or "coordinator" in normalized

        # 3. Extract Interest Keywords
        interests = []
        interest_keywords = {
            "ai": ["ai", "artificial intelligence", "machine learning", "r&d", "research"],
            "coding": ["coding", "code", "programming", "hackathon", "web dev", "developer", "software"],
            "design": ["design", "creative", "graphics", "visual", "ui", "ux"],
            "game": ["game", "gaming", "game dev", "game jam", "unity"],
            "research": ["research", "r&d", "innovate", "curation"],
            "leadership": ["leadership", "management", "operations", "corporate", "sponsorship"],
            "prize": ["prize", "high prize", "money", "reward"]
        }
        for category, kws in interest_keywords.items():
            if any(kw in normalized for kw in kws):
                interests.append(category)

        return {
            "raw_query": raw_query,
            "normalized_query": normalized,
            "intent": detected_intent,
            "entities": mentioned_entities,
            "interests": interests,
            "is_siggraph_deadline": is_siggraph_deadline,
            "is_faculty_coordinator": is_faculty_coordinator,
            "is_vague": detected_intent == "VAGUE_QUERY" or normalized in ["what's there?", "what is there", "help", "options"]
        }
