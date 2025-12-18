from typing import Any

def search_medical_records(query: str, retriever: Any, top_k: int = 3, similarity_threshold: float = 0.5) -> str:
    """
    Search the patient's medical records/reports for specific information.
    
    This function is intended for students to implement/modify.
    
    Args:
        query: The question or keyword to search for in the reports.
        retriever: The initialized vector retriever object to use for searching.
        top_k: The number of top results to retrieve.
        similarity_threshold: The threshold for filtering irrelevant results. It would be better to set a lower threshold(like 0.2-0.4) to get more results.
        
    Returns:
        str: A string containing the combined relevant information found, 
             or a message indicating no records were found.
    """
    try:
        # =======================================================
        # TODO: TASK 3
        # 提示：
        # 1. 使用 retriever检索
        # 2. 处理返回结果：
        #    - 过滤掉 "No suitable information retrieved" 的结果
        #    - 提取 text 字段
        # 3. 如果有有效结果，用换行符连接返回；否则返回 "未找到相关记录。"
        # 可参考：https://docs.camel-ai.org/key_modules/retrievers
        # =======================================================
        
        # print("Warning: search_medical_records not implemented.")
        # return "TODO: 请实现 search_medical_records 函数 (src/core/tools.py)"

        # 参考思路:
        results = retriever.query(query, top_k=top_k, similarity_threshold=similarity_threshold)
        
        if not results:
            return "未找到相关记录。"
        
        valid_results = []
        for r in results:
            text = r.get('text', '')
            # Filter out generic empty messages if any
            if "No suitable information retrieved" in text:
                continue
            valid_results.append(text)
        
        if not valid_results:
            return "未找到相关记录。"
            
        return "\n\n".join(valid_results)

        
    except Exception as e:
        return f"查询出错: {str(e)}"
