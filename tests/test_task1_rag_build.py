import unittest
from unittest.mock import MagicMock, mock_open, patch
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
        
        # Mock file paths
        file_paths = ["/tmp/file1.txt", "/tmp/file2.txt"]
        
        # Mock file contents
        mock_file_contents = {
            "/tmp/file1.txt": "这是文件1的内容",
            "/tmp/file2.txt": "这是文件2的内容"
        }
        
        # Mock open function to simulate file reading
        def side_effect(file_path, *args, **kwargs):
            # Return appropriate content based on file path
            content = mock_file_contents.get(file_path, "")
            m = mock_open(read_data=content)
            return m(file_path, *args, **kwargs)
        
        with patch('src.core.rag.VectorRetriever') as MockRetrieverClass, \
             patch('builtins.open', side_effect=side_effect):
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
            
            # Verify that process was called for each file
            # Note: process might be called with file_path or file_content, both are acceptable
            self.assertEqual(
                mock_retriever_instance.process.call_count,
                len(file_paths),
                f"process 方法应该被调用 {len(file_paths)} 次，但实际调用了 {mock_retriever_instance.process.call_count} 次"
            )
            
            # Verify embed_batch parameter
            for call in mock_retriever_instance.process.call_args_list:
                kwargs = call.kwargs
                self.assertEqual(
                    kwargs.get('embed_batch'),
                    10,
                    "process 方法应该使用 embed_batch=10 参数"
                )
            
            print("✅ 任务 1 测试通过！")

if __name__ == '__main__':
    unittest.main()
