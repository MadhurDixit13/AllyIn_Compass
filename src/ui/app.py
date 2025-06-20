import torch
try:
    del torch.__path__
except AttributeError:
    pass

import streamlit as st
import os
os.environ["PYTORCH_DISABLE_CHECKPOINT"] = "1"
import sys

import altair as alt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.tools.rag_tool import generate_rag_answer
from src.feedback.logger import log_feedback
from src.dashboards.metrics import load_logs


st.set_page_config(page_title="AllyIn Compass", layout="wide")

st.title("🧭 AllyIn Compass")
st.markdown("Ask questions and get smart, document-backed answers!")
st.markdown("---")

# Sidebar filters
st.sidebar.markdown("### 📂 Filters & Logs")
st.sidebar.header("🔍 Filters")
domain = st.sidebar.selectbox("Domain", ["All", "Movies", "Projects", "Customers"])
confidence = st.sidebar.slider("Confidence threshold (mock)", 0.0, 1.0, 0.5)

st.sidebar.header("📈 Usage Metrics")

df = load_logs()
if not df.empty:
    st.sidebar.markdown(f"**Total queries:** {len(df)}")

    chart = alt.Chart(df).mark_bar().encode(
        x='date:T',
        y='count()',
        tooltip=['date:T', 'count()']
    ).properties(width=250, height=100)
    st.sidebar.altair_chart(chart)

    if "response_time" in df.columns:
        avg_time = round(df["response_time"].mean(), 2)
        st.sidebar.markdown(f"**Avg Response Time:** {avg_time}s")


    st.sidebar.markdown("**Tool Usage:**")
    tool_counts = df["tool"].value_counts().to_dict()
    for tool, count in tool_counts.items():
        st.sidebar.markdown(f"- {tool}: {count}")
else:
    st.sidebar.write("No logs yet.")


# Main input
user_query = st.text_input("Enter your query:", placeholder="e.g. Find CO2 violations since Q1 in San Jose")
modified_query = f"[{domain}] {user_query}" if domain != "All" else user_query



if st.button("💬 Ask", type="primary") and user_query:
    with st.spinner("Thinking..."):
        try:
            result = generate_rag_answer(modified_query)
            st.session_state["latest_query"] = user_query
            st.session_state["latest_answer"] = result["answer"]
            st.success("✅ Answer")
            st.write(result["answer"])
            with st.expander("📄 Sources used"):
                for file in result["sources"]:
                    st.markdown(f"- `{file}`")
        except Exception as e:
            st.error(f"Error: {e}")
            st.write("Please try again or refine your query.")

if "latest_answer" in st.session_state:
    st.markdown("**Rate this answer:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍"):
            log_feedback(st.session_state["latest_query"], st.session_state["latest_answer"], 1, tool="RAG", response_time=0)
            st.toast("Thanks for the thumbs up! 👍")
    with col2:
        if st.button("👎"):
            log_feedback(st.session_state["latest_query"], st.session_state["latest_answer"], 0, tool="RAG", response_time=0)
            st.toast("Thanks for your feedback! 👎")


