import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.retrieval.engine import RetrievalEngine
from backend.reasoning.query_parser import QueryParser
from backend.reasoning.answer_generator import AnswerGenerator
from backend.reasoning.recommender import OpportunityRecommender
from backend.reasoning.deadline import DeadlineRadar
from backend.validation.guardrails import GroundingGuardrail
from backend.ingestion.ingest import NoticeIngestionEngine

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

retrieval_engine = RetrievalEngine(DATA_DIR)
ingestion_engine = NoticeIngestionEngine(DATA_DIR)

class handler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/opportunities" or path.endswith("/opportunities"):
            retrieval_engine.load_knowledge_base()
            opps = retrieval_engine.opportunities
            radar_data = DeadlineRadar.get_radar_summary(opps)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"opportunities": radar_data}).encode("utf-8"))
            return

        elif path == "/api/radar" or path.endswith("/radar"):
            retrieval_engine.load_knowledge_base()
            opps = retrieval_engine.opportunities
            radar_summary = DeadlineRadar.get_radar_summary(opps)
            
            grouped = {
                "today": [o for o in radar_summary if o["radar"]["status"] == "TODAY"],
                "soon": [o for o in radar_summary if o["radar"]["status"] == "SOON"],
                "upcoming": [o for o in radar_summary if o["radar"]["status"] == "UPCOMING"],
                "unavailable": [o for o in radar_summary if o["radar"]["status"] == "UNAVAILABLE"]
            }
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(grouped).encode("utf-8"))
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            body_data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body_data = {}

        if path == "/api/query" or path.endswith("/query"):
            raw_query = body_data.get("query", "").strip()
            if not raw_query:
                self._set_headers(400, "application/json")
                self.wfile.write(json.dumps({"error": "Empty query provided"}).encode("utf-8"))
                return

            retrieval_engine.load_knowledge_base()
            parsed_query = QueryParser.parse(raw_query)

            retrieved = retrieval_engine.search_opportunities(
                query=parsed_query["normalized_query"],
                entity_ids=parsed_query["entities"],
                interests=parsed_query["interests"]
            )

            is_refusal, refusal_msg = GroundingGuardrail.check_missing_information_queries(parsed_query, retrieved)

            if is_refusal:
                response_payload = {
                    "answer": refusal_msg,
                    "sources": [e for e in parsed_query["entities"] if e],
                    "intent": parsed_query["intent"],
                    "confidence": "HIGH (Grounded Refusal)",
                    "type": "refusal"
                }
            elif parsed_query["is_vague"]:
                response_payload = AnswerGenerator.generate_vague_query_response(retrieval_engine.opportunities)
                response_payload["intent"] = "VAGUE_QUERY"
            elif parsed_query["intent"] == "NOTICE_SUMMARY" and retrieved:
                response_payload = AnswerGenerator.generate_notice_summary(retrieved[0])
                response_payload["intent"] = "NOTICE_SUMMARY"
            elif parsed_query["intent"] == "COMPARISON":
                response_payload = AnswerGenerator.generate_comparison(retrieved or retrieval_engine.opportunities)
                response_payload["intent"] = "COMPARISON"
            elif parsed_query["intent"] == "RECOMMENDATION" or (parsed_query["interests"] and not parsed_query["entities"]):
                rec_res = OpportunityRecommender.recommend(parsed_query["interests"], retrieval_engine.opportunities)
                response_payload = AnswerGenerator.generate_recommendation_response(rec_res)
                response_payload["intent"] = "RECOMMENDATION"
            elif retrieved:
                response_payload = AnswerGenerator.generate_factual_response(parsed_query, retrieved)
            else:
                response_payload = {
                    "answer": GroundingGuardrail.REFUSAL_MESSAGE,
                    "sources": [],
                    "intent": parsed_query["intent"],
                    "type": "refusal"
                }

            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(response_payload).encode("utf-8"))
            return

        elif path == "/api/recommend" or path.endswith("/recommend"):
            interests = body_data.get("interests", [])
            retrieval_engine.load_knowledge_base()
            rec_res = OpportunityRecommender.recommend(interests, retrieval_engine.opportunities)
            payload = AnswerGenerator.generate_recommendation_response(rec_res)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        elif path == "/api/ingest" or path.endswith("/ingest"):
            notice_text = body_data.get("text", "")
            raw_record = body_data.get("record")

            if raw_record:
                success, msg = ingestion_engine.ingest_opportunity(raw_record)
            elif notice_text:
                extracted = ingestion_engine.simulate_ocr_extraction(notice_text)
                success, msg = ingestion_engine.ingest_opportunity(extracted)
            else:
                success, msg = False, "No 'text' or 'record' provided for ingestion."

            self._set_headers(200 if success else 400, "application/json")
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
