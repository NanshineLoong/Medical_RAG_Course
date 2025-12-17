import streamlit as st
from src.utils.state import init_session_state
from src.ui.layout import render_header
from src.ui.sidebar import render_model_config_section
from src.ui.tabs.expert_qa import render_expert_qa_tab
from src.ui.tabs.consultation import render_consultation_tab

def main():
    # 1. Render Global Header (Must be first)
    render_header()

    # 2. Initialize State
    init_session_state()
    
    # 3. Sidebar Configuration & Navigation
    with st.sidebar:
        st.title("功能导航")
        page = st.radio("选择模式", ["问答模式", "模拟模式"], index=0)
        st.divider()
        render_model_config_section()

    # 4. Main Content
    if page == "问答模式":
        render_expert_qa_tab()
    elif page == "模拟模式":
        render_consultation_tab()

if __name__ == "__main__":
    main()
