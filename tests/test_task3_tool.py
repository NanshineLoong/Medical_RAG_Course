import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.tools import search_medical_records

class TestTask3ToolImplementation(unittest.TestCase):
    def test_search_tool_success(self):
        """测试 search_medical_records 成功查找到信息的情况"""
        
        mock_retriever = MagicMock()
        # Simulate Camel retriever results
        mock_retriever.query.return_value = [
            {'text': 'Patient has high blood pressure.', 'similarity score': 0.8},
            {'text': 'No suitable information retrieved', 'similarity score': 0.1}, # Should be filtered
            {'text': 'Patient is 45 years old.', 'similarity score': 0.7}
        ]
        
        result = search_medical_records("history", mock_retriever, top_k=2, similarity_threshold=0.6)
        
        # Check for implementation
        if "TODO" in result and "Patient" not in result:
             self.fail("任务3未完成: 函数返回了 TODO 提示")
             
        # Verify logic
        self.assertIn("Patient has high blood pressure.", result)
        self.assertIn("Patient is 45 years old.", result)
        self.assertNotIn("No suitable information retrieved", result)
        
        # Verify args passed to retriever
        mock_retriever.query.assert_called_with("history", top_k=2, similarity_threshold=0.6)
        
        print("✅ 任务 3 (成功查找) 测试通过！")

    def test_search_tool_empty(self):
        """测试 search_medical_records 未查找到信息的情况"""
        mock_retriever = MagicMock()
        mock_retriever.query.return_value = []
        
        result = search_medical_records("random", mock_retriever)
        
        self.assertIn("未找到相关记录", result)
        print("✅ 任务 3 (空结果) 测试通过！")

if __name__ == '__main__':
    unittest.main()

