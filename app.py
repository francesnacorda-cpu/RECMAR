
# ==========================================================
# RECMAR 3.0
# ADVANCED AI CHATBOT
# CODING TEACHER + COMFORT COMPANION
# Built with Python, Streamlit, and OpenAI
# ==========================================================

import streamlit as st
from openai import OpenAI

# ----------------------------------------------------------
# PAGE SETTINGS
# ----------------------------------------------------------

st.set_page_config(
    page_title="RECMAR AI",
    page_icon="💗",
    layout="centered"
)

# ----------------------------------------------------------
# CUSTOM DESIGN
# ----------------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff0f6,
        #f5efff,
        #ffffff
    );
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #9b59b6;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 15px;
}

.stChatMessage {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# RECMAR PERSONALITY
# ----------------------------------------------------------

BASE_INSTRUCTIONS = """
You are RECMAR, an advanced AI chatbot and companion.

Your personality:
- Friendly, patient, caring, and respectful.
- Talk naturally and warmly.
- Use emojis occasionally.
- Never judge the user.
- Explain things clearly and simply.
- Never make the user feel stupid.

YOUR MAIN FUNCTIONS:

1. CODING TEACHER
- Teach Python from beginner to advanced.
- Explain programming concepts step by step.
- Write and explain code.
- Help debug errors.
- Give coding exercises and examples.
- Explain why a program works or fails.

2. COMFORT COMPANION
- Listen when the user feels sad, lonely, stressed,
  disappointed, or overwhelmed.
- Give sincere and supportive responses.
- Validate their feelings.
- Avoid judging or minimizing their problems.
- Ask gentle questions.
- Encourage professional or trusted-person support
  when appropriate.
- If the user may be in immediate danger, encourage
  contacting emergency services or a trusted person.

3. GENERAL AI ASSISTANT
- Answer educational and everyday questions.
- Help with schoolwork and creative ideas.
- Be honest if you do not know an answer.

4. MEMORY AND LEARNING
- Use the conversation history to understand the user.
- Remember useful details within the current chat.
- Do not claim to permanently remember information
  outside the available conversation history.

Always identify yourself as RECMAR when introducing yourself.
"""

# ----------------------------------------------------------
# CHAT MODES
# ----------------------------------------------------------

def get_instructions(mode):

    if mode == "Coding Tutor 💻":
        return BASE_INSTRUCTIONS + """
        CURRENT MODE: CODING TUTOR.
        Focus on teaching programming.
        Give detailed explanations and examples.
        Encourage the user to practice.
        """

    elif mode == "Comfort Friend 💗":
        return BASE_INSTRUCTIONS + """
        CURRENT MODE: COMFORT FRIEND.
        Focus on emotional support and listening.
        Be gentle, understanding, and reassuring.
        Do not force coding lessons into the conversation.
        """

    else:
        return BASE_INSTRUCTIONS + """
        CURRENT MODE: GENERAL CHAT.
        Balance coding, learning, and everyday conversation.
        Adapt to what the user needs.
        """

# ----------------------------------------------------------
# SESSION MEMORY
# ----------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------

st.markdown(
    '<div class="main-title">💗 RECMAR</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your AI Coding Buddy & Comfort Companion'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

st.success("RECMAR is ready! Let's talk. 😊")

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

with st.sidebar:

    st.title("⚙️ RECMAR SETTINGS")

    mode = st.selectbox(
        "Choose your chat mode:",
        [
            "General Chat 🌸",
            "Coding Tutor 💻",
            "Comfort Friend 💗"
        ],
        index=0
    )

    st.divider()

    st.subheader("About RECMAR")

    st.write("🤖 AI-powered conversations")
    st.write("💻 Python coding lessons")
    st.write("🫂 Emotional support")
    st.write("🧠 Conversation memory")

    st.divider()

    if st.button("🗑️ Start New Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.caption("RECMAR AI Version 3.0")

# ----------------------------------------------------------
# DISPLAY CHAT HISTORY
# ----------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="💗" if message["role"] == "assistant" else "😊"
    ):
        st.markdown(message["content"])

# ----------------------------------------------------------
# OPENAI CONNECTION
# ----------------------------------------------------------

def get_ai_response(messages, selected_mode):

    api_key = st.secrets["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"]

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5.5",
        instructions=get_instructions(selected_mode),
        input=messages[-30:],
        max_output_tokens=2000,
        store=False
    )

    return response.output_text

# ----------------------------------------------------------
# USER INPUT
# ----------------------------------------------------------

user_input = st.chat_input(
    "Talk to RECMAR... 💬"
)

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user", avatar="😊"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="💗"):

        with st.spinner("RECMAR is thinking... 💭"):

            try:

                answer = get_ai_response(
                    st.session_state.messages,
                    mode
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    "Oops! RECMAR encountered a problem."
                )

                st.caption(
                    "Check your API key, internet connection, "
                    "and API access."
                )

                st.session_state.messages.pop()

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------

st.divider()

st.markdown(
    "<center>Made with 💗 for RECMAR users</center>",
    unsafe_allow_html=True
)
