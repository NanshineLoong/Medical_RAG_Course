import streamlit as st
from src.core.models import ModelConfig
from src.core.rag import RAGManager
from src.core.agents import AgentManager

def init_session_state():
    """Initialize Streamlit session state variables."""
    
    if "model_config" not in st.session_state:
        st.session_state.model_config = ModelConfig(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key="",
            model_name="qwen-flash",
            temperature=0.2
        )

    if "rag_manager" not in st.session_state:
        st.session_state.rag_manager = RAGManager()

    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = AgentManager()

    if "messages_qa" not in st.session_state:
        st.session_state.messages_qa = []
        
    if "messages_sim" not in st.session_state:
        st.session_state.messages_sim = []



