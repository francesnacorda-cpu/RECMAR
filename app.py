
# DESIGN - WHITE BACKGROUND, BLACK TEXT
st.markdown("""
<style>

/* White background */
.stApp {
    background-color: #FFFFFF;
}

/* Black text everywhere */
.stApp,
.stApp p,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp label,
.stApp span,
.stApp li,
.stApp strong {
    color: #000000 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F5F5F5;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #F2F2F2;
    color: #000000 !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF;
    color: #000000 !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #777777 !important;
}

/* Buttons */
.stButton button {
    background-color: #EEEEEE;
    color: #000000 !important;
    border: 1px solid #CCCCCC;
}

/* Dividers */
hr {
    border-color: #DDDDDD;
}

</style>
""", unsafe_allow_html=True)
