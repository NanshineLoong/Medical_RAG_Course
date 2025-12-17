from enum import Enum
from typing import Dict, Any, List, Optional
import streamlit as st

# Camel Imports
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelPlatformType
from camel.models import ModelFactory
from camel.toolkits import FunctionTool


# Project Imports
from src.core.tools import search_medical_records

class SimulationStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"

class AgentManager:
    """Manages the lifecycle and interaction of Doctor and Patient agents."""
    
    def __init__(self):
        self.doctor_agent = None
        self.patient_agent = None
        self.status = SimulationStatus.IDLE
        self.chat_history: List[Dict[str, str]] = []
        self.max_steps = 10
        self.current_step = 0

    def _create_camel_model(self, model_config):
        """Helper to create Camel Model instance."""
        return ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI, # Assuming OpenAI compatible
            model_type=model_config.model_name or "qwen-plus", # Default fallback
            url=model_config.base_url,
            api_key=model_config.api_key,
            model_config_dict={"temperature": model_config.temperature}
        )

    def initialize_agents(self, patient_profile: str, doctor_instruction: str, model_config: Any, rag_content: str = "", max_steps: int = 10):
        """
        Initialize both agents with provided profiles and instructions.
        """
        self.status = SimulationStatus.RUNNING
        self.chat_history = []
        self.current_step = 0
        self.max_steps = max_steps
        
        # 1. Setup RAG Tool for Doctor
        doctor_tools = []
        if rag_content:
            if 'rag_manager' in st.session_state:
                retriever = st.session_state.rag_manager.create_temporary_retriever(rag_content)
                
                if retriever:
                    def rag_tool_wrapper(query: str, top_k: int = 3, similarity_threshold: float = 0.5) -> str:
                        """
                        Search the patient's medical records/reports for specific information.
                        Args:
                            query: The question or keyword to search for in the reports.
                            top_k: Number of results to return (default: 3).
                            similarity_threshold: Threshold for relevance. It would be better to set a lower threshold(like 0.2-0.4) to get more results.
                        """
                        return search_medical_records(query, retriever, top_k=top_k, similarity_threshold=similarity_threshold)

                    rag_tool = FunctionTool(rag_tool_wrapper)
                    doctor_tools.append(rag_tool)

        # 2. Create Models
        model_instance = self._create_camel_model(model_config)

        # 3. Create Doctor Agent
        doctor_sys_content = doctor_instruction
        if rag_content:
            doctor_sys_content += "\n\n你可以使用 search_medical_records 方法查询病历信息。请只通过工具查找信息。如果没有工具或工具查不到，请根据病人描述判断。"
        
        doctor_sys_msg = BaseMessage.make_assistant_message(
            role_name="Doctor",
            content=doctor_sys_content
        )
        self.doctor_agent = ChatAgent(
            system_message=doctor_sys_msg,
            model=model_instance,
            tools=doctor_tools,
        )

        # 4. Create Patient Agent
        patient_sys_msg = BaseMessage.make_assistant_message(
            role_name="Patient",
            content=f"请扮演一名病人，根据提供的 {patient_profile} 回答医生的问题。只回答你知道的内容，不知道就说不知道。使用自然、口语化的中文，每次回复 2–3 句话，不用医学术语，也不要提及任何档案或资料，只描述身体感受。"
        )
        self.patient_agent = ChatAgent(
            system_message=patient_sys_msg,
            model=model_instance
        )

    def generate_opening_message(self, starter_role: str) -> Optional[Dict[str, Any]]:
        """
        Generate the first message of the conversation based on who starts.
        If starter_role is 'Patient', the patient speaks first (e.g. complaint).
        If starter_role is 'Doctor', the doctor speaks first (e.g. inquiry).
        """
        if starter_role == "Patient":

            prompt = "请你向医生描述你的主诉和不适症状，作为开场白。"
            role_name = "Patient"
            agent = self.patient_agent
        else:
            # Doctor starts: Simulate them asking for the patient
            # Increment step for Doctor's first turn
            self.current_step = 1
            prompt = f"病人已就诊。请开始你的问诊。\n\n[System Note: 已问诊轮次 {self.current_step}/{self.max_steps}]"
            role_name = "Doctor"
            agent = self.doctor_agent
            
        try:
            user_msg = BaseMessage.make_user_message(role_name="User", content=prompt)
            response = agent.step(user_msg)
            content = response.msg.content or ""
            
            message = {
                "role": role_name,
                "content": content,
            }
            self.chat_history.append(message)
            return message
            
        except Exception as e:
            st.error(f"Failed to generate opening message: {e}")
            return None

    def step_simulation(self) -> Optional[Dict[str, Any]]:
        """
        Execute one step of the simulation (non-streaming).
        """
        if self.status != SimulationStatus.RUNNING:
            return None
        
        # If history is empty, default to Doctor starting if not handled
        if not self.chat_history:
             # Fallback: Doctor starts
             return self.generate_opening_message("Doctor")

        last_role = self.chat_history[-1]["role"]

        if last_role in ("Patient", "system"):
            current_agent = self.doctor_agent
            role_name = "Doctor"
            last_content = self.chat_history[-1]["content"]
            
            # Increment step for Doctor's turn
            self.current_step += 1
            # Inject turn info
            last_content = f"{last_content}\n\n[System Note: 当前轮次 {self.current_step}/{self.max_steps}]"
            
        else:
            current_agent = self.patient_agent
            role_name = "Patient"
            last_content = self.chat_history[-1]["content"]

        user_msg = BaseMessage.make_user_message(role_name="User", content=last_content)

        try:
            response = current_agent.step(user_msg)
        except Exception as exc:
            error_message = {"role": role_name, "content": f"Error: {exc}"}
            self.chat_history.append(error_message)
            return error_message

        content = ""
        if response and getattr(response, "msg", None):
            content = response.msg.content or ""

        if "<DIAGNOSIS_DONE>" in content:
            self.status = SimulationStatus.COMPLETED
            content = content.replace("<DIAGNOSIS_DONE>", "").strip()

        tool_calls_info = []
        info_payload = getattr(response, "info", None)
        if info_payload:
            if isinstance(info_payload, dict):
                tool_calls_info = info_payload.get("tool_calls", []) or []
            elif hasattr(info_payload, "get"):
                tool_calls_info = info_payload.get("tool_calls", []) or []

        message = {
            "role": role_name,
            "content": content,
        }
        if tool_calls_info:
            message["tool_calls"] = tool_calls_info

        self.chat_history.append(message)
        return message

    def send_user_message(self, message: str, role: str):
        """
        Handle user interaction in semi-automatic modes.
        User plays 'role' (e.g. Doctor), so we inject that message into history
        and then let the OTHER agent respond.
        """
        self.chat_history.append({"role": role, "content": message})
        
        # Now trigger the other agent to respond
        # We can just return, and let the UI Call step_simulation logic if it was auto,
        # but here we want an immediate response from the other party.
        
        other_role = "Patient" if role == "Doctor" else "Doctor"
        other_agent = self.patient_agent if other_role == "Patient" else self.doctor_agent
        
        try:
            user_msg = BaseMessage.make_user_message(role_name="User", content=message)
            response = other_agent.step(user_msg)
            content = response.msg.content
            
            if "<DIAGNOSIS_DONE>" in content:
                self.status = SimulationStatus.COMPLETED
                content = content.replace("<DIAGNOSIS_DONE>", "").strip()

            self.chat_history.append({
                "role": other_role,
                "content": content,
                "tool_calls": response.info.get('tool_calls', []) if response.info else []
            })
            
        except Exception as e:
            st.error(f"Response Error: {str(e)}")

    def add_message(self, role: str, content: str):
        """
        Manually add a message to the history without triggering a response.
        Useful for UI rendering immediate user input.
        """
        self.chat_history.append({"role": role, "content": content})
