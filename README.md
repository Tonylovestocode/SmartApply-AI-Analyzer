# SmartApply-AI-Analyzer

SmartApply - AI Resume Analyzer
A full-stack web application designed to help job seekers optimize their resumes. SmartApply performs a skill-gap analysis by comparing a user's resume against a job description, calculates a match score, and leverages Google's Gemini AI to generate tailored bullet points for missing skills.

Live Demo: [Link to your live Render application]

Features
Resume Parsing: Extracts text directly from uploaded PDF resumes.

Skill Gap Analysis: Identifies skills present in the job description but missing from the resume using NLP.

Match Score Calculation: Provides a percentage score based on how well the resume's skills match the job's requirements.

AI-Powered Suggestions: Integrates with the Google Gemini API to generate professional, context-aware resume bullet points for missing skills.

Responsive UI: A clean, modern, and mobile-friendly interface built with Tailwind CSS.

Technologies Used
Backend: Python, Flask

Frontend: HTML, Tailwind CSS, JavaScript

NLP: spaCy, rapidfuzz

AI Integration: Google Gemini API, Python requests library

Deployment: Render (Backend), Vercel (Frontend - if separated)

How To Run Locally
Prerequisites
Python 3.x

Git

Setup
Clone the repository:

git clone https://github.com/YOUR_USERNAME/SmartApply-AI-Analyzer.git
cd SmartApply-AI-Analyzer

Create and activate a virtual environment:

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install the required dependencies:

pip install -r requirements.txt

Download the spaCy language model:

python -m spacy download en_core_web_sm

Run the Flask application:

python app.py

The application will be available at http://127.0.0.1:5000.
