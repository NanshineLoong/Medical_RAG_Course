import streamlit as st

def render_expert_qa_tab():
    """Render the Expert QA / Chat with Doctor tab."""    
    # --- Configuration Section ---
    with st.expander("⚙️ 专家设定与知识库配置", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👨‍⚕️ 医生人设")
            default_prompt = "你是一个经验丰富的全科医生。"
            if "qa_system_prompt" not in st.session_state:
                st.session_state.qa_system_prompt = default_prompt
                
            st.session_state.qa_system_prompt = st.text_area(
                "System Instruction",
                value=st.session_state.qa_system_prompt,
                height=150,
                key="qa_sys_prompt_input"
            )
        
        with col2:
            st.subheader("📚 RAG 知识库")
            
            # List existing KBs
            existing_kbs = st.session_state.rag_manager.list_knowledge_bases()
            
            kb_mode = st.radio("知识库操作", ["选择现有知识库", "新建/更新知识库"], horizontal=True)
            
            if kb_mode == "选择现有知识库":
                if existing_kbs:
                    selected_kb = st.selectbox("选择知识库", existing_kbs, key="qa_kb_selector")
                    if selected_kb != st.session_state.rag_manager.current_kb_name:
                         if st.button("📂 加载该知识库"):
                            with st.spinner(f"正在加载 {selected_kb}..."):
                                if st.session_state.rag_manager.load_knowledge_base(selected_kb):
                                    st.success(f"已加载: {selected_kb}")
                                else:
                                    st.error("加载失败")
                else:
                    st.info("暂无本地知识库，请先新建。")
            
            else: # Create New
                new_kb_name = st.text_input("知识库名称 (英文/数字)", placeholder="e.g. pediatrics_v1")
                uploaded_files = st.file_uploader(
                    "上传参考文档 (TXT/MD)", 
                    accept_multiple_files=True,
                    type=["txt", "md"],
                    key="qa_file_uploader"
                )
                
                if uploaded_files and new_kb_name:
                    if st.button("🚀 创建并处理"):
                        with st.spinner("正在处理文档并构建索引..."):
                            status = st.session_state.rag_manager.process_files(new_kb_name, uploaded_files)
                            st.success(status)
                            st.rerun() # Refresh to show in list

            st.caption(f"当前状态: {st.session_state.rag_manager.vector_store_status}")
            
            enable_rag = st.checkbox("开启 RAG 模式", value=getattr(st.session_state, 'enable_rag', False), key="qa_enable_rag")
            st.session_state.enable_rag = enable_rag
            
            if enable_rag:
                st.session_state.rag_threshold = st.slider("相似度阈值", 0.0, 1.0, 0.6, key="qa_rag_threshold")
                st.session_state.rag_top_k = st.slider("检索 Top-K", 1, 10, 3, key="qa_rag_topk")

    st.markdown("---")

    # Quick Questions and Reset
    if not st.session_state.messages_qa:
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            if st.button("临床药理学的主要研究内容和核心任务分别是什么?"):
                st.session_state.current_input = "临床药理学的主要研究内容和核心任务分别是什么?"
        with col_q2:
            if st.button("新药临床试验的 I、II、III、IV 期各自的主要内容是什么"):
                st.session_state.current_input = "新药临床试验的 I、II、III、IV 期各自的主要内容是什么"
        with col_q3:
            if st.button("临床试验中必须遵循哪些核心伦理学原则？"):
                st.session_state.current_input = "临床试验中必须遵循哪些核心伦理学原则？"
    else:
        if st.button("🔄 重置对话"):
            st.session_state.messages_qa = []
            st.rerun()

    # Chat History
    for msg in st.session_state.messages_qa:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            # Show RAG context if enabled (even if empty)
            if msg["role"] == "assistant" and getattr(st.session_state, 'enable_rag', False):
                rag_data = msg.get("rag_context", [])
                
                with st.expander(f"📚 参考了 {len(rag_data)} 个文档片段"):
                    if not rag_data:
                        st.caption("没有找到符合阈值的相关文档。")
                    else:
                        for idx, ctx in enumerate(rag_data):
                            score = float(ctx.get('similarity', 0.0))
                            text = ctx.get('text', '')
                            # Show a snippet in the header
                            summary = f"片段 {idx+1} (相似度: {score:.4f})"
                            
                            # Use HTML details for nested expander effect
                            st.markdown(
                                f"""
                                <details>
                                <summary>{summary}</summary>
                                <div style='padding: 10px; border-left: 3px solid #ccc; background-color: #f9f9f9; margin-top: 5px;'>
                                <pre style='white-space: pre-wrap; word-wrap: break-word;'>{text}</pre>
                                </div>
                                </details>
                                """,
                                unsafe_allow_html=True
                            )

    # Input Area
    if "current_input" in st.session_state and st.session_state.current_input:
        prompt = st.session_state.current_input
        del st.session_state.current_input
        handle_user_input(prompt)
        st.rerun()
    
    prompt = st.chat_input("请输入您的病情或问题...")
    if prompt:
        handle_user_input(prompt)
        st.rerun()

def handle_user_input(prompt: str):
    """Process user input for QA tab."""
    st.session_state.messages_qa.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)

    # 1. RAG Retrieval
    rag_context = []
    if getattr(st.session_state, 'enable_rag', False):
         rag_context = st.session_state.rag_manager.retrieve(
             prompt, 
             getattr(st.session_state, 'rag_threshold', 0.7), 
             getattr(st.session_state, 'rag_top_k', 3)
         )
    
    # 2. Build Prompt with Context
    full_prompt = prompt
    if rag_context:
        # Extract text for the prompt
        context_str = "\n".join([item['text'] for item in rag_context])
        full_prompt = f"Background Information:\n{context_str}\n\nUser Question: {prompt}"
        
    # 3. Call Camel Agent with Streaming
    response_content = ""
    with st.chat_message("assistant"):
        with st.spinner("医生正在思考..."):
            from camel.agents import ChatAgent
            from camel.messages import BaseMessage
            from camel.models import ModelFactory
            from camel.types import ModelPlatformType
            
            # Helper to create model
            model_config = st.session_state.model_config
            model_instance = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=model_config.model_name or "qwen-plus",
                url=model_config.base_url,
                api_key=model_config.api_key,
                model_config_dict={"temperature": model_config.temperature}
            )
            
            # System Message
            sys_msg = BaseMessage.make_assistant_message(
                role_name="Expert",
                content=st.session_state.qa_system_prompt
            )
            
            agent = ChatAgent(system_message=sys_msg, model=model_instance)
            
            user_msg = BaseMessage.make_user_message(role_name="User", content=full_prompt)
            
            try:
                response = agent.step(user_msg)
                response_content = response.msg.content if response and getattr(response, "msg", None) else ""
            except Exception as exc:
                response_content = f"模型响应失败：{exc}"
            
            st.write(response_content or "（未返回内容）")

    st.session_state.messages_qa.append({
        "role": "assistant", 
        "content": response_content,
        "rag_context": rag_context
    })
