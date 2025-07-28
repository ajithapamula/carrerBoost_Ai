import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import spacy
from sentence_transformers import SentenceTransformer, util
import pdfkit
from io import BytesIO
import PyPDF2
import docx

app = Flask(__name__)
app.secret_key = "careerboost-secret"
os.makedirs("uploads", exist_ok=True)

# Load NLP models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

# wkhtmltopdf configuration - update path here if needed for Windows
PDFKIT_CONFIG = pdfkit.configuration()  # If error occurs, specify absolute path to wkhtmltopdf executable
PDFKIT_OPTIONS = {"enable-local-file-access": None}

TEMPLATES = {
    "simple": "preview_simple.html",
    "modern": "preview_modern.html"
}

SECTION_NAMES = {
    "contact": ["contact", "contact information", "phone", "email"],
    "summary": ["summary", "objective", "profile"],
    "skills": ["skills", "technical skills"],
    "experience": ["experience", "work experience", "employment"],
    "education": ["education", "academic"],
    "projects": ["projects", "research"],
    "certifications": ["certifications", "licenses"],
    "additional": ["additional", "languages", "awards"]
}

DEFAULT_SKILLS = [
    "python", "sql", "machine learning", "deep learning", "data analysis",
    "project management", "cloud computing", "nlp", "docker", "git",
    "tensorflow", "keras", "aws", "azure", "react", "node.js", "excel"
]

TEMPLATES_CONTENT = {
    "summary": "Results-driven professional with expertise in {skills}. Passionate about data and technology to solve real-world problems.",
    "skills": ", ".join(DEFAULT_SKILLS[:8]),
    "experience": "Job Title | Company | 2020 - Present\n- Describe your accomplishment with quantifiable metric.",
    "education": "Degree | University | Year\n- Include honors, activities.",
    "projects": "Project Title | Year\n- Brief description with technologies and impact.",
    "certifications": "Certification Name | Authority | Year",
    "additional": "Languages: English (Fluent), Hindi (Native)\nAwards: Achieved Best Student Award"
}

def extract_text(file_path, ext):
    if ext == ".pdf":
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        text += txt + '\n'
        except Exception:
            return ""
        return text
    elif ext == ".docx":
        try:
            doc = docx.Document(file_path)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
            return "\n".join(fullText)
        except Exception:
            return ""
    else:  # Plain text or fallback
        try:
            with open(file_path, "r", encoding="utf8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

def parse_sections(text):
    """
    Parse the resume text into sections by simple regex detection based on known headers.
    """
    sections = {key: "" for key in SECTION_NAMES}
    lower_text = text.lower()

    indices = []
    for key, keywords in SECTION_NAMES.items():
        for kw in keywords:
            pattern = rf'(^|\n){re.escape(kw)}[\n:\-]'
            match = re.search(pattern, lower_text, re.I | re.M)
            if match:
                indices.append((match.start(), key))
                break
    indices = sorted(indices)

    if not indices:
        # fallback - just 'summary'
        sections["summary"] = text.strip()
        return sections

    for i, (start_idx, key) in enumerate(indices):
        end_idx = indices[i + 1][0] if i + 1 < len(indices) else len(text)
        val = text[start_idx:end_idx].strip()
        # Strip the header line and colon sign to keep clean content
        val = re.sub(r'^[^\n]*\n', '', val)
        val = val.strip(": \n\r\t")
        sections[key] = val

    return sections

def extract_skills(text):
    found = set()
    ltext = text.lower()
    for skill in DEFAULT_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', ltext):
            found.add(skill)
    return sorted(found)

def fill_missing_sections(sections, job_description):
    job_skills = extract_skills(job_description)
    # Fill missing sections with default templates or generated content

    if not sections.get("summary"):
        top_skills = ", ".join(job_skills[:5]) if job_skills else "your field"
        sections["summary"] = TEMPLATES_CONTENT["summary"].format(skills=top_skills)

    if not sections.get("skills"):
        sections["skills"] = TEMPLATES_CONTENT["skills"]

    if not sections.get("experience"):
        sections["experience"] = TEMPLATES_CONTENT["experience"]

    if not sections.get("education"):
        sections["education"] = TEMPLATES_CONTENT["education"]

    if not sections.get("projects"):
        sections["projects"] = TEMPLATES_CONTENT["projects"]

    if not sections.get("certifications"):
        sections["certifications"] = TEMPLATES_CONTENT["certifications"]

    if not sections.get("additional"):
        sections["additional"] = TEMPLATES_CONTENT["additional"]

    return sections, job_skills

def render_template_string(tmpl_str, **kwargs):
    tmpl = Template(tmpl_str)
    return tmpl.render(**kwargs)

def calculate_ats_score(resume_text, job_description):
    if not resume_text or not job_description:
        return None
    emb_res = model.encode([resume_text], convert_to_tensor=True)
    emb_job = model.encode([job_description], convert_to_tensor=True)
    score = util.cos_sim(emb_res, emb_job).item()
    return round(score * 100, 1)

def generate_html_resume(template_name, sections, job_skills=None):
    """Generate the resume in selected template"""
    template_file = TEMPLATES.get(template_name, "preview_simple.html")
    return render_template(template_file, **sections, job_skills=job_skills or [])

def convert_html_to_pdf(html):
    pdf = pdfkit.from_string(html, False, options=PDFKIT_OPTIONS, configuration=PDFKIT_CONFIG)
    return pdf

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("resume_file")
        job_description = request.form.get("job_description","").strip()
        selected_template = request.form.get("template_choice","simple")

        if not file or file.filename == "":
            return render_template("index.html", error="Please upload a resume.", templates=TEMPLATES)
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        filepath = os.path.join("uploads", filename)
        file.save(filepath)

        resume_text = extract_text(filepath, file_ext)
        if not resume_text.strip():
            return render_template("index.html", error="Cannot extract text from resume.", templates=TEMPLATES)

        sections = parse_sections(resume_text)
        sections, job_skills = fill_missing_sections(sections, job_description)

        # Store in session for next
        session["sections"] = sections
        session["job_description"] = job_description
        session["template"] = selected_template
        session["resume_text"] = resume_text
        session["job_skills"] = job_skills

        return redirect(url_for("edit_form"))

    return render_template("index.html", error=None, templates=TEMPLATES)

@app.route("/edit", methods=["GET", "POST"])
def edit_form():
    if "sections" not in session:
        return redirect(url_for("index"))
    sections = session["sections"]
    job_desc = session.get("job_description", "")
    job_skills = session.get("job_skills", [])
    template = session.get("template", "simple")

    if request.method == "POST":
        for key in sections.keys():
            form_val = request.form.get(key)
            if form_val is not None:
                sections[key] = form_val
        # Update template selection
        selected_template = request.form.get("template_choice", template)
        session["template"] = selected_template
        session["sections"] = sections
        return redirect(url_for("preview"))

    return render_template("edit_form.html", sections=sections,
                           job_keywords=", ".join(job_skills),
                           template_choice=template,
                           templates=TEMPLATES)

@app.route("/preview", methods=["GET", "POST"])
def preview():
    if "sections" not in session:
        return redirect(url_for("index"))
    sections = session["sections"]
    job_desc = session.get("job_description","")
    template = session.get("template","simple")
    job_skills = session.get("job_skills", [])

    if request.method == "POST":
        export_type = request.form.get("export_type","pdf")
        html = generate_html_resume(template, sections, job_skills)
        if export_type == "pdf":
            pdf = convert_html_to_pdf(html)
            return send_file(BytesIO(pdf), as_attachment=True, download_name="resume.pdf", mimetype="application/pdf")
        elif export_type == "html":
            return html

    ats_score = None
    if job_desc:
        combined = " ".join(sections.values())
        ats_score = calculate_ats_score(combined, job_desc)

    return render_template(TEMPLATES.get(template, "preview_simple.html"),
                           **sections,
                           job_skills=job_skills,
                           is_preview=True,
                           ats_score=ats_score)

@app.route("/download/<path:filename>")
def download_file(filename):
    path = os.path.join("uploads", filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "File not found", 404

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == '__main__':
    app.run(debug=True)
