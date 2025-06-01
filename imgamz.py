import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import PyPDF2
import docx
from PIL import Image
import pytesseract

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

def translate_text(text, target_lang="en"):
    prompt = f"Translate this text to {target_lang}:\n{text}"
    return model.generate_content(prompt).text

# Sidebar – Resume Upload
st.sidebar.header("📄 Upload Your Resume")
resume_file = st.sidebar.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
resume_text = ""
if resume_file:
    resume_text = extract_text_from_pdf(resume_file) if resume_file.type == "application/pdf" else extract_text_from_docx(resume_file)

# Main Tabs
tab1, tab2, tab3 = st.tabs(["💼 Resume Agent", "🖼️ Image Translator", "🎤 Speaker Info"])

# ==================== Tab 1: Resume Q&A Agent ====================
with tab1:
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

    if send_clicked and job_desc_input:
        st.session_state.job_description = job_desc_input
        st.session_state.initial_review_done = False

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

# ==================== Tab 2: Image Translator ====================
from PIL import Image

with tab2:
    st.header("🖼️ Universal Image Translator")
    st.markdown("""
    Upload any image — be it a **document, plot, graph, chart, natural scene, UI screen, infographic, or handwritten note**.  
    This tool will **describe and translate** its contents both in **English and Hindi**. 📄➡️🌐  
    """)

    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "bmp", "webp"])

    if uploaded_image:
        # Load image using PIL
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Prompt for Gemini
        prompt = """
        You are an intelligent image understanding agent. The image uploaded by the user could be anything — a photo, chart, diagram, screenshot, or scanned text.
        Your job is to:
        1. First, analyze and describe what's inside the image in **English**.
        2. Then, translate the same description into **Hindi**.

        Make sure your response includes:
        - A clear breakdown of what’s visible in the image
        - Label graphs or diagrams if they are detected
        - Capture any text or scene elements accurately

        Format your response like this:

        **English Description**:
        - ...
        - ...

        **Hindi Translation**:
        - ...
        - ...
        """

        # Use Gemini Vision API with the PIL image
        multimodal_model = genai.GenerativeModel("gemini-1.5-flash")
        response = multimodal_model.generate_content([prompt, image])  # <== pass `image` not `image_bytes`
        output = response.text

        st.markdown("### 🔍 AI Transcription & Translation")
        st.markdown(output)


# ==================== Tab 3: Speaker Info ====================
with tab3:
    st.header("🎤 Speaker Info")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("D:\GIGA\First AI Agent\Shreya Dhurde pink Square.jpeg", caption="Speaker Photo")  # Replace with real photo or uploader
    with col2:
        st.markdown("""
        **Name**: Shreya Dhurde  
        **Role**: AI Engineer
        **Location**: Pune, India  
        **Specialties**: Generative AI,AI Agents, LLM Apps  
        **Talks Given**: 5+ Research & Dev Talks  
         
        """)

        st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/shreya-dhurde/)")  # Replace with real link