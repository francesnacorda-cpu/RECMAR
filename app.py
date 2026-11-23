
import streamlit as st

st.set_page_config(
    page_title="RECMAR TEST",
    page_icon="💗"
)

st.title("💗 RECMAR IS WORKING!")

st.success("Your Streamlit website is running!")

st.write("Welcome! This is a test of your RECMAR application.")

name = st.text_input("What is your name?")

if name:
    st.write(f"Hello, {name}! Nice to meet you! 😊")

st.chat_input("Type something here...")
