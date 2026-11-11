"""
JobShield AI - Automated Verification & Test Suite
Validates Document Extraction, NLP & Rules Engine, Database, and Web Routes.
"""

import os
import unittest
from app import app
from database import init_db, get_scan, get_analytics_summary
from document_extractor import extract_text_from_pdf, clean_extracted_text
from analysis_engine import JobShieldAnalyzer
from samples import SAMPLE_OFFERS

class JobShieldTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        self.analyzer = JobShieldAnalyzer()

    def test_database_initialization(self):
        """Tests database tables and initial analytics."""
        init_db()
        stats = get_analytics_summary()
        self.assertIn("total_scans", stats)
        self.assertIn("high_risk", stats)

    def test_high_risk_scam_detection(self):
        """Tests that upfront fee + Telegram recruiter flags as HIGH RISK."""
        text = SAMPLE_OFFERS["scam_upfront_fee"]["text"]
        result = self.analyzer.analyze(text)

        self.assertEqual(result["risk_level"], "HIGH")
        self.assertGreaterEqual(result["risk_score"], 65)
        
        # Verify specific critical flag was raised
        flag_ids = [f["id"] for f in result["flags"]]
        self.assertIn("financial_demand", flag_ids)
        self.assertIn("free_webmail_only", flag_ids)
        self.assertTrue(result["extracted_data"]["free_email_detected"])

    def test_medium_risk_vague_role_detection(self):
        """Tests that copy-paste work from home with unrealistic pay flags MEDIUM RISK."""
        text = SAMPLE_OFFERS["suspicious_vague_role"]["text"]
        result = self.analyzer.analyze(text)

        self.assertIn(result["risk_level"], ["MEDIUM", "HIGH"])
        flag_categories = [f["category"] for f in result["flags"]]
        self.assertTrue(any("Role" in c or "Promise" in c or "Communication" in c for c in flag_categories))

    def test_low_risk_legitimate_internship(self):
        """Tests that a legitimate corporate offer with no fees flags LOW RISK."""
        text = SAMPLE_OFFERS["legitimate_internship"]["text"]
        result = self.analyzer.analyze(text)

        self.assertEqual(result["risk_level"], "LOW")
        self.assertLess(result["risk_score"], 35)
        self.assertFalse(result["extracted_data"]["free_email_detected"])

    def test_pdf_extraction(self):
        """Tests PyMuPDF extraction on generated sample PDF."""
        pdf_path = os.path.join(os.path.dirname(__file__), "test_samples", "sample_scam_offer.pdf")
        if os.path.exists(pdf_path):
            text, meta = extract_text_from_pdf(pdf_path)
            self.assertIn("Apex", text)
            self.assertIn("1,850", text)
            self.assertEqual(meta["extractor_used"], "PyMuPDF")

    def test_web_routes(self):
        """Tests Flask HTTP routes."""
        # 1. Landing Page
        r_home = self.client.get("/")
        self.assertEqual(r_home.status_code, 200)
        self.assertIn(b"JobShield", r_home.data)
        self.assertIn(b"Team HackNova", r_home.data)

        # 2. Guide Page
        r_guide = self.client.get("/guide")
        self.assertEqual(r_guide.status_code, 200)
        self.assertIn(b"Safety Guide", r_guide.data)

        # 3. About Pitch Page
        r_about = self.client.get("/about")
        self.assertEqual(r_about.status_code, 200)
        self.assertIn(b"HackNova", r_about.data)

        # 4. History Page
        r_history = self.client.get("/history")
        self.assertEqual(r_history.status_code, 200)

        # 5. Sample API
        r_sample = self.client.get("/api/sample/scam_upfront_fee")
        self.assertEqual(r_sample.status_code, 200)
        self.assertIn(b"Apex", r_sample.data)

        # 6. Analyze Form Submission
        r_post = self.client.post("/analyze", data={
            "input_type": "text",
            "job_title_input": "Automated Test Scam Scan",
            "job_text": SAMPLE_OFFERS["scam_upfront_fee"]["text"]
        }, follow_redirects=True)
        self.assertEqual(r_post.status_code, 200)
        self.assertIn(b"HIGH RISK ASSESSMENT", r_post.data)
        self.assertIn(b"Upfront Monetary Requirement", r_post.data)

if __name__ == "__main__":
    unittest.main()
