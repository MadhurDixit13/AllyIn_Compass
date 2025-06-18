import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.rag_tool import generate_rag_answer
from src.feedback.logger import log_feedback


st.set_page_config(page_title="AllyIn Compass", layout="wide")

st.title("🧭 AllyIn Compass")
st.markdown("Ask questions and get smart, document-backed answers!")

# Sidebar filters
st.sidebar.header("🔍 Filters")
domain = st.sidebar.selectbox("Domain", ["All", "Finance", "Biotech", "Energy"])
confidence = st.sidebar.slider("Confidence threshold (mock)", 0.0, 1.0, 0.5)

# Main input
user_query = st.text_input("Enter your query:", placeholder="e.g. Find CO2 violations since Q1 in San Jose")

if st.button("Get Answer") and user_query:
    with st.spinner("Thinking..."):
        try:
            answer = generate_rag_answer(user_query)
            st.success("✅ Answer")
            st.write(answer)

            # Feedback section
            st.markdown("**Rate this answer:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍"):
                    log_feedback(user_query, answer, 1)
                    st.toast("Thanks for the thumbs up! 👍")
            with col2:
                if st.button("👎"):
                    log_feedback(user_query, answer, 0)
                    st.toast("Thanks for your feedback! 👎")

        except Exception as e:
            st.error(f"Error: {e}")
            st.write("Please try again or refine your query.")
