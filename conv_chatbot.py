import os
from datetime import datetime
import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import csv

# ------------------ Page Setup ------------------
st.set_page_config(page_title="Artificial Intelligence & Machine Learning ", layout="wide")
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# ------------------ Load PDF ------------------
pdf_path = "AI_ML.pdf"  
if not os.path.exists(pdf_path):
    st.error(f"PDF not found at {pdf_path}")
    st.stop()

pdf_reader = PdfReader(pdf_path)
pdf_text = ""
for page in pdf_reader.pages:
    pdf_text += page.extract_text()

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Sidebar Settings ------------------
st.sidebar.title("⚙️ Response Settings")
tone = st.sidebar.radio("Select Answer Tone", ["Formal", "Friendly"])

st.sidebar.markdown("---") 

# ------------------ Feedback Box (Moved Lower) ------------------
st.sidebar.title("📝 Feedback")
feedback = st.sidebar.text_area("Your Feedback")
if st.sidebar.button("Save Feedback"):
    if feedback.strip():
        feedback_file = "feedback.csv"
        file_exists = os.path.exists(feedback_file)
        with open(feedback_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Feedback"])
            writer.writerow([datetime.now().isoformat(), feedback])
        st.sidebar.success("✅ Feedback saved!")
        feedback = ""
        st.rerun()
    else:
        st.sidebar.warning("⚠️ Please write feedback before saving.")


# ------------------ Main App ------------------
st.set_page_config(page_title="Artificial Intelligence & Machine Learning", layout="centered")
st.title("Artificial Intelligence & Machine Learning")
st.markdown("AI is a field of computer science that enables machines to mimic human intelligence—like reasoning, learning, and decision-making.")
st.markdown("---")

# Show Chat History
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(chat["bot"])

# Chat input
user_input = st.chat_input("Ask a question related to the AI...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    # Greeting recognition
    greetings = ["hello", "hi", "hey", "salam", "assalamualaikum"]
    if user_input.lower().strip() in greetings:
        bot_reply = "Hello! I'm here to help you. Ask me anything related to the material."
    else:
        with st.spinner("Generating answer..."):
            model = genai.GenerativeModel("gemini-1.5-flash-8b")

            # Tone-based prompt
            if tone == "Formal":
                style_prompt = "Answer in a formal, academic tone with clear and structured explanation."
            else:
                style_prompt = "Answer in a friendly and casual tone, like talking to a student."

            prompt = f"""
Use only the following content to answer. Do NOT add outside knowledge.
If the question is unrelated, respond with:
"I'm only able to answer questions based on the uploaded CSS content."

Tone instruction: {style_prompt}

Content:
{pdf_text}

User Question:
{user_input}
"""
            response = model.generate_content(prompt)
            bot_reply = response.text

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    # Save chat
    st.session_state.chat_history.append({
        "user": user_input,
        "bot": bot_reply
    })

