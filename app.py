import os
import fitz  # PyMuPDF
import spacy
import json
import requests
from flask import Flask, request, render_template, jsonify
from rapidfuzz import fuzz

# --- Basic Flask App Setup ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Load NLP Model ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Spacy model 'en_core_web_sm' not found.")
    print("Please run: python -m spacy download en_core_web_sm")
    nlp = None 

# --- Skill Analysis Logic (No changes) ---
SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'c#', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
    'nodejs', 'flask', 'django', 'ruby', 'php', 'swift', 'kotlin', 'sql', 'mysql', 'postgresql',
    'mongodb', 'firebase', 'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'git',
    'jenkins', 'ci/cd', 'linux', 'unix', 'windows', 'macos', 'bash', 'powershell',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
    'numpy', 'data analysis', 'data visualization', 'tableau', 'power bi', 'agile', 'scrum',
    'project management', 'product management', 'ui/ux', 'figma', 'sketch', 'adobe xd',
    'photoshop', 'illustrator', 'communication', 'teamwork', 'leadership', 'problem-solving',
    'customer service', 'technical support', 'troubleshooting', 'time management', 'negotiation'
]

def extract_text_from_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        text = "".join([page.get_text() for page in doc])
        return text
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
        return ""

def extract_skills_from_job_description(text):
    if not nlp: return []
    doc = nlp(text.lower())
    found_skills = set()
    for chunk in doc.noun_chunks:
        if chunk.text in SKILL_KEYWORDS or chunk.root.text in SKILL_KEYWORDS:
            found_skills.add(chunk.text.strip())
    for token in doc:
        if not token.is_stop and not token.is_punct and token.lemma_ in SKILL_KEYWORDS:
            found_skills.add(token.lemma_)
    return list(found_skills)

def analyze_resume_against_skills(resume_text, job_skills):
    resume_text_lower = resume_text.lower()
    matched_skills, missing_skills = [], []
    for skill in job_skills:
        if fuzz.partial_ratio(skill, resume_text_lower) > 85:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    return list(set(matched_skills)), list(set(missing_skills))

def calculate_match_score(matched_skills, job_skills):
    if not job_skills: return 0
    return round((len(matched_skills) / len(job_skills)) * 100)

# --- Main Flask Route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    analysis_results = None
    if request.method == 'POST' and nlp:
        resume_file = request.files.get('resume')
        job_desc_text = request.form.get('jobdesc')
        job_title = request.form.get('job_title', 'the position') 

        if resume_file and resume_file.filename and job_desc_text:
            filepath = os.path.join(UPLOAD_FOLDER, resume_file.filename)
            resume_file.save(filepath)
            resume_text = extract_text_from_pdf(filepath)
            
            if resume_text:
                job_skills = extract_skills_from_job_description(job_desc_text)
                matched_skills, missing_skills = analyze_resume_against_skills(resume_text, job_skills)
                match_score = calculate_match_score(matched_skills, job_skills)
                
                analysis_results = {
                    "matched_skills": sorted(matched_skills),
                    "missing_skills": sorted(missing_skills),
                    "match_score": match_score,
                    "job_title": job_title,
                }
            os.remove(filepath)
    return render_template('index.html', results=analysis_results)


# --- AI Suggestion Route with Local Simulation ---
@app.route('/generate-suggestion', methods=['POST'])
def generate_suggestion():
    try:
        data = request.get_json()
        skill = data.get('skill')
        job_title = data.get('job_title')

        if not skill or not job_title:
            return jsonify({'error': 'Missing skill or job title'}), 400

        api_key = '' # This remains empty for local testing.
        
        # --- SIMULATION LOGIC ---
        if not api_key:
            print("--- RUNNING IN LOCAL SIMULATION MODE (NO API KEY) ---")
            simulated_text = f"Spearheaded a project utilizing {skill.title()} to streamline backend processes for the {job_title} role, improving system efficiency by 15%."
            return jsonify({'suggestion': simulated_text})
        
        # --- REAL API CALL LOGIC (for deployment) ---
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
        prompt = f"You are a professional career coach. Write a single, powerful, results-oriented resume bullet point for a '{job_title}' role that highlights the skill '{skill}'. The bullet point should start with an action verb and be concise."
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        result = response.json()
        suggestion_text = result['candidates'][0]['content']['parts'][0].get('text', 'Could not parse suggestion.')
        return jsonify({'suggestion': suggestion_text.strip()})

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return jsonify({'error': f'API Request Error: {e}'}), 500
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({'error': f'An internal server error occurred: {e}'}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
