import streamlit as st
import json
from src.core.agents import SimulationStatus

# --- Patient Presets ---
PATIENT_PRESETS = {
    "胃炎患者 (Zhang)": {
        "profile": "姓名：张三\n性别：男\n年龄：45岁\n主诉：上腹部隐痛不适2个月。\n现病史：患者2个月前无明显诱因出现上腹部隐痛，呈持续性，与进食无明显关系，伴饱胀感、嗳气，无反酸、烧心，无恶心、呕吐，无呕血、黑便。自服“胃药”（具体不详）后症状无明显缓解。发病以来，食欲尚可，睡眠佳，大小便正常，体重无明显变化。\n既往史：否认高血压、糖尿病病史。\n过敏史：无。",
        "rag_text": "【胃镜检查报告】\n检查日期：2023-10-15\n检查所见：食管黏膜光滑，血管纹理清晰，齿状线清晰。贲门开闭良好。胃底黏膜充血，粘液湖清亮。胃体黏膜红白相间，以红为主，皱襞肿胀。胃角切迹形态正常。胃窦黏膜充血水肿，红白相间，散在点片状糜烂。幽门圆，开闭良好。十二指肠球部及降部未见明显异常。\n诊断意见：慢性非萎缩性胃炎伴糜烂。",
        "diagnosis": "慢性非萎缩性胃炎"
    },
    "高血压患者 (Li)": {
        "profile": "姓名：李四\n性别：女\n年龄：58岁\n主诉：头晕、头痛1周。\n现病史：患者1周前劳累后出现头晕、头痛，以颞部胀痛为主，伴颈部僵硬感，无视物旋转，无恶心呕吐，无肢体麻木无力。休息后症状未见明显缓解。自测血压160/95mmHg。\n既往史：发现血压升高2年，最高170/100mmHg，不规律服用“硝苯地平”，未监测血压。",
        "rag_text": "【动态血压监测报告】\n检查日期：2023-10-20\n监测结果：\n24小时平均血压：155/92 mmHg\n白昼平均血压：162/98 mmHg\n夜间平均血压：140/85 mmHg\n血压负荷：收缩压 > 135mmHg 占 85%，舒张压 > 85mmHg 占 70%。\n结论：符合高血压诊断，非杓型血压改变。\n\n【生化检查】\n甘油三酯：2.8 mmol/L (↑)\n总胆固醇：6.2 mmol/L (↑)\n血糖：5.8 mmol/L (-)",
        "diagnosis": "高血压病（2级，很高危）"
    },
    "糖尿病患者 (Wang)": {
        "profile": "姓名：王五\n性别：男\n年龄：62岁\n主诉：口干、多饮、多尿3个月。\n现病史：患者3个月前出现口干，每日饮水量约2500ml，尿量增多，夜尿3-4次。伴体重下降约5kg。无视物模糊，无手足麻木。\n既往史：吸烟史20年，每日1包。",
        "rag_text": "【空腹血糖检测】\n结果：11.2 mmol/L (参考值 3.9-6.1)\n\n【糖化血红蛋白 (HbA1c)】\n结果：9.5% (参考值 4.0-6.0%)\n\n【尿常规】\n尿糖：(3+)\n尿酮体：(-)\n尿蛋白：(+)",
        "diagnosis": "2型糖尿病"
    },
    "自定义病人": {
        "profile": "",
        "rag_text": "",
        "diagnosis": ""
    }
}

def render_consultation_tab():
    """Render the Consultation Simulation tab."""
    
    # --- Settings Panel ---
    # Only show settings if not running or explicitly expanded
    is_idle = st.session_state.agent_manager.status == SimulationStatus.IDLE
    max_iterations = 5
    
    with st.expander("📝 模拟参数设置", expanded=is_idle):
        
        # Ensure session state is initialized if not present (e.g. first run)
        if "sim_patient_profile" not in st.session_state:
             # Initialize with first key
             first_key = list(PATIENT_PRESETS.keys())[0]
             st.session_state.sim_patient_profile = PATIENT_PRESETS[first_key]["profile"]
             st.session_state.sim_rag_text = PATIENT_PRESETS[first_key]["rag_text"]
             st.session_state.sim_diagnosis = PATIENT_PRESETS[first_key]["diagnosis"]
             # Initialize selector explicitly to match
             if "preset_selector" not in st.session_state:
                 st.session_state.preset_selector = first_key

        def on_preset_change():
            """Callback for preset selection change"""
            # This will be called BEFORE the rest of the script reruns
            selected = st.session_state.preset_selector
            data = PATIENT_PRESETS[selected]
            st.session_state.sim_patient_profile = data["profile"]
            st.session_state.sim_rag_text = data["rag_text"]
            st.session_state.sim_diagnosis = data["diagnosis"]

        # Patient Selection
        st.selectbox(
            "选择模拟病人案例", 
            options=list(PATIENT_PRESETS.keys()),
            key="preset_selector",
            on_change=on_preset_change
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("病人设定 (Patient)")
            patient_profile = st.text_area(
                "病人档案", 
                height=300,
                key="sim_patient_profile"
            )
            # Display Truth Diagnosis (Label)
            if st.session_state.get("sim_diagnosis"):
                 st.info(f"💡 真实诊断 (仅供参考): {st.session_state.sim_diagnosis}")
            
        with col2:
            st.subheader("医生设定 (Doctor)")
            default_doc = "你是一名专业医生。请通过循序渐进的问诊来明确病因。每次提问控制在 2–3 句话内，问题应具有针对性和医学逻辑。在收集到足够且必要的信息之前，不要给出诊断；仅在信息充分后，才进行综合分析并给出诊断结论。"
            doctor_prompt = st.text_area("医生 Prompt", value=default_doc, height=150, key="sim_doc_prompt")
            
            st.subheader("检查报告 (RAG 知识库)")
            use_rag = st.checkbox("启用 RAG 工具", value=True, key="use_rag_checkbox")
            st.caption("医生可以通过工具搜索这里的内容")
            rag_text_input = st.text_area(
                "输入检查报告文本", 
                height=150,
                key="sim_rag_text"
            )

    # --- Control Panel ---
    st.markdown("---")
    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    
    with col_ctrl1:
        mode = st.radio(
            "选择交互模式", 
            ["🤖 全自动模拟", "👨‍⚕️ 我来扮演医生", "🤒 我来扮演病人"],
            horizontal=True
        )
        
    with col_ctrl2:
        btn_label = "🚀 开始模拟" if is_idle else "🔄 重置模拟"
        if st.button(btn_label, use_container_width=True):
            with st.spinner("正在初始化模拟环境..."):
                # 1. Initialize RAG for Simulation
                st.session_state.agent_manager.initialize_agents(
                    patient_profile=patient_profile, 
                    doctor_instruction=doctor_prompt +  f"你最多进行 {max_iterations} 次问诊，确诊后输出 <DIAGNOSIS_DONE>。", 
                    model_config=st.session_state.model_config,
                    rag_content=rag_text_input if use_rag else "", # Pass the text directly only if enabled
                    max_steps=max_iterations
                )
            st.session_state.messages_sim = [] # Clear legacy history if any
            
            # 2. Trigger initial message based on mode
            if "我来扮演医生" in mode:
                 with st.spinner("病人正在进入诊室..."):
                    st.session_state.agent_manager.generate_opening_message("Patient")
                    
            elif "我来扮演病人" in mode:
                with st.spinner("医生正在准备提问..."):
                    st.session_state.agent_manager.generate_opening_message("Doctor")
            
            else:
                # "全自动模拟"
                pass

            st.rerun()

    # --- Simulation Display ---
    st.markdown("### 💬 模拟对话")
    
    # Display History
    if st.session_state.agent_manager.status != SimulationStatus.IDLE:
        for msg in st.session_state.agent_manager.chat_history:
            role = msg["role"]
            content = msg["content"]
            
            # Icon selection
            if role == "Doctor":
                avatar = "👨‍⚕️"
            elif role == "Patient":
                avatar = "🤒"
            elif role == "system": # Tool outputs etc
                avatar = "🛠️"
            else:
                avatar = "❓"

            with st.chat_message(role, avatar=avatar):
                st.write(content)
                # If there are tool calls info in the message (custom field), display them
                # ONLY if tool_calls list is present and NOT empty
                if "tool_calls" in msg and msg["tool_calls"]:
                    with st.expander("🛠️ 工具调用详情"):
                        for tc in msg["tool_calls"]:
                            data = tc.model_dump() if hasattr(tc, "model_dump") else tc.dict()
                            st.code(
                                "Tool: " + str(data.get("tool_name")) + "\n"
                                "Args: " + json.dumps(data.get("args"), indent=2, ensure_ascii=False, default=str) + "\n"
                                "Result: " + json.dumps(data.get("result"), indent=2, ensure_ascii=False, default=str)
                            )

    # Simulation Logic / Input
    if st.session_state.agent_manager.status == SimulationStatus.RUNNING:
        
        # Check if we need to trigger an AI response in role-play modes
        # This allows user input to be shown immediately before the AI responds
        if st.session_state.agent_manager.chat_history:
            last_msg = st.session_state.agent_manager.chat_history[-1]
            last_role = last_msg["role"]
            
            trigger_ai = False
            if "我来扮演医生" in mode and last_role == "Doctor":
                trigger_ai = True
            elif "我来扮演病人" in mode and last_role == "Patient":
                trigger_ai = True
                
            if trigger_ai:
                with st.spinner("对方正在思考中..."):
                    st.session_state.agent_manager.step_simulation()
                st.rerun()

        if "全自动模拟" in mode:
            if st.button("开始全自动运行", type="primary"):
                # Run loop
                loop_safety_counter = 0
                safety_limit = 20 # Prevent infinite loops
                
                with st.spinner("模拟对话生成中..."):
                    while st.session_state.agent_manager.status == SimulationStatus.RUNNING and \
                          st.session_state.agent_manager.current_step <= max_iterations and \
                          loop_safety_counter < safety_limit:
                        
                        loop_safety_counter += 1
                        
                        message = st.session_state.agent_manager.step_simulation()
                        if not message:
                            break
                        
                        role_name = message["role"]
                        avatar = "👨‍⚕️" if role_name == "Doctor" else "🤒"
                        
                        with st.chat_message(role_name, avatar=avatar):
                            st.write(message.get("content", ""))
                            if message.get("tool_calls"):
                                with st.expander("🛠️ 工具调用详情"):
                                    for tc in message["tool_calls"]:
                                        data = tc.model_dump() if hasattr(tc, "model_dump") else tc.dict()
                                        st.code(
                                            "Tool: " + str(data.get("tool_name")) + "\n"
                                            "Args: " + json.dumps(data.get("args"), indent=2, ensure_ascii=False, default=str) + "\n"
                                            "Result: " + json.dumps(data.get("result"), indent=2, ensure_ascii=False, default=str)
                                        )
                        
                        # Check if we should stop
                        if st.session_state.agent_manager.status == SimulationStatus.COMPLETED:
                            break
                            
                    st.rerun()
                
            if st.button("单步执行 (Step)"):
                 with st.spinner("正在生成下一条回复..."):
                     message = st.session_state.agent_manager.step_simulation()
                 
                 if message:
                     role_name = message["role"]
                     avatar = "👨‍⚕️" if role_name == "Doctor" else "🤒"
                     with st.chat_message(role_name, avatar=avatar):
                         st.write(message.get("content", ""))
                         if message.get("tool_calls"):
                             with st.expander("🛠️ 工具调用详情"):
                                 for tc in message["tool_calls"]:
                                     data = tc.model_dump() if hasattr(tc, "model_dump") else tc.dict()
                                     st.code(
                                         "Tool: " + str(data.get("tool_name")) + "\n"
                                         "Args: " + json.dumps(data.get("args"), indent=2, ensure_ascii=False, default=str) + "\n"
                                         "Result: " + json.dumps(data.get("result"), indent=2, ensure_ascii=False, default=str)
                                     )
                     st.rerun()
                    
        elif "我来扮演医生" in mode:
            user_input = st.chat_input("请输入医生问诊内容...")
            if user_input:
                st.session_state.agent_manager.add_message("Doctor", user_input)
                st.rerun()
                
        elif "我来扮演病人" in mode:
            user_input = st.chat_input("请输入病人回答...")
            if user_input:
                st.session_state.agent_manager.add_message("Patient", user_input)
                st.rerun()
    
    if st.session_state.agent_manager.status == SimulationStatus.COMPLETED:
         st.success("✅ 诊断结束，模拟完成")
