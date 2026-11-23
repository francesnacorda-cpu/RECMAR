
import streamlit as st
from openai import OpenAI

# =====================================
# RECMAR AI CHATBOT
# =====================================

st.set_page_config(
    page_title="RECMAR AI",
    page_icon="🤖",
    layout="centered"
)

# =====================================
# CUSTOM DESIGN
# =====================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07152e, #102b50);
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.stChatMessage {
    background-color: #18365b;
    border-radius: 15px;
    padding: 12px;
}

.stChatInput textarea {
    color: white !important;
}

header {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================

st.title("🤖 RECMAR AI")
st.subheader("Your AI companion. Talk about anything!")

st.caption("Powered by OpenAI | Version 1.0")

# =====================================
# API CONFIGURATION
# =====================================

api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.warning(
        "Please configure your OpenAI API key "
        "in Streamlit Secrets."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# =====================================
# CHAT MEMORY
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am RECMAR AI. "
                "I'm happy to talk with you! "
                "Ask me anything. 😊"
            )
        }
    ]

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:
    st.title("⚙️ RECMAR SETTINGS")

    st.write("Welcome to RECMAR AI!")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello again! I'm RECMAR. "
                    "What would you like to talk about?"
                )
            }
        ]
        st.rerun()

    st.divider()

    st.write("### About RECMAR")
    st.write(
        "RECMAR is an AI chatbot designed "
        "to answer questions, explain topics, "
        "and have conversations."
    )

    st.caption("RECMAR AI Version 1.0")

# =====================================
# DISPLAY CHAT HISTORY
# =====================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================
# USER INPUT
# =====================================

user_input = st.chat_input(
    "Message RECMAR..."
)

if user_input:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("RECMAR is thinking..."):

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are RECMAR, a friendly, intelligent,
helpful, and conversational AI assistant.

Your purpose is to help users talk about
almost anything.

You can:
- Answer general questions.
- Explain difficult subjects.
- Help with school activities.
- Write and improve essays.
- Help with programming.
- Give creative ideas.
- Have natural conversations.

Always:
- Be respectful and friendly.
- Give accurate and understandable answers.
- Explain complicated things simply.
- Admit when you do not know something.
- Never pretend to have information
  you do not actually have.
- Respond in the language the user uses
  whenever possible.

Your name is RECMAR.
"""
                        }
                    ] + st.session_state.messages,

                    temperature=0.7,
                    max_tokens=1500
                )

                ai_reply = response.choices[0].message.content

                st.markdown(ai_reply)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })

            except Exception as e:
                st.error(
                    "Sorry! RECMAR encountered an error."
                )
                st.caption(str(e))
