import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------------------
# Config
# ------------------------------
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/query")

# Page setup
st.set_page_config(
    page_title="IntelliRAG",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.header("IntelliRAG")
    st.write("""
        IntelliRAG is an AI-powered document intelligence system built on
        Retrieval-Augmented Generation (RAG). Ask any question related to
        your corpus and get answers along with cited sources.
    """)
    st.markdown("---")

# ------------------------------
# Main interface
# ------------------------------
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>IntelliRAG</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Document Intelligence System — retrieve answers from your knowledge base with sources</p>", unsafe_allow_html=True)

query = st.text_input('Enter your question here:')

if st.button('Search') and query:
    with st.spinner('Querying the model...'):
        try:
            response = requests.post(API_URL, json={'q': query})
            response.raise_for_status()
            res = response.json()
            
            # Display answer
            st.markdown("###  Answer")
            st.info(res.get('answer', 'No answer found.'))
            
            # Display sources
            st.markdown("### Sources")
            sources = res.get('sources', [])
            if sources:
                for i, s in enumerate(sources, start=1):
                    st.markdown(f"**{i}.** {s}")
            else:
                st.write("No sources returned.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error querying the API: {e}")

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>IntelliRAG — Powered by Streamlit & LangChain</p>", unsafe_allow_html=True)
