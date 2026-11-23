
import streamlit as st
from openai import OpenAI

# PAGE SETTINGS
st.set_page_config(
    page_title="RECMAR AI",
    page_icon="🤖",
    layout="centered"
)

# DESIGN
st.markdown("""
<style>
.stApp {
    background: #101827;
    color: white;
}
h1 {
    text-align: center;
    color: #55b8ff;
}
p {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# API KEY
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY:
    st.error("API KEY NOT FOUND. Please configure Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# SESSION HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.title("🤖 RECMAR AI")
    st.write("Your personal AI assistant.")

    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by OpenAI")

# HEADER
st.title("🤖 RECMAR AI")
st.markdown(
    "<center>Your intelligent AI assistant. Ask me anything!</center>",
    unsafe_allow_html=True
)

st.divider()

# DISPLAY MESSAGES
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT
prompt = st.chat_input("Message RECMAR...")

if prompt:

    # SHOW USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # GENERATE AI RESPONSE
    with st.chat_message("assistant"):

        with st.spinner("RECMAR is thinking..."):

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions="""
                    Your name is RECMAR AI.
                    You are a friendly, intelligent,
                    helpful and creative AI assistant.
                    You can answer questions, explain lessons,
                    write content, solve problems and help
                    users with programming.
                    Always provide clear and useful answers.
                    """,
                    input=st.session_state.messages
                )

                answer = response.output_text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error("RECMAR encountered an error.")
                st.code(str(e))

    st.rerun()

# FOOTER
st.divider()
st.caption("© RECMAR AI | Generative Artificial Intelligence")
