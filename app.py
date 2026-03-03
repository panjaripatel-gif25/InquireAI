import os
os.system('pip install pypdf2 google-generativeai streamlit')
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. SETUP THE BRAIN (Get your API key from Google AI Studio)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# FIND THE WORKING MODEL AUTOMATICALLY
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
model_to_use = available_models[0] if available_models else 'models/gemini-1.5-flash'

st.write(f"Using model: {model_to_use}") # This helps us see if it's working
model = genai.GenerativeModel(model_to_use)

st.title("InquireAI")
st.subheader("Turn your profile into a 1% success-rate email")

# 2. THE INPUTS (The "Face" of your app)
col1, col2 = st.columns(2)
with col1:
    student_name = st.text_input("Your Full Name")
    college = st.text_input("Your College (e.g., IIT Delhi)")
    year = st.selectbox("Current Year", ["Freshman", "Sophomore", "Junior Undergraduate", "Senior Undergraduate", "Master's"])
    dept = st.text_input("Department")

with col2:
    prof_name = st.text_input("Professor's Name")
    resume_link = st.text_input("Hyperlink to your Resume (Drive/Dropbox)")
    uploaded_file = st.file_uploader("Upload Resume (PDF) to help AI learn about you")

interests = st.text_area("What are your research interests? (Short sentences)")
prof_text = st.text_area("Paste the Professor's 'Research/Recent Papers' text here (Copy-paste from their site)")

# 3. THE LOGIC
if st.button("Generate My Cold Email"):
    with st.spinner("Analyzing papers and crafting your connection..."):
        
        # Read the PDF if uploaded
        resume_context = ""
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            resume_context = " ".join([page.extract_text() for page in reader.pages])

        # THE UPGRADED "SMART" PROMPT
        prompt = f"""
        You are an elite Academic Career Coach. Your goal is to write a short, punchy, and professional cold email.
        
        DATA PROVIDED:
        - Student Interests: {interests}
        - Professor's Raw Text: {prof_text}
        - Student Resume Context: {resume_context[:1000]}

        INSTRUCTIONS FOR THE CONNECTION PARAGRAPH (5 lines max):
        1. Start with ONE clear line stating the student's research interest.
        2. Scan the 'Professor's Raw Text' and identify the TOP 3 most important recent papers or projects.
        3. Ignore the niche technical jargon (e.g., specific chemical formulas or low-level coding libraries).
        4. Write 4 lines explaining how these specific works inspire the student. 
        5. Focus on the "Why" and the "Impact" (e.g., "Your work on sustainable AI efficiency" instead of "Your paper on 4-bit quantization in Transformer-based architectures").
        6. Use a sophisticated yet "human" tone—not robotic.

        TEMPLATE TO FOLLOW EXACTLY:
        Dear Professor {prof_name},

        My name is {student_name}, and I am a {year} in {dept} at {college}. I am writing to request a Research Opportunity for the Summer of 2027.

        [Insert the Smart 5-line paragraph here]

        My resume ({resume_link}) is attached for your review. I would be privileged to discuss how my specific skills could directly contribute to your ongoing projects in Summer 2027.

        Thank you for your time and consideration.
        """

        response = model.generate_content(prompt)
        
        st.success("Done! Copy the email below:")
        st.text_area("Your Final Email", value=response.text, height=400)