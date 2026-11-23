import os
import base64
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ==========================================
# RECMAR AI - GENERATIVE AI CHATBOT
# ==========================================

st.set_page_config(
    page_title="RECMAR AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CONFIGURATION
# ==========================================

def get_api_key():
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        try:
            key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            key = None

    return key


API_KEY = get_api_key()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

SYSTEM_PROMPT = """
You are RECMAR, a friendly, intelligent and helpful generative AI assistant.

Your identity:
- Your name is RECMAR AI.
- You are a knowledgeable and conversational AI assistant.
- You can discuss almost any topic.
- You help with education, science, technology, business,
  programming, writing, mathematics and everyday questions.
- Explain complicated topics in simple language when needed.
- Be respectful, creative, patient and professional.
- Give accurate answers and admit when you are uncertain.
- Never pretend to know information you do not know.
- Respond in the same language as the user when appropriate.
"""

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "image_data" not in st.session_state:
    st.session_state.image_data = None

if "image_mime" not in st.session_state:
    st.session_state.image_mime = None

if "pending_voice" not in st.session_state:
    st.session_state.pending_voice = None


# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #0b1020;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111a30;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #65aaff;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #aab8d0;
    margin-bottom: 25px;
}

.stChatMessage {
    border-radius: 15px;
}

div.stButton > button {
    border-radius: 12px;
    width: 100%;
    font-weight: bold;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# 🤖 RECMAR AI")
    st.caption("Your personal generative AI assistant")

    st.divider()

    if st.button("➕ NEW CHAT"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.image_data = None
        st.session_state.image_mime = None
        st.session_state.pending_voice = None
        st.rerun()

    st.divider()

    st.markdown("### 📁 Upload Documents")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        key="pdf_upload"
    )

    if uploaded_pdf is not None:
        try:
            reader = PdfReader(uploaded_pdf)
            extracted = []

            for page in reader.pages:
                extracted.append(page.extract_text() or "")

            st.session_state.pdf_text = "\n".join(extracted)[:30000]
            st.success("PDF successfully loaded!")

        except Exception as e:
            st.error(f"PDF error: {e}")

    uploaded_image = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_upload"
    )

    if uploaded_image is not None:
        image_bytes = uploaded_image.getvalue()

        if len(image_bytes) > 10 * 1024 * 1024:
            st.error("Image must be smaller than 10 MB.")
        else:
            st.session_state.image_data = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            st.session_state.image_mime = uploaded_image.type
            st.image(uploaded_image, caption="Uploaded image")
            st.success("Image ready for RECMAR!")

    if st.button("🗑️ CLEAR UPLOADS"):
        st.session_state.pdf_text = ""
        st.session_state.image_data = None
        st.session_state.image_mime = None
        st.rerun()

    st.divider()

    st.markdown("### 💬 Chat History")

    if not st.session_state.messages:
        st.caption("Your conversations will appear here.")

    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            label = message["content"][:35]
            st.caption(f"👤 {label}")

    st.divider()

    st.caption("RECMAR AI | Generative AI")
    st.caption("Powered by OpenAI")


# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🤖 RECMAR AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask anything. Learn anything. Create anything.</div>',
    unsafe_allow_html=True
)

# ==========================================
# API CONNECTION
# ==========================================

if not API_KEY:
    st.error(
        "OPENAI API KEY NOT FOUND. "
        "Please configure your API key in Streamlit Secrets."
    )
    st.stop()

client = OpenAI(api_key=API_KEY)


# ==========================================
# AI RESPONSE FUNCTION
# ==========================================

def generate_response(user_message):

    conversation = []

    # Previous conversation
    for msg in st.session_state.messages:
        conversation.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add PDF content to the current question
    full_message = user_message

    if st.session_state.pdf_text:
        full_message += (
            "\n\nDOCUMENT CONTENT:\n"
            + st.session_state.pdf_text
        )

    # Current user message
    if st.session_state.image_data:
        current_content = [
            {
                "type": "input_text",
                "text": full_message
            },
            {
                "type": "input_image",
                "image_url": (
                    "data:"
                    + st.session_state.image_mime
                    + ";base64,"
                    + st.session_state.image_data
                )
            }
        ]

        conversation.append({
            "role": "user",
            "content": current_content
        })

    else:
        conversation.append({
            "role": "user",
            "content": full_message
        })

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=conversation,
        max_output_tokens=2000
    )

    return response.output_text


# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# VOICE INPUT
# ==========================================

st.markdown("### 🎤 Talk to RECMAR")

audio = st.audio_input(
    "Record your voice",
    key="voice_recorder"
)

if audio is not None:

    if st.button("📨 SEND VOICE MESSAGE"):

        try:
            with st.spinner("RECMAR is listening..."):

                transcript = client.audio.transcriptions.create(
                    model="gpt-transcribe",
                    file=(
                        "voice.wav",
                        audio.getvalue(),
                        "audio/wav"
                    )
                )

                st.session_state.pending_voice = transcript.text

                st.success(
                    "Voice recognized: " + transcript.text
                )

        except Exception as e:
            st.error(f"Voice recognition error: {e}")


# ==========================================
# TEXT CHAT INPUT
# ==========================================

prompt = st.chat_input("Message RECMAR AI...")

if prompt or st.session_state.pending_voice:

    user_message = (
        prompt
        if prompt
        else st.session_state.pending_voice
    )

    st.session_state.pending_voice = None

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("RECMAR is thinking..."):

            try:

                answer = generate_response(user_message)

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                error_message = (
                    "Sorry! RECMAR encountered an error. "
                    "Please check your API key, internet connection, "
                    "model access, and API billing.\n\n"
                    f"Technical details: {e}"
                )

                st.error(error_message)

    st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    "<center>🤖 <b>RECMAR AI</b> — "
    "Your ideas, powered by artificial intelligence.</center>",
    unsafe_allow_html=True
)
