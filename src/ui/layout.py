import streamlit as st

def render_header():
    """Render the global application header."""
    st.set_page_config(
        page_title="CAMEL-AI 医疗智能体演示",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🏥 CAMEL-AI 医疗智能体演示")



