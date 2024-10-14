from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from researchpaper import download_papers
from PyPDF2 import PdfReader

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Set up Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-pro')

def get_safe_config():
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        return "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

def generate_summary(text):
    prompt = """Generate a detailed summary of the following research paper. 
    Structure the summary as follows:
    1. Title and Authors
    2. Abstract (brief overview)
    3. Introduction and Background
    4. Methodology
    5. Key Findings and Results
    6. Discussion
    7. Conclusion
    8. Implications and Future Work

    Ensure each section is comprehensive yet concise. Highlight any significant contributions or novelties presented in the paper.

    Paper text:
    {text}

    Detailed Summary:"""

    response = model.generate_content(prompt.format(text=text[:30000]), safety_settings=get_safe_config())
    return response.text

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/download_papers', methods=['POST'])
def download_papers_route():
    data = request.json
    target_date = data['date']
    paper_limit = data['paperLimit']
    
    download_dir = download_papers(target_date, paper_limit=(None if paper_limit == 0 else paper_limit))
    return jsonify({'status': 'success', 'downloadDir': download_dir})

@app.route('/get_pdf_dirs', methods=['GET'])
def get_pdf_dirs():
    pdf_dirs = [d for d in os.listdir('downloaded_papers') if os.path.isdir(os.path.join('downloaded_papers', d))]
    return jsonify(pdf_dirs)

@app.route('/get_pdf_files', methods=['POST'])
def get_pdf_files():
    data = request.json
    selected_dir = data['selectedDir']
    pdf_files = [f for f in os.listdir(os.path.join('downloaded_papers', selected_dir)) if f.endswith('.pdf')]
    return jsonify(pdf_files)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    data = request.json
    selected_dir = data['selectedDir']
    selected_file = data['selectedFile']
    
    pdf_path = os.path.join('downloaded_papers', selected_dir, selected_file)
    extracted_text = extract_text_from_pdf(pdf_path)
    
    if extracted_text:
        summary = generate_summary(extracted_text)
        return jsonify({'status': 'success', 'summary': summary, 'content': extracted_text[:30000]})
    else:
        return jsonify({'status': 'error', 'message': f"Could not extract text from {selected_file}"})

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    user_input = data['question']
    summary = data['summary']
    content = data['content']
    
    prompt = f"""Based on the following paper summary and the original content, please answer this question: {user_input}

    Summary: {summary}

    Original Content: {content}

    Answer:"""
    
    response = model.generate_content(prompt, safety_settings=get_safe_config())
    return jsonify({'answer': response.text})

if __name__ == '__main__':
    app.run(debug=True)