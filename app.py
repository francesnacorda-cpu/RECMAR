
import streamlit as st
import sqlite3
import uuid
import json
import os
import base64
import io
from datetime import datetime

from openai import OpenAI
from pypdf import PdfReader
from docx import Document


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="RECMAR AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "recmar_history.db"
AI_MODEL = "gpt-4o-mini"


# ==========================================
# 2. MODERN WEBSITE DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background: #f5f7fb;
    color: #172033;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #101b31;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #1769d2;
    letter-spacing: -1px;
}

.subtitle {
    color: #718096;
    font-size: 15px;
}

.stChatMessage {
    border-radius: 15px;
    padding: 12px;
}

.stChatInput {
    border-radius: 15px;
}

div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.7rem 2rem 0.7rem;
    }

    .main-title {
        font-size: 29px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. DATABASE SETUP
# ==========================================

def connect_db():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                owner TEXT,
                title TEXT,
                created TEXT,
                messages TEXT
            )
        """)

        conn.commit()


def create_conversation(owner):

    conversation_id = str(uuid.uuid4())

    messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm RECMAR, your personal AI "
                "assistant. 😊\n\n"
                "You can ask me questions, upload files, "
                "share pictures, or talk to me using your "
                "microphone. What would you like to do today?"
            )
        }
    ]

    with connect_db() as conn:

        conn.execute("""
            INSERT INTO conversations
            (id, owner, title, created, messages)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            owner,
            "New Conversation",
            datetime.now().isoformat(),
            json.dumps(messages)
        ))

        conn.commit()

    return conversation_id


def get_conversations(owner):

    with connect_db() as conn:

        rows = conn.execute("""
            SELECT id, title, created
            FROM conversations
            WHERE owner = ?
            ORDER BY created DESC
        """, (owner,)).fetchall()

    return rows


def get_messages(conversation_id, owner):

    with connect_db() as conn:

        row = conn.execute("""
            SELECT messages
            FROM conversations
            WHERE id = ? AND owner = ?
        """, (conversation_id, owner)).fetchone()

    if row:
        return json.loads(row[0])

    return []


def save_messages(conversation_id, owner, messages):

    title = "New Conversation"

    for message in messages:

        if message["role"] == "user":

            title = message["content"][:40]

            if len(message["content"]) > 40:
                title += "..."

            break

    with connect_db() as conn:

        conn.execute("""
            UPDATE conversations
            SET title = ?, messages = ?
            WHERE id = ? AND owner = ?
        """, (
            title,
            json.dumps(messages),
            conversation_id,
            owner
        ))

        conn.commit()


def delete_conversation(conversation_id, owner):

    with connect_db() as conn:

        conn.execute("""
            DELETE FROM conversations
            WHERE id = ? AND owner = ?
        """, (conversation_id, owner))

        conn.commit()


initialize_database()


# ==========================================
# 4. SESSION CONFIGURATION
# ==========================================

if "owner_id" not in st.session_state:
    st.session_state.owner_id = str(uuid.uuid4())

if "active_id" not in st.session_state:
    st.session_state.active_id = None

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

if "personality" not in st.session_state:
    st.session_state.personality = "Friendly"

if "custom_personality" not in st.session_state:
    st.session_state.custom_personality = ""


owner = st.session_state.owner_id


# ==========================================
# 5. OPENAI CONFIGURATION
# ==========================================

api_key = st.secrets.get(
    "OPENAI_API_KEY",
    os.getenv("OPENAI_API_KEY", "")
)

if not api_key:

    st.error("RECMAR cannot start without an API key.")

    st.info(
        "Add OPENAI_API_KEY to your Streamlit Secrets."
    )

    st.stop()

client = OpenAI(api_key=api_key)


# ==========================================
# 6. PERSONALITY SETTINGS
# ==========================================

PERSONALITIES = {

    "Friendly": """
    You are warm, friendly, encouraging, and approachable.
    Talk naturally like a helpful companion.
    """,

    "Professional": """
    You are professional, organized, respectful,
    and precise. Give well-structured responses.
    """,

    "Teacher": """
    You are an excellent teacher.
    Explain difficult lessons step by step.
    Use simple examples and make learning easy.
    """,

    "Funny": """
    You are humorous, cheerful, and entertaining.
    Use appropriate jokes while remaining helpful.
    """,

    "Creative": """
    You are imaginative, artistic, and creative.
    Help with writing, storytelling, ideas, and projects.
    """,

    "Simple": """
    Use simple words and short explanations.
    Make complicated topics easy to understand.
    """
}


def create_system_prompt():

    personality = PERSONALITIES.get(
        st.session_state.personality,
        PERSONALITIES["Friendly"]
    )

    custom = st.session_state.custom_personality

    return f"""
You are RECMAR AI, a helpful personal AI assistant.

YOUR IDENTITY:
Your name is RECMAR.
You are an intelligent, friendly, and capable AI.

YOUR PERSONALITY:
{personality}

ADDITIONAL PERSONALITY INSTRUCTIONS:
{custom}

YOUR ABILITIES:
- Answer general knowledge questions.
- Help with school and research activities.
- Explain mathematics and science.
- Write and improve essays.
- Help users understand documents.
- Analyze uploaded images.
- Assist with Python and programming.
- Have natural conversations.
- Help users brainstorm creative ideas.

YOUR RULES:
1. Always try to provide accurate information.
2. Never invent facts or sources.
3. Admit when you are uncertain.
4. Explain complicated ideas clearly.
5. Respect the user's opinions.
6. Respond in the language used by the user.
7. Be conversational, not robotic.
8. Your name is RECMAR, not ChatGPT.

Remember: You are RECMAR AI.
"""


# ==========================================
# 7. DOCUMENT READER
# ==========================================

def read_document(uploaded_file):

    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    try:

        if filename.endswith(".pdf"):

            pdf = PdfReader(io.BytesIO(file_bytes))

            text = ""

            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"

                if len(text) >= 30000:
                    break

            return text[:30000]

        elif filename.endswith(".txt"):

            return file_bytes.decode(
                "utf-8",
                errors="replace"
            )[:30000]

        elif filename.endswith(".docx"):

            document = Document(io.BytesIO(file_bytes))

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

            return text[:30000]

        else:
            return None

    except Exception as error:

        return f"Document reading error: {error}"


# ==========================================
# 8. IMAGE PROCESSING
# ==========================================

def encode_image(uploaded_file):

    image_bytes = uploaded_file.getvalue()

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    mime_type = uploaded_file.type or "image/jpeg"

    return f"data:{mime_type};base64,{encoded}"


# ==========================================
# 9. AI RESPONSE GENERATOR
# ==========================================

def generate_response(user_text, messages, uploaded_files):

    content = []

    # Add user's text
    if user_text.strip():

        content.append({
            "type": "text",
            "text": user_text
        })

    # Read documents and process images
    for uploaded_file in uploaded_files:

        filename = uploaded_file.name.lower()

        if filename.endswith(
            (".pdf", ".txt", ".docx")
        ):

            document_text = read_document(uploaded_file)

            if document_text:

                content.append({
                    "type": "text",
                    "text": (
                        f"\n\nDOCUMENT: {uploaded_file.name}\n"
                        f"{document_text}"
                    )
                })

        elif filename.endswith(
            (".png", ".jpg", ".jpeg", ".webp")
        ):

            image_url = encode_image(uploaded_file)

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "auto"
                }
            })

    if not content:

        content.append({
            "type": "text",
            "text": "Hello RECMAR!"
        })

    # Build conversation
    api_messages = [
        {
            "role": "system",
            "content": create_system_prompt()
        }
    ]

    for message in messages[-20:]:

        api_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    api_messages.append({
        "role": "user",
        "content": content
    })

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=api_messages,
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content


# ==========================================
# 10. VOICE GENERATION
# ==========================================

def generate_voice(text):

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text[:4000],
        instructions=(
            "Speak clearly, naturally, warmly, "
            "and conversationally."
        )
    )

    return speech.content


def transcribe_audio(audio_file):

    audio = io.BytesIO(audio_file.getvalue())
    audio.name = "recording.wav"

    result = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio
    )

    return result.text


# ==========================================
# 11. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# 🤖 RECMAR AI")

    st.caption("Your personal AI assistant")

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        st.session_state.active_id = create_conversation(
            owner
        )

        st.rerun()

    st.markdown("### 💬 Chat History")

    conversations = get_conversations(owner)

    for conversation_id, title, created in conversations:

        col1, col2 = st.columns([4, 1])

        with col1:

            if st.button(
                title,
                key=f"open_{conversation_id}",
                use_container_width=True
            ):

                st.session_state.active_id = conversation_id
                st.rerun()

        with col2:

            if st.button(
                "✕",
                key=f"delete_{conversation_id}"
            ):

                delete_conversation(
                    conversation_id,
                    owner
                )

                if st.session_state.active_id == conversation_id:
                    st.session_state.active_id = None

                st.rerun()

    st.divider()

    st.markdown("### ⚙️ RECMAR Settings")

    st.session_state.personality = st.selectbox(
        "AI Personality",
        list(PERSONALITIES.keys()),
        index=list(PERSONALITIES.keys()).index(
            st.session_state.personality
        )
    )

    st.session_state.custom_personality = st.text_area(
        "Custom Personality Instructions",
        value=st.session_state.custom_personality,
        placeholder="Example: Speak in a cheerful and supportive way.",
        height=90
    )

    st.session_state.voice_enabled = st.toggle(
        "🔊 Enable spoken responses",
        value=st.session_state.voice_enabled
    )

    st.divider()

    st.caption("RECMAR AI VERSION 4.0")
    st.caption("Powered by OpenAI")


# ==========================================
# 12. ACTIVE CONVERSATION
# ==========================================

if not st.session_state.active_id:

    st.session_state.active_id = create_conversation(
        owner
    )

active_id = st.session_state.active_id

messages = get_messages(active_id, owner)

if not messages:

    messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm RECMAR. How can I help you?"
        }
    ]


# ==========================================
# 13. MAIN CHAT INTERFACE
# ==========================================

st.markdown(
    '<div class="main-title">🤖 RECMAR AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask anything. Learn anything. Create anything.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# Display conversation
for message in messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# 14. FILE UPLOADER
# ==========================================

st.markdown("#### 📎 Attach files")

uploaded_files = st.file_uploader(
    "Upload PDF, DOCX, TXT, or images",
    type=[
        "pdf",
        "docx",
        "txt",
        "png",
        "jpg",
        "jpeg",
        "webp"
    ],
    accept_multiple_files=True,
    key="rec_mar_files"
)

if uploaded_files:

    for file in uploaded_files:

        st.caption(
            f"📄 Attached: {file.name}"
        )


# ==========================================
# 15. CHAT INPUT WITH MICROPHONE
# ==========================================

prompt = st.chat_input(
    "Message RECMAR or record your voice...",
    accept_audio=True,
    key="rec_mar_chat"
)


# ==========================================
# 16. PROCESS USER MESSAGE
# ==========================================

if prompt:

    user_text = prompt.text or ""

    # Convert recorded voice into text
    if prompt.audio:

        with st.spinner("RECMAR is listening..."):

            try:

                voice_text = transcribe_audio(
                    prompt.audio
                )

                if user_text.strip():

                    user_text += "\n" + voice_text

                else:

                    user_text = voice_text

                st.info(
                    f"🎤 Recognized speech: {voice_text}"
                )

            except Exception as error:

                st.error(
                    f"Voice recognition failed: {error}"
                )

                st.stop()

    # Add attachment descriptions to saved message
    attachment_names = [
        file.name for file in uploaded_files
    ]

    saved_text = user_text

    if attachment_names:

        saved_text += (
            "\n\n[Attached files: "
            + ", ".join(attachment_names)
            + "]"
        )

    if not user_text.strip() and not uploaded_files:

        st.warning("Please enter a message or attach a file.")
        st.stop()

    messages.append({
        "role": "user",
        "content": saved_text
    })

    with st.chat_message("user"):

        st.markdown(user_text or "Please analyze my attachment.")

        for name in attachment_names:
            st.caption(f"📎 {name}")

    # Generate AI answer
    with st.chat_message("assistant"):

        with st.spinner("RECMAR is thinking..."):

            try:

                ai_reply = generate_response(
                    user_text or "Please analyze the attached files.",
                    messages[:-1],
                    uploaded_files
                )

                st.markdown(ai_reply)

                messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })

                save_messages(
                    active_id,
                    owner,
                    messages
                )

                # Generate spoken response
                if st.session_state.voice_enabled:

                    try:

                        with st.spinner("RECMAR is preparing its voice..."):

                            audio_bytes = generate_voice(
                                ai_reply
                            )

                        st.audio(
                            audio_bytes,
                            format="audio/mpeg"
                        )

                    except Exception as voice_error:

                        st.warning(
                            f"Voice generation unavailable: {voice_error}"
                        )

            except Exception as error:

                st.error(
                    "RECMAR encountered an error. "
                    "Please check your API configuration."
                )

                st.caption(str(error))
