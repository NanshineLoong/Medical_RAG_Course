import streamlit as st
from src.core.models import ModelConfig

def render_model_config_section():
    """Render the model connection settings in the sidebar."""
    st.sidebar.header("🔌 模型连接配置")
    
    # Base URL
    st.session_state.model_config.base_url = st.sidebar.text_input(
        "Base URL", 
        value=st.session_state.model_config.base_url,
        help="例如: https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # API Key
    st.session_state.model_config.api_key = st.sidebar.text_input(
        "API Key",
        value=st.session_state.model_config.api_key,
        type="password"
    )
    
    # Model Name
    st.session_state.model_config.model_name = st.sidebar.text_input(
        "Model Name",
        value=st.session_state.model_config.model_name
    )
    
    # Temperature
    st.session_state.model_config.temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.model_config.temperature,
        step=0.1
    )
    
    st.sidebar.markdown("---")



