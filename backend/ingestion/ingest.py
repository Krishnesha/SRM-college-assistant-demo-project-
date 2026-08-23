import json
import os
import re
from typing import Dict, Any, List, Tuple

class NoticeIngestionEngine:
    """
    Ingestion engine for new poster/notice images or text data.
    Parses, validates, formats, and updates the local knowledge base.
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.opp_file = os.path.join(data_dir, "opportunities.json")
        self.notices_file = os.path.join(data_dir, "notices.json")

    def simulate_ocr_extraction(self, notice_text: str) -> Dict[str, Any]:
        """
        Simulates OCR / LLM extraction of raw notice text into structured opportunity schema.
        """
        # Basic regex pattern extraction for quick structured data creation
        lines = notice_text.strip().split("\n")
        title = lines[0] if lines else "New College Event"

        prize_match = re.search(r"₹\s*[\d,]+|prize.*[\d,]+", notice_text, re.I)
        fee_match = re.search(r"₹\s*[\d,]+.*fee|fee.*₹\s*[\d,]+|free", notice_text, re.I)
        date_match = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}", notice_text, re.I)

        opp_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        structured_record = {
            "id": opp_id,
            "name": title,
            "category": "event",
            "type": "College Notice / Event",
            "organization": "SRMIST",
            "theme": notice_text[:100] + "...",
            "dates": [],
            "date_display": date_match.group(0) if date_match else "See Notice",
            "deadline": None,
            "deadline_display": "Information unavailable",
            "venue": "SRM KTR Campus",
            "eligibility": ["UG", "PG"],
            "team_size": "Individual / Team",
            "registration_fee": fee_match.group(0) if fee_match else "Free",
            "prize_pool": prize_match.group(0) if prize_match else None,
            "domains": ["General"],
            "contacts": [],
            "application_method": "QR code on notice",
            "registration_method": "QR code on notice",
            "source": "ingested_notice",
            "confidence": 0.95
        }
        return structured_record

    def ingest_opportunity(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates and appends a new opportunity record to opportunities.json.
        """
        if not record.get("id") or not record.get("name"):
            return False, "Record must have 'id' and 'name' fields."

        opps = []
        if os.path.exists(self.opp_file):
            with open(self.opp_file, "r", encoding="utf-8") as f:
                opps = json.load(f)

        # Check for duplicates, update if existing
        existing_idx = -1
        for idx, o in enumerate(opps):
            if o["id"] == record["id"]:
                existing_idx = idx
                break

        if existing_idx >= 0:
            opps[existing_idx] = record
            msg = f"Updated existing opportunity '{record['id']}'."
        else:
            opps.append(record)
            msg = f"Successfully added new opportunity '{record['name']}' ({record['id']})."

        with open(self.opp_file, "w", encoding="utf-8") as f:
            json.dump(opps, f, indent=2)

        return True, msg
