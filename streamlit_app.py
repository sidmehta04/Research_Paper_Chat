import streamlit as st
import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from researchpaper import download_papers

# Load environment variables
load_dotenv()

# CSS for styling the Streamlit app
def inject_custom_css():
    st.markdown("""
    <style>
    /* Custom background gradient */
    body {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
    }

    /* Title and headers styling */
    .stApp header {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #0056b3;
    }

    /* Input fields */
    .stNumberInput, .stTextInput {
        border-radius: 5px;
        padding: 5px;
        font-size: 14px;
        margin-bottom: 15px;
    }

    /* File selectors and dropdowns */
    .stSelectbox {
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
    }

    /* Spinner */
    .stSpinner {
        color: #007bff;
    }

    /* General text styling */
    p, .stMarkdown {
        font-family: 'Roboto', sans-serif;
        line-height: 1.6;
    }

    /* Section headers */
    .stMarkdown h2 {
        color: #0056b3;
        margin-top: 20px;
    }

    /* Add subtle box shadows */
    .stApp .stAlert, .stApp .stMarkdown {
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
        padding: 10px;
        border-radius: 5px;
    }

    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

def initialize_model():
    return genai.GenerativeModel('gemini-1.5-pro')

def get_safe_config():
    return [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

def generate_summary(model, text):
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

def main():
    inject_custom_css()  # Inject custom CSS
    st.title("Research Paper Downloader, Summarizer, and Chat")
    
    # Paper Downloading Section
    st.header("Download Papers")
    target_date = st.date_input("Select date for paper download", datetime.now())
    paper_limit = st.number_input("Number of papers to download (0 for all available)", min_value=0, value=5, step=1)
    
    if st.button("Download Papers"):
        with st.spinner('Downloading papers...'):
            download_dir = download_papers(target_date.strftime("%Y-%m-%d"), paper_limit=(None if paper_limit == 0 else paper_limit))
        st.success(f"Papers downloaded to {download_dir}")

    st.header("PDF Summarizer and Interactive Chat")
    st.write("Choose a downloaded PDF file to get a detailed summary and chat about its content using Gemini 1.5 Pro.")
    st.warning("Note: This version uses unfiltered AI responses. Use responsibly.")

    if 'model' not in st.session_state:
        st.session_state.model = initialize_model()
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = None
    if 'summary' not in st.session_state:
        st.session_state.summary = None

    # File Selection
    pdf_dirs = [d for d in os.listdir('downloaded_papers') if os.path.isdir(os.path.join('downloaded_papers', d))]
    selected_dir = st.selectbox("Choose a date", pdf_dirs, index=len(pdf_dirs)-1 if pdf_dirs else 0)
    
    if selected_dir:
        pdf_files = [f for f in os.listdir(os.path.join('downloaded_papers', selected_dir)) if f.endswith('.pdf')]
        selected_file = st.selectbox("Choose a PDF file", pdf_files)

        if selected_file:
            pdf_path = os.path.join('downloaded_papers', selected_dir, selected_file)
            st.write(f"Processing: {selected_file}")
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_path)

            if extracted_text:
                st.session_state.pdf_content = extracted_text
                with st.spinner('Generating detailed summary...'):
                    st.session_state.summary = generate_summary(st.session_state.model, extracted_text)
                st.success("PDF processed and summary generated successfully.")
            else:
                st.error(f"Could not extract text from {selected_file}")

    if st.session_state.summary:
        st.subheader("Detailed Summary")
        st.write(st.session_state.summary)

        st.subheader("Ask Questions")
        user_input = st.text_input("Ask a question about the paper:")
        if user_input:
            with st.spinner('Generating response...'):
                prompt = f"""Based on the following paper summary and the original content, please answer this question: {user_input}

                Summary: {st.session_state.summary}

                Original Content: {st.session_state.pdf_content[:30000]}

                Answer:"""
                response = st.session_state.model.generate_content(prompt, safety_settings=get_safe_config())
            
            st.write("Answer:")
            st.write(response.text)

    st.write("Note: This app uses Gemini 1.5 Pro for summarization and chat interactions without content filtering. Ensure you have proper API access and credentials set up.")

if __name__ == "__main__":
    # Set up Gemini API using the key from .env file
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file. Please set up your API key.")
    else:
        genai.configure(api_key=api_key)
        main()
