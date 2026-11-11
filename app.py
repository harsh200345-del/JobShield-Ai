"""
JobShield AI - Main Flask Web Application
Hackathon Project: AI Fake Internship & Job Detector
Team HackNova: Harsh Pandey, Shivam Yadav, Mahi Garg, Priyanshi Bansal
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from config import Config
from database import (
    init_db, save_scan, get_scan, get_recent_scans,
    get_analytics_summary, save_feedback
)
from document_extractor import extract_text_from_pdf, extract_text_from_txt, clean_extracted_text
from analysis_engine import JobShieldAnalyzer
from samples import SAMPLE_OFFERS

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize Database
init_db()

# Initialize NLP & Rule Engine Analyzer
analyzer = JobShieldAnalyzer(
    gemini_api_key=app.config.get("GEMINI_API_KEY"),
    openai_api_key=app.config.get("OPENAI_API_KEY")
)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Main Scanner Page with Paste Text, PDF Upload, and One-Click Sample Presets."""
    analytics = get_analytics_summary()
    return render_template("index.html", samples=SAMPLE_OFFERS, stats=analytics)


@app.route("/analyze", methods=["POST"])
def analyze_offer():
    """Receives submitted job text or uploaded PDF, runs analysis, and saves report."""
    input_type = request.form.get("input_type", "text")
    doc_name = "Pasted Job Description"
    extracted_text = ""
    metadata = {}

    if input_type == "file":
        if "document_file" not in request.files:
            flash("No file was uploaded.", "danger")
            return redirect(url_for("index"))
        
        file = request.files["document_file"]
        if file.filename == "":
            flash("Please select a valid file to analyze.", "warning")
            return redirect(url_for("index"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            doc_name = filename
            saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(saved_path)

            ext = filename.rsplit(".", 1)[1].lower()
            try:
                if ext == "pdf":
                    extracted_text, metadata = extract_text_from_pdf(saved_path)
                else:
                    extracted_text, metadata = extract_text_from_txt(saved_path)
            except Exception as e:
                flash(f"Error reading document: {str(e)}", "danger")
                return redirect(url_for("index"))
            finally:
                # Clean up uploaded file immediately per privacy policy:
                # "MVP privacy principle: process documents for analysis and avoid retaining personal data"
                if os.path.exists(saved_path):
                    try:
                        os.remove(saved_path)
                    except Exception:
                        pass
        else:
            flash("Supported file formats are PDF and TXT only.", "warning")
            return redirect(url_for("index"))

    else:
        # Text input
        extracted_text = request.form.get("job_text", "").strip()
        custom_title = request.form.get("job_title_input", "").strip()
        if custom_title:
            doc_name = custom_title
        else:
            doc_name = "Pasted Job / Offer Notice"

    if not extracted_text or len(extracted_text) < 20:
        flash("The document content is too brief to analyze. Please provide a more complete job post or offer letter.", "warning")
        return redirect(url_for("index"))

    # Perform analysis
    analysis_result = analyzer.analyze(extracted_text, metadata)

    # Save to SQLite database
    scan_id = save_scan(
        document_name=doc_name,
        input_type=input_type,
        analysis=analysis_result
    )

    return redirect(url_for("view_report", scan_id=scan_id))


@app.route("/report/<int:scan_id>")
def view_report(scan_id: int):
    """Renders the comprehensive risk assessment report for a scan."""
    scan = get_scan(scan_id)
    if not scan:
        flash("The requested assessment report was not found.", "warning")
        return redirect(url_for("index"))

    return render_template("results.html", scan=scan, analysis=scan["analysis"])


@app.route("/history")
def history():
    """Placement cell / applicant report archive and aggregate trends."""
    scans = get_recent_scans(limit=50)
    stats = get_analytics_summary()
    return render_template("history.html", scans=scans, stats=stats)


@app.route("/guide")
def guide():
    """Student Safety Guide & Red Flag Education."""
    return render_template("guide.html")


@app.route("/about")
def about():
    """About JobShield AI, Team HackNova, Mission and Architecture."""
    return render_template("about.html")


@app.route("/api/sample/<sample_key>")
def get_sample(sample_key: str):
    """Returns sample text via JSON for instant form pre-fill."""
    sample = SAMPLE_OFFERS.get(sample_key)
    if sample:
        return jsonify({"status": "success", "title": sample["title"], "text": sample["text"]})
    return jsonify({"status": "error", "message": "Sample not found"}), 404


@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Collects student feedback on risk assessment accuracy."""
    data = request.get_json() or {}
    scan_id = data.get("scan_id")
    rating = data.get("rating", 5)
    comments = data.get("comments", "")

    if scan_id:
        save_feedback(scan_id, rating, comments)
        return jsonify({"status": "success", "message": "Feedback submitted successfully."})
    return jsonify({"status": "error", "message": "Invalid scan ID."}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
