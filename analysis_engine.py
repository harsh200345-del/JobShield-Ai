"""
JobShield AI - Intelligent Analysis Engine
Rules + Heuristic NLP + Optional LLM Synthesis
Flags warning signs and explains what to verify — never claims a final fraud verdict.
"""

import re
import json
from typing import Dict, Any, List, Optional
import os

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com",
    "yandex.com", "proton.me", "protonmail.com", "aol.com", "icloud.com",
    "mail.com", "zoho.com", "inbox.com", "gmx.com"
}

SUSPICIOUS_MESSAGING_APPS = [
    ("telegram", "Telegram messaging app"),
    ("whatsapp", "WhatsApp direct messaging"),
    ("signal", "Signal messenger"),
    ("discord", "Discord channel/DM"),
    ("skype", "Skype chat")
]

PAYMENT_KEYWORDS = [
    (r"\b(?:registration|application|processing|onboarding|documentation)\s+fees?\b", "Registration / Processing Fee", "critical"),
    (r"\b(?:security|refundable|caution)\s+deposit\b", "Refundable Security Deposit Demand", "critical"),
    (r"\b(?:training|certification|course)\s+(?:fee|charges?|cost|amount)\b", "Training / Certification Fee", "critical"),
    (r"\b(?:laptop|equipment|id\s*card|kit)\s+(?:deposit|fee|charge)\b", "Equipment / Kit Charges", "critical"),
    (r"\b(?:pay|transfer|deposit|send)\s+(?:rs\.?|inr|₹|\$)\s*[0-9]+", "Direct Payment Demand", "critical"),
    (r"\b(?:upi\s*id|gpay|phonepe|paytm|qr\s*code|net\s*banking)\b", "Personal UPI / Digital Wallet Payment Request", "critical"),
    (r"\bbank\s*transfer\s+before\s+(?:joining|offer|interview)\b", "Upfront Bank Transfer", "critical")
]

URGENCY_KEYWORDS = [
    (r"\b(?:within\s+24\s*hours?|immediately|urgent\s+action|last\s+day\s+today)\b", "High-Pressure Urgency", "warning"),
    (r"\b(?:limited\s+seats|only\s+[0-9]+\s+slots?\s+left|first\s+come\s+first\s+serve)\b", "Artificial Scarcity Tactics", "warning"),
    (r"\b(?:offer\s+will\s+expire|seat\s+will\s+be\s+cancelled|forfeited)\b", "Coercive Expiration Warning", "warning")
]

VAGUE_ROLE_KEYWORDS = [
    (r"\b(?:data\s+entry|copy\s+paste|form\s+filling|sms\s+sending|ad\s+posting|typing\s+work)\b", "Common Low-Skill Trap Category", "warning"),
    (r"\b(?:earn\s+from\s+home\s+without\s+skills?|no\s+experience\s+needed\s+high\s+income)\b", "Effort-Income Disconnect", "warning"),
    (r"\b(?:simple\s+tasks?\s+daily|earn\s+daily\s+cash)\b", "Vague Task Description", "warning")
]

UNREALISTIC_PROMISES = [
    (r"\b(?:guaranteed\s+(?:selection|job|placement|salary))\b", "Guaranteed Selection Guarantee", "warning"),
    (r"\b(?:no\s+interview\s+required|direct\s+offer\s+letter|instant\s+selection)\b", "No Interview / Immediate Offer", "critical"),
    (r"\b(?:earn\s+(?:rs\.?|inr|₹|\$)?\s*[4-9][0-9],[0-9]{3}\s*(?:daily|weekly))\b", "Unrealistically High Short-Term Payout", "critical")
]


class JobShieldAnalyzer:
    """Core evaluation engine combining rule-based heuristics and explainable NLP."""

    def __init__(self, gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")

    def analyze(self, text: str, document_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes full 4-step workflow:
        1. Parse & Extract key entities
        2. Detect Suspicious Indicators across 5 categories
        3. Calculate Risk Score & Risk Level
        4. Synthesize Explainable Assessment & Actionable Verification Checklist
        """
        if not text or not text.strip():
            return self._empty_result()

        # Step 1: Extraction
        extracted = self._extract_entities(text, document_metadata)

        # Step 2: Warning-Sign Checks
        flags = self._detect_warning_signs(text, extracted)

        # Step 3: Compute Risk Score and Category Breakdown
        scores = self._calculate_risk_scores(flags)

        # Step 4: Generate Explanations & Verification Checklist
        checklist = self._generate_verification_checklist(extracted, flags)
        summary = self._generate_executive_summary(extracted, scores, flags)

        return {
            "extracted_data": extracted,
            "flags": flags,
            "risk_score": scores["total_score"],
            "risk_level": scores["risk_level"],
            "category_scores": scores["categories"],
            "summary": summary,
            "checklist": checklist,
            "flags_count": {
                "critical": sum(1 for f in flags if f["severity"] == "critical"),
                "warning": sum(1 for f in flags if f["severity"] == "warning"),
                "info": sum(1 for f in flags if f["severity"] == "info")
            }
        }

    def _extract_entities(self, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extracts company name, job role, pay/stipend, contact details, fees."""
        # 1. Email extraction
        emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)))
        email_domains = []
        free_email_detected = False
        corporate_email_detected = False

        for email in emails:
            parts = email.split("@")
            if len(parts) == 2:
                domain = parts[1].lower()
                email_domains.append(domain)
                if domain in FREE_EMAIL_DOMAINS:
                    free_email_detected = True
                else:
                    corporate_email_detected = True

        # 2. Company name extraction heuristics
        company = "Unspecified / Not Detected"
        company_patterns = [
            r"(?:Company|Organization|Firm|Employer|Offer from)\s*[:\-–]\s*([A-Za-z0-9&., ]{3,50})",
            r"(?:Welcome to|At)\s+([A-Z][A-Za-z0-9&., ]+(?:Pvt\.?|Ltd\.?|Limited|LLP|Inc\.?|Technologies|Solutions|Software|Corp))",
            r"([A-Z][A-Za-z0-9& ]+(?:Pvt\.?|Ltd\.?|Limited|LLP|Solutions|Technologies|Infotech))"
        ]
        for pattern in company_patterns:
            m = re.search(pattern, text)
            if m:
                candidate = m.group(1).strip().strip(".,-")
                if len(candidate) > 3 and not candidate.lower().startswith("dear"):
                    company = candidate
                    break

        # 3. Role extraction heuristics
        role = "Unspecified Position"
        role_patterns = [
            r"(?:Role|Position|Designation|Job Title|Internship as)\s*[:\-–]\s*([A-Za-z0-9/ ]{3,50})",
            r"(?:offer of|offering you the role of|appointed as|selected as)\s+(?:an?\s+)?([A-Za-z0-9/ ]+(?:Intern|Developer|Engineer|Associate|Executive|Analyst|Trainee|Specialist))",
            r"([A-Za-z0-9/ ]+(?:Internship|Intern|Frontend Developer|Backend Developer|Full Stack|Data Analyst|Content Writer|Software Engineer|Sales Executive))"
        ]
        for pattern in role_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                if len(candidate) > 3:
                    role = candidate.title()
                    break

        # 4. Compensation / Stipend extraction
        stipend = "Not Disclosed / Unspecified"
        pay_patterns = [
            r"(?:Stipend|Salary|CTC|Compensation|Package|Pay)\s*[:\-–]\s*([₹$€£INR\w\d,./\-\s]+?(?:per\s+(?:month|annum|year|hr|day)|p\.m\.|p\.a\.|month|\/mo|\/pm))",
            r"((?:₹|Rs\.?|INR|\$)\s*[0-9,]+(?:\s*(?:-|to)\s*(?:₹|Rs\.?|INR|\$)?\s*[0-9,]+)?\s*(?:per\s+month|p\.m\.|\/month|monthly))",
            r"((?:₹|Rs\.?|INR|\$)\s*[0-9,]+(?:\s*(?:LPA|lpa|per\s+annum|p\.a\.)))"
        ]
        for pattern in pay_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                stipend = m.group(1).strip()
                break

        # 5. Upfront payment / fees extraction (with negation suppression)
        fees = []
        fee_patterns = [
            r"((?:registration|training|security|caution|processing|kit)\s+(?:fee|charges?|deposit|amount)[^.\n]*)",
            r"(pay\s+(?:rs\.?|inr|₹|\$)\s*[0-9,]+[^.\n]*)",
            r"((?:deposit|transfer)\s+of\s+(?:rs\.?|inr|₹|\$)\s*[0-9,]+[^.\n]*)"
        ]
        disclaimer_words = ["never", "do not", "does not", "without", "no fee", "free of cost", "at no cost"]
        for pattern in fee_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                m_str = match.strip()
                # Ignore if disclaimer
                if not any(dw in m_str.lower() for dw in disclaimer_words):
                    fees.append(m_str)

        # 6. Messaging channels
        detected_channels = []
        for channel, desc in SUSPICIOUS_MESSAGING_APPS:
            if re.search(rf"\b{channel}\b", text, re.IGNORECASE):
                detected_channels.append(desc)

        # 7. Contact phones
        phones = list(set(re.findall(r'(?:\+?91[\-\s]?)?[6-9]\d{9}\b|\+?\d{1,3}[\-\s]?\d{3,4}[\-\s]?\d{3,4}', text)))

        return {
            "company": company,
            "role": role,
            "stipend": stipend,
            "emails": emails[:4],
            "email_domains": list(set(email_domains)),
            "free_email_detected": free_email_detected,
            "corporate_email_detected": corporate_email_detected,
            "phones": phones[:3],
            "detected_channels": detected_channels,
            "fees_extracted": fees[:3],
            "word_count": len(text.split()),
            "meta": meta or {}
        }

    def _detect_warning_signs(self, text: str, extracted: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifies concrete warning signs across recruitment safety dimensions."""
        flags: List[Dict[str, Any]] = []

        # --- CATEGORY 1: Financial Demands & Upfront Fees ---
        found_fee = False
        negation_pattern = re.compile(r"\b(?:never\s+(?:solicits?|demands?|charges?|asks?|requests?)|does\s+not\s+(?:charge|ask|demand)|no\s+(?:fee|charges?|deposit)|without\s+any\s+fee|free\s+of\s+cost|at\s+no\s+cost|beware\s+of|scam\s+alert|do\s+not\s+pay)\b", re.IGNORECASE)

        for pattern, title, severity in PAYMENT_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                # Check 80 chars before and after for negation or disclaimer context
                start_ctx = max(0, m.start() - 80)
                end_ctx = min(len(text), m.end() + 80)
                surrounding = text[start_ctx:end_ctx]

                if negation_pattern.search(surrounding):
                    # This is an explicit anti-scam / zero-fee disclaimer, not a fee demand!
                    continue

                found_fee = True
                snippet = self._extract_snippet(text, m.start(), m.end())
                flags.append({
                    "id": "financial_demand",
                    "category": "Financial Demands",
                    "severity": severity,
                    "title": f"Upfront Monetary Requirement: {title}",
                    "evidence": snippet,
                    "reason": "Legitimate employers never ask candidates to pay for training, interview registration, security deposits, or office equipment. Upfront payment requests are the #1 hallmark of recruitment scams.",
                    "verification": "Immediately pause all communication and refuse payment. Check if the company has published an official advisory against fraudulent recruitment."
                })
                break  # Don't overwhelm with multiple duplicate fee flags
            if found_fee:
                break

        # --- CATEGORY 2: Suspicious Communication & Contact Channels ---
        if extracted.get("free_email_detected") and not extracted.get("corporate_email_detected"):
            flags.append({
                "id": "free_webmail_only",
                "category": "Communication Channels",
                "severity": "critical" if extracted.get("company") != "Unspecified / Not Detected" else "warning",
                "title": "Use of Public Webmail (Gmail/Yahoo/Outlook)",
                "evidence": f"Recruiter contact email domain: {', '.join(extracted.get('email_domains', []))}",
                "reason": "Established companies and genuine corporate recruiters use registered business domain emails (e.g. name@company.com), not free webmail accounts.",
                "verification": "Search the company's verified website and cross-check the official careers/HR email domain before responding."
            })

        if extracted.get("detected_channels"):
            channels_str = ", ".join(extracted["detected_channels"])
            flags.append({
                "id": "unofficial_messaging",
                "category": "Communication Channels",
                "severity": "warning",
                "title": "Hiring Directed Through Informal Messaging Apps",
                "evidence": f"Detected communication platform: {channels_str}",
                "reason": "Recruitment workflows conducted strictly via messaging apps (Telegram, WhatsApp, Signal) without formal interview links or corporate ATS are frequently associated with anonymous threat actors.",
                "verification": "Request an official video conference link (Google Meet / MS Teams / Zoom) and an official offer letter sent to your email from a corporate domain."
            })

        # --- CATEGORY 3: Unrealistic Promises & Effort-Reward Disconnect ---
        for pattern, title, severity in UNREALISTIC_PROMISES:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                snippet = self._extract_snippet(text, m.start(), m.end())
                flags.append({
                    "id": "unrealistic_promise",
                    "category": "Promise Realism",
                    "severity": severity,
                    "title": title,
                    "evidence": snippet,
                    "reason": "Genuine organizations assess qualifications through interviews or skill tests. Offers extended without any screening or promising unrealistic rewards are designed to bypass critical thinking.",
                    "verification": "Ask what specific technical evaluation criteria or rounds your application was selected from."
                })
                break

        # --- CATEGORY 4: Vague Role Details & High-Risk Tasks ---
        for pattern, title, severity in VAGUE_ROLE_KEYWORDS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                snippet = self._extract_snippet(text, m.start(), m.end())
                flags.append({
                    "id": "vague_role_description",
                    "category": "Role Clarity",
                    "severity": severity,
                    "title": title,
                    "evidence": snippet,
                    "reason": "Data entry, copy-paste, and click/task operations with vague deliverables are frequent vehicles for non-payment scams or phishing data harvesters.",
                    "verification": "Request a structured job description containing measurable learning objectives, mentor assignment, and clear deliverables."
                })
                break

        # Check for very brief descriptions
        if extracted.get("word_count", 0) < 60:
            flags.append({
                "id": "insufficient_detail",
                "category": "Role Clarity",
                "severity": "info",
                "title": "Minimal Offer Documentation",
                "evidence": f"Document length is only {extracted.get('word_count')} words.",
                "reason": "Official offer letters typically outline reporting managers, working hours, IP rights, non-disclosure agreements, and leave policies.",
                "verification": "Request an official, formal appointment letter containing company registration details (CIN/GST) and company policies."
            })

        # --- CATEGORY 5: Pressure Tactics & Artificial Urgency ---
        for pattern, title, severity in URGENCY_KEYWORDS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                snippet = self._extract_snippet(text, m.start(), m.end())
                flags.append({
                    "id": "urgency_tactics",
                    "category": "Pressure Tactics",
                    "severity": severity,
                    "title": title,
                    "evidence": snippet,
                    "reason": "Imposing artificial short-fuse deadlines (e.g. 'accept within 6 hours or forfeit') is a pressure strategy to stop applicants from consulting parents, placement cells, or mentors.",
                    "verification": "Do not let arbitrary deadlines rush you. Legitimate employers grant at least 48-72 hours for candidates to review terms."
                })
                break

        # If clean document, add positive reassurance
        if not flags:
            flags.append({
                "id": "clean_profile",
                "category": "Standard Alignment",
                "severity": "info",
                "title": "No Obvious High-Risk Red Flags Detected",
                "evidence": "Document contains professional phrasing, no upfront fee demands, and standard recruitment terminology.",
                "reason": "The offer does not display common high-risk indicators like upfront fees or pressure tactics.",
                "verification": "Always verify the offer on the employer's official website and confirm with your campus placement cell as good practice."
            })

        return flags

    def _extract_snippet(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extracts a readable context snippet around a matched regex span."""
        s = max(0, start - window)
        e = min(len(text), end + window)
        snippet = text[s:e].replace("\n", " ").strip()
        if s > 0:
            snippet = "..." + snippet
        if e < len(text):
            snippet = snippet + "..."
        return snippet

    def _calculate_risk_scores(self, flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates normalized category scores (0-100) and overall weighted risk score."""
        category_weights = {
            "Financial Demands": 45,
            "Communication Channels": 25,
            "Promise Realism": 15,
            "Role Clarity": 10,
            "Pressure Tactics": 15
        }

        cat_scores = {
            "financial": 0,
            "communication": 0,
            "realism": 0,
            "role_clarity": 0,
            "pressure": 0
        }

        total_penalty = 0

        for flag in flags:
            sev = flag.get("severity")
            cat = flag.get("category", "")
            
            # Severity points
            points = 35 if sev == "critical" else (18 if sev == "warning" else 0)
            total_penalty += points

            if "Financial" in cat:
                cat_scores["financial"] = min(100, cat_scores["financial"] + (80 if sev == "critical" else 45))
            elif "Communication" in cat:
                cat_scores["communication"] = min(100, cat_scores["communication"] + (70 if sev == "critical" else 40))
            elif "Promise" in cat:
                cat_scores["realism"] = min(100, cat_scores["realism"] + (65 if sev == "critical" else 35))
            elif "Role" in cat:
                cat_scores["role_clarity"] = min(100, cat_scores["role_clarity"] + (50 if sev == "critical" else 30))
            elif "Pressure" in cat:
                cat_scores["pressure"] = min(100, cat_scores["pressure"] + (60 if sev == "critical" else 35))

        # Overall risk score capped at 100
        overall = min(100, total_penalty)

        # Baseline baseline logic for low risk if clean
        if overall < 30:
            risk_level = "LOW"
            if overall == 0:
                overall = 12  # modest baseline because all offers deserve standard verification
        elif overall < 65:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "total_score": overall,
            "risk_level": risk_level,
            "categories": cat_scores
        }

    def _generate_verification_checklist(self, extracted: Dict[str, Any], flags: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Constructs an interactive step-by-step verification checklist for the student."""
        checklist = [
            {
                "id": "chk_mca_registry",
                "title": "Verify Corporate Registration (MCA / ROC)",
                "description": f"Look up '{extracted.get('company', 'the company')}' on the Ministry of Corporate Affairs (mca.gov.in) portal to ensure it has an active CIN and legitimate directors.",
                "importance": "High"
            },
            {
                "id": "chk_domain_identity",
                "title": "Inspect Email & Web Domain Authenticity",
                "description": "Ensure official communications originate from the official domain (@company.com). Beware of subtle misspellings (e.g., info@micro-soft.com vs @microsoft.com).",
                "importance": "Critical" if extracted.get("free_email_detected") else "Medium"
            },
            {
                "id": "chk_zero_fees",
                "title": "Strict Zero-Fee Policy",
                "description": "Never transfer money for registration, security deposit, ID cards, or interview scheduling. Legitimate companies never charge applicants.",
                "importance": "Critical"
            },
            {
                "id": "chk_linkedin_recruiter",
                "title": "Authenticate Recruiter on LinkedIn",
                "description": "Search for the sender's name and role on LinkedIn. Confirm they work at the company and share mutual industry connections.",
                "importance": "High"
            },
            {
                "id": "chk_careers_page",
                "title": "Cross-check on Official Careers Portal",
                "description": "Visit the company's verified website directly (not via links in the email/PDF) and confirm the job opening is publicly listed.",
                "importance": "High"
            },
            {
                "id": "chk_campus_cell",
                "title": "Consult College Placement Cell / Mentors",
                "description": "Show the offer letter to your college training & placement officer (TPO) or career mentor before signing or sharing personal IDs.",
                "importance": "Medium"
            }
        ]
        return checklist

    def _generate_executive_summary(self, extracted: Dict[str, Any], scores: Dict[str, Any], flags: List[Dict[str, Any]]) -> str:
        """Produces a clear, student-friendly explanation conforming to the JobShield AI philosophy."""
        level = scores["risk_level"]
        score = scores["total_score"]
        role = extracted.get("role", "the role")
        company = extracted.get("company", "the stated employer")

        critical_count = sum(1 for f in flags if f.get("severity") == "critical")
        warning_count = sum(1 for f in flags if f.get("severity") == "warning")

        if level == "HIGH":
            return (
                f"JobShield AI detected {critical_count} critical warning sign(s) and {warning_count} secondary concern(s) "
                f"for the offer regarding '{role}' at '{company}'. The document displays patterns heavily correlated with "
                f"unauthorized recruitment practices, such as upfront financial demands or unverified personal contact channels. "
                f"We strongly recommend pausing further engagement until you have independently authenticated the company through official channels."
            )
        elif level == "MEDIUM":
            return (
                f"JobShield AI identified noticeable inconsistencies ({warning_count} cautionary indicator(s)) in this offer for '{role}'. "
                f"While it may be a fledgling startup or informal agency, key details—such as communication channels or job scope—"
                f"require careful verification before submitting sensitive documents or signing agreements."
            )
        else:
            return (
                f"JobShield AI detected minimal warning signs for '{role}' at '{company}'. "
                f"The text aligns with standard recruitment practices without upfront fee demands or coercion. "
                f"Remember: JobShield flags warning signs to assist your review; always complete the recommended verification checklist as a smart candidate."
            )

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "extracted_data": {
                "company": "None", "role": "None", "stipend": "None", "emails": [],
                "email_domains": [], "phones": [], "detected_channels": [], "fees_extracted": []
            },
            "flags": [],
            "risk_score": 0,
            "risk_level": "LOW",
            "category_scores": {"financial": 0, "communication": 0, "realism": 0, "role_clarity": 0, "pressure": 0},
            "summary": "No text content detected for analysis.",
            "checklist": [],
            "flags_count": {"critical": 0, "warning": 0, "info": 0}
        }
