import json
from pathlib import Path
import requests
import time

def load_qar_data(domain: str = "finance", language: str = "zh"):
    """加载QAR数据"""
    qar_dir = Path(f"RAGEval/rageval/qar_generation/output/{domain}/{language}/config")
    qar_data = []
    
    # 读取所有JSON文件
    for json_file in qar_dir.glob("**/*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 提取QAR数据
            if 'qa_fact_based' in data:
                for qa in data['qa_fact_based']:
                    qar_data.append({
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'reference': qa.get('reference', ''),
                        'source': str(json_file)
                    })
    return qar_data

def evaluate_rag_system(webui_url: str, qar_data: list):
    """评估RAG系统"""
    results = []
    
    for item in qar_data:
        # 调用你的RAG系统
        response = requests.post(
            f"{webui_url}/v1/chat/completions",
            json={
                "model": "your-model-name",
                "messages": [
                    {
                        "role": "system",
                        "content": f"Context: {item['reference']}\n\n请基于以上上下文回答问题。"
                    },
                    {
                        "role": "user",
                        "content": item['question']
                    }
                ]
            }
        )
        
        # 记录结果
        results.append({
            'question': item['question'],
            'reference': item['reference'],
            'gold_answer': item['answer'],
            'system_answer': response.json()['choices'][0]['message']['content'],
            'source': item['source']
        })
        
        time.sleep(1)  # 避免请求过快
    
    return results

def main():
    # 加载QAR数据
    qar_data = load_qar_data(domain="finance", language="zh")
    
    # 评估RAG系统
    results = evaluate_rag_system(
        webui_url="http://localhost:8000",  # 你的Open WebUI地址
        qar_data=qar_data
    )
    
    # 保存结果
    with open('evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()