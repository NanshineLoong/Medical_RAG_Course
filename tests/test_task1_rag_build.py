import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.rag import build_retriever_from_files

class TestTask1RetrievalBuild(unittest.TestCase):
    def test_build_retriever(self):
        """测试 build_retriever_from_files 是否正确初始化 retriever 并处理文件"""
        
        # Mocks
        mock_embedding = MagicMock()
        mock_storage = MagicMock()
        mock_retriever_cls = MagicMock()
        
        # Mock file paths
        file_paths = ["/tmp/file1.txt", "/tmp/file2.txt"]
        
        # Use patch to intercept VectorRetriever creation inside the function? 
        # Or passing real objects is fine since they are just objects.
        # The function creates a VectorRetriever(embedding_model, storage).
        # We need to mock VectorRetriever class, but it is imported inside rag.py.
        # We can pass mocks as arguments, but the VectorRetriever class instantiation happens inside.
        # Actually, looking at the code:
        # retriever = VectorRetriever(embedding_model=embedding_model, storage=storage)
        # So we need to patch 'src.core.rag.VectorRetriever'
        
        with unittest.mock.patch('src.core.rag.VectorRetriever') as MockRetrieverClass:
            mock_retriever_instance = MockRetrieverClass.return_value
            
            # Run student code
            result = build_retriever_from_files(mock_embedding, mock_storage, file_paths)
            
            # Check if NotImplemented
            if result is None:
                self.fail("任务1未完成: 函数返回了 None，请实现 build_retriever_from_files")
            
            # Verify Initialization
            MockRetrieverClass.assert_called_once_with(
                embedding_model=mock_embedding,
                storage=mock_storage
            )
            
            # Verify Processing
            
            processed_contents = []
            for call in mock_retriever_instance.process.call_args_list:
                # 获取 content 参数，支持位置参数和关键字参数
                args, kwargs = call
                content = kwargs.get('content')
                if content is None and len(args) > 0:
                    content = args[0]
                
                if content:
                    if isinstance(content, list):
                        processed_contents.extend(content)
                    else:
                        processed_contents.append(content)
            
            for file_path in file_paths:
                self.assertIn(file_path, processed_contents, f"文件 {file_path} 未被 retriever.process 处理")
            
            
            print("✅ 任务 1 测试通过！")

if __name__ == '__main__':
    unittest.main()
