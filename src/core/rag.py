import os
from typing import List, Optional, Dict, Any
import streamlit as st

from camel.embeddings import OpenAICompatibleEmbedding
from camel.storages import QdrantStorage
from camel.retrievers import VectorRetriever

# Helper functions for Student Exercises
# Students will focus on understanding/implementing logic within these boundaries.

def build_retriever_from_files(
    embedding_model: OpenAICompatibleEmbedding,
    storage: QdrantStorage,
    file_paths: List[str]
) -> Optional[VectorRetriever]:
    """
    Construct a retriever and process the given files.
    
    Args:
        embedding_model: The initialized embedding model.
        storage: The initialized storage backend.
        file_paths: List of absolute paths to the files that need to be indexed.
        
    Returns:
        VectorRetriever: The fully initialized and indexed retriever.
    """
    # =======================================================
    # TODO: TASK 1
    # 提示：
    # 1. 初始化 VectorRetriever
    # 2. 遍历 file_paths 列表，注意 retriever 在处理文件时 batch 需要设为 10。
    #    参考： https://help.aliyun.com/zh/model-studio/embedding-interfaces-compatible-with-openai
    # 3. 返回初始化好的 retriever
    # 可参考：https://docs.camel-ai.org/key_modules/retrievers
    # =======================================================
    
    print("Warning: build_retriever_from_files not implemented.")
    return None


def get_retrieval_results(
    retriever: VectorRetriever, 
    query: str, 
    threshold: float = 0.5, 
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Execute a query against the retriever and return raw results.
    
    Args:
        retriever: The initialized VectorRetriever.
        query: The user's query string.
        threshold: Similarity threshold (0.0 to 1.0).
        top_k: Number of top results to return.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries returned by the retriever.
    """
    if not retriever:
        return []

    # =======================================================
    # TODO: TASK 2
    # 任务：调用 retriever 的 query 方法获取结果
    # =======================================================
    
    print("Warning: get_retrieval_results not implemented.")
    return []


def format_retrieval_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and format the raw results from the retriever.
    Removes invalid entries and formats similarity scores.
    """
    valid_results = []
    for res in results:
        text = res.get('text', '')
        if "No suitable information retrieved" in text:
            continue
        
        similarity_raw = res.get('similarity score', 0.0)
        similarity = float(similarity_raw) if similarity_raw is not None else 0.0
        
        valid_results.append({
            'text': text,
            'similarity': similarity
        })
        
    return valid_results


class RAGManager:
    """Manages document ingestion and retrieval for RAG using Camel AI."""
    
    def __init__(self, base_path: str = "local_data"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
        self.documents = []
        self.vector_store_status = "Not Initialized"
        self.retriever = None
        self.storage = None
        self.current_kb_name = None

    def _get_embedding_model(self):
        """Helper to create embedding model based on session config."""
        # Check if config exists in session state, otherwise use defaults or fail gracefully
        if hasattr(st.session_state, 'model_config'):
            api_key = st.session_state.model_config.api_key
            base_url = st.session_state.model_config.base_url
        else:
            # Fallback for testing without Streamlit context if needed
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "")

        return OpenAICompatibleEmbedding(
            model_type="text-embedding-v4",
            api_key=api_key,
            url=base_url
        )

    def list_knowledge_bases(self) -> List[str]:
        """List available knowledge bases (subdirectories in local_data)."""
        if not os.path.exists(self.base_path):
            return []
        return [d for d in os.listdir(self.base_path) 
                if os.path.isdir(os.path.join(self.base_path, d))]

    def load_knowledge_base(self, kb_name: str) -> bool:
        """Load an existing knowledge base from disk."""
        kb_path = os.path.join(self.base_path, kb_name)
        if not os.path.exists(kb_path):
            return False
            
        try:
            embedding_model = self._get_embedding_model()
            
            # Use local path for persistence
            self.storage = QdrantStorage(
                vector_dim=embedding_model.get_output_dim(),
                collection_name="expert_qa_kb",
                path=kb_path
            )
            
            self.retriever = VectorRetriever(
                embedding_model=embedding_model, 
                storage=self.storage
            )
            
            self.current_kb_name = kb_name
            self.vector_store_status = f"✅ 已加载知识库: {kb_name}"
            return True
        except Exception as e:
            self.vector_store_status = f"❌ 加载失败: {str(e)}"
            return False

    def process_files(self, kb_name: str, uploaded_files: List[Any]) -> str:
        """
        Process uploaded files, save them to local folder, and update vector store.
        DELEGATES core logic to build_retriever_from_files.
        """
        if not uploaded_files or not kb_name:
            return "❌ 请提供知识库名称和文件"
            
        # Create separate directory for this KB
        kb_path = os.path.join(self.base_path, kb_name)
        if not os.path.exists(kb_path):
            os.makedirs(kb_path)
        
        try:
            # 1. Initialize Components
            embedding_model = self._get_embedding_model()
            
            self.storage = QdrantStorage(
                vector_dim=embedding_model.get_output_dim(),
                collection_name="expert_qa_kb",
                path=kb_path
            )
            
            # 2. Save files locally first (System responsibility)
            file_paths = []
            file_names = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(kb_path, uploaded_file.name)
                # uploaded_file is a streamlit UploadedFile object
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
                file_names.append(uploaded_file.name)
            
            # 3. Build Retriever (STUDENT EXERCISE DELEGATION)
            self.retriever = build_retriever_from_files(
                embedding_model=embedding_model,
                storage=self.storage,
                file_paths=file_paths
            )
            
            self.documents = file_names
            self.current_kb_name = kb_name
            self.vector_store_status = f"✅ 已创建并索引知识库: {kb_name} ({len(file_names)} 文件)"
            return self.vector_store_status

        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
            return "处理失败"

    def retrieve(self, query: str, threshold: float, top_k: int) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document context based on query.
        DELEGATES core logic to get_retrieval_results.
        """
        try:
            # Student returns raw results
            raw_results = get_retrieval_results(self.retriever, query, threshold, top_k)
            # System formats them
            return format_retrieval_results(raw_results)
        except Exception as e:
            print(f"Retrieval error: {e}")
            error_message = f"检索失败: {str(e)}"
            return [{
                'text': error_message,
                'similarity': 0.0
            }]

    def create_temporary_retriever(self, text_content: str) -> Optional[VectorRetriever]:
        """
        Creates a standalone retriever for a specific text block (e.g. Simulation Mode).
        Uses in-memory storage.
        """
        if not text_content or not text_content.strip():
            return None
            
        try:
            embedding_model = self._get_embedding_model()
            
            storage = QdrantStorage(
                vector_dim=embedding_model.get_output_dim(),
                collection_name="temp_sim_kb",
                path=":memory:"
            )
            
            retriever = VectorRetriever(
                embedding_model=embedding_model,
                storage=storage
            )
            
            retriever.process(content=text_content)
            return retriever
        except Exception as e:
            print(f"Temp retriever creation failed: {e}")
            return None
