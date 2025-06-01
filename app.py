import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import PyPDF2
import docx

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages])

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

st.sidebar.header("📄 Upload Your Resume")
resume_file = st.sidebar.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
resume_text = ""
if resume_file:
    resume_text = extract_text_from_pdf(resume_file) if resume_file.type == "application/pdf" else extract_text_from_docx(resume_file)

st.title("💼 Resume Review Q&A Agent")
st.markdown("Paste the **Job Description** below and click Send:")

job_desc_input = st.text_area("Job Description", height=200)
send_clicked = st.button("Send")

if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "initial_review_done" not in st.session_state:
    st.session_state.initial_review_done = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store job description when sent
if send_clicked and job_desc_input:
    st.session_state.job_description = job_desc_input
    st.session_state.initial_review_done = False

# Run initial Gemini review
if resume_text and st.session_state.job_description and not st.session_state.initial_review_done:
    prompt = f"""You are an expert AI assistant that reviews resumes based on job descriptions.

Analyze the given resume and job description. Provide insights in a short, clear, and friendly tone.

Focus on:
- Compatibility: Is the resume a good fit? Briefly explain.
- Improvements: What specific updates or additions are needed?
- Missing Keywords: Important terms from the job description not found in the resume.
- Missing Skills: Key skills the resume lacks and how to incorporate them.
- Resume Edits: Suggest sentence-level rewrites for clarity or relevance.

Keep the response brief, use bullet points, and make it engaging with emojis. Avoid long paragraphs.
Resume:
{resume_text}

Job Description:
{st.session_state.job_description}
"""
    response = model.generate_content(prompt).text
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.initial_review_done = True

# Show conversation
if st.session_state.initial_review_done:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ask follow-up questions here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        followup_prompt = f"""Resume:
{resume_text}

Job Description:
{st.session_state.job_description}

User Question:
{user_input}

Respond in a human-like tone with bullet points and emojis."""
        reply = model.generate_content(followup_prompt).text
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
