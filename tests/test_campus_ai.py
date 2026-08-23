import unittest
import os
import sys

# Ensure root folder is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.retrieval.engine import RetrievalEngine
from backend.reasoning.query_parser import QueryParser
from backend.reasoning.answer_generator import AnswerGenerator
from backend.reasoning.recommender import OpportunityRecommender
from backend.reasoning.deadline import DeadlineRadar
from backend.validation.guardrails import GroundingGuardrail

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

class TestCampusAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.retrieval = RetrievalEngine(DATA_DIR)

    def test_01_prize_retrieval(self):
        """1. Correct retrieval: 'What's the EDGENOVA prize?' -> ₹40,000"""
        parsed = QueryParser.parse("What's the EDGENOVA prize?")
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["id"], "edgenova-26")
        
        resp = AnswerGenerator.generate_factual_response(parsed, results)
        self.assertIn("₹40,000", resp["answer"])

    def test_02_deadline_retrieval(self):
        """2. Deadline: 'When is Microsoft Student Ambassadors deadline?' -> 21 August 2026"""
        parsed = QueryParser.parse("When is Microsoft Student Ambassadors deadline?")
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["id"], "microsoft-student-ambassadors-srm")
        
        resp = AnswerGenerator.generate_factual_response(parsed, results)
        self.assertIn("21 August 2026", resp["answer"])

    def test_03_eligibility_retrieval(self):
        """3. Eligibility: 'Can PG students join EDGENOVA?' -> Yes (UG & PG eligible)"""
        parsed = QueryParser.parse("Can PG students join EDGENOVA?")
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        self.assertTrue(len(results) > 0)
        
        resp = AnswerGenerator.generate_factual_response(parsed, results)
        self.assertIn("PG", resp["answer"])

    def test_04_missing_information_siggraph_deadline(self):
        """4. Missing information: 'When is SIGGRAPH deadline?' -> Zero-hallucination Refusal"""
        parsed = QueryParser.parse("When is SIGGRAPH deadline?")
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        
        is_refusal, refusal_msg = GroundingGuardrail.check_missing_information_queries(parsed, results)
        self.assertTrue(is_refusal)
        self.assertIn("I don't have enough information in the college data to answer that confidently", refusal_msg)
        self.assertIn("does not provide a specific application deadline", refusal_msg)

    def test_05_recommendation_ai_research(self):
        """5. Recommendation: 'I like AI and research.' -> SIGGRAPH R&D and EDGENOVA"""
        parsed = QueryParser.parse("I like AI and research.")
        rec_res = OpportunityRecommender.recommend(parsed["interests"], self.retrieval.opportunities)
        matched_ids = [item["opportunity"]["id"] for item in rec_res["recommendations"]]
        
        self.assertIn("edgenova-26", matched_ids)
        self.assertIn("siggraph-srm-ktr", matched_ids)

    def test_06_misspelling_handling(self):
        """6. Misspelling: 'when is microsoft ambassdor last date' -> 21 August 2026"""
        parsed = QueryParser.parse("when is microsoft ambassdor last date")
        self.assertIn("microsoft-student-ambassadors-srm", parsed["entities"])
        
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        resp = AnswerGenerator.generate_factual_response(parsed, results)
        self.assertIn("21 August 2026", resp["answer"])

    def test_07_unsupported_claim_website(self):
        """7. Unsupported claim: 'What's the official registration website for EDGENOVA?' -> No fake URL, QR code only"""
        parsed = QueryParser.parse("What's the official registration website for EDGENOVA?")
        results = self.retrieval.search_opportunities(parsed["normalized_query"], parsed["entities"])
        
        is_refusal, refusal_msg = GroundingGuardrail.check_missing_information_queries(parsed, results)
        self.assertTrue(is_refusal)
        self.assertIn("QR code", refusal_msg)
        self.assertNotIn("http://", refusal_msg)
        self.assertNotIn("https://", refusal_msg)

    def test_08_deadline_radar_evaluation(self):
        """8. Radar evaluation relative to 19 Aug 2026"""
        msa_opp = self.retrieval.get_opportunity_by_id("microsoft-student-ambassadors-srm")
        msa_radar = DeadlineRadar.evaluate_opportunity_deadline(msa_opp)
        self.assertEqual(msa_radar["status"], "SOON")
        self.assertIn("Due in 2 days", msa_radar["badge"])

        gamejam_opp = self.retrieval.get_opportunity_by_id("ai-game-jam")
        gamejam_radar = DeadlineRadar.evaluate_opportunity_deadline(gamejam_opp)
        self.assertEqual(gamejam_radar["status"], "TODAY")


if __name__ == "__main__":
    unittest.main()
