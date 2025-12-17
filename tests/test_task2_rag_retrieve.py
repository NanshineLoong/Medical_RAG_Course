import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.rag import get_retrieval_results

class TestTask2RetrievalQuery(unittest.TestCase):
    def test_get_results(self):
        """测试 get_retrieval_results 是否正确调用 query"""
        
        # Mock Retriever
        mock_retriever = MagicMock()
        expected_results = [{'text': 'result1'}, {'text': 'result2'}]
        mock_retriever.query.return_value = expected_results
        
        query_text = "test query"
        top_k = 5
        threshold = 0.7
        
        # Run student code
        results = get_retrieval_results(mock_retriever, query_text, threshold, top_k)
        
        # Check if NotImplemented
        if not results and mock_retriever.query.call_count == 0:
             self.fail("任务2未完成: 未调用 retriever.query")
        
        # Verify Call
        mock_retriever.query.assert_called_once_with(
            query=query_text,
            top_k=top_k,
            similarity_threshold=threshold
        )
        
        # Verify Return
        self.assertEqual(results, expected_results)
        
        print("✅ 任务 2 测试通过！")

if __name__ == '__main__':
    unittest.main()

