import os

try:
    import streamlit as st

    if "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    else:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")

except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
