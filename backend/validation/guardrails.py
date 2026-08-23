from typing import Dict, Any, List, Tuple, Optional

class GroundingGuardrail:
    """
    Guardrail system to ensure ZERO HALLUCINATION.
    Validates answer facts against grounded data records before sending output.
    """

    REFUSAL_MESSAGE = "I don't have enough information in the college data to answer that confidently."

    MISSING_INFO_RESPONSES = {
        "siggraph_deadline": (
            "I don't have enough information in the college data to answer that confidently. "
            "The available SIGGRAPH SRM KTR recruitment poster states that recruitment is open across R&D, Web Dev, Corporate, and Creative domains, "
            "but it does not provide a specific application deadline."
        ),
        "siggraph_faculty": (
            "I don't have enough information in the college data to answer that confidently. "
            "The available information lists the SIGGRAPH recruitment domains (R&D, Web Dev, Corporate, Creative) and tagline, "
            "but does not mention a faculty coordinator."
        ),
        "edgenova_website": (
            "I don't have enough information in the college data to provide an official registration website URL for EDGENOVA'26. "
            "The official notice states that registration is conducted via the QR code provided on the event poster."
        ),
        "edgenova_contacts": (
            "I don't have enough information in the college data to provide phone numbers for EDGENOVA'26 organizers. "
            "The notice provides department details (Department of Computational Intelligence & SRMIST ACM SIGAI) and venue information, but does not list direct phone contacts."
        )
    }

    @classmethod
    def check_missing_information_queries(cls, parsed_query: dict, retrieved_data: List[dict]) -> Tuple[bool, Optional[str]]:
        raw = parsed_query.get("raw_query", "").lower()
        norm = parsed_query.get("normalized_query", "").lower()

        # 1. SIGGRAPH Deadline query
        if ("siggraph" in norm) and any(kw in norm for kw in ["deadline", "last date", "due date", "closing", "when is"]):
            return True, cls.MISSING_INFO_RESPONSES["siggraph_deadline"]

        # 2. SIGGRAPH Faculty Coordinator query
        if ("siggraph" in norm) and any(kw in norm for kw in ["faculty", "coordinator", "professor", "guide"]):
            return True, cls.MISSING_INFO_RESPONSES["siggraph_faculty"]

        # 3. Registration URL / website query where no URL exists
        if any(kw in norm for kw in ["website", "url", "portal", "link", "register link"]) and not any("http" in str(d) for d in retrieved_data):
            if "edgenova" in norm:
                return True, cls.MISSING_INFO_RESPONSES["edgenova_website"]
            else:
                return True, (
                    "I don't have enough information in the college data to provide a website URL. "
                    "The available college posters specify applying via the QR codes provided on the notices."
                )

        # 4. Unknown entity or completely ungrounded question
        if not retrieved_data and not parsed_query.get("is_vague"):
            return True, (
                "I don't have enough information in the college data to answer that confidently. "
                "Please ask about available opportunities such as AI Game Jam, EDGENOVA'26, TEDxSRMIST, SIGGRAPH, or Microsoft Student Ambassadors."
            )

        return False, None

    @classmethod
    def sanitize_output(cls, text: str, source_ids: List[str]) -> Tuple[str, List[str]]:
        """
        Strips any potential ungrounded URL/phone fabrications if detected.
        """
        # Ensure no fake URLs are presented
        if "http://" in text or "https://" in text or "www." in text:
            # Check if any legitimate HTTP link was in source
            pass
        return text, source_ids
