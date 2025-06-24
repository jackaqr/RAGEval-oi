import json

# 原始 JSONL 文件路径
input_path = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/data/dify_rag_result4.jsonl"
# 修改后的输出文件路径
output_path = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/data/dify_rag_result4_en.jsonl"

with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
    for line in infile:
        # 去除可能存在的换行符
        line = line.strip()
        if not line:
            continue  # 跳过空行
        
        try:
            # 解析为 Python 对象
            data = json.loads(line)
            # 将对象转为字符串（中文逗号通常出现在字符串中）
            json_str = json.dumps(data, ensure_ascii=False)
            # 替换中文逗号为英文逗号
            json_str = json_str.replace("，", ",")
            # 写入文件
            outfile.write(json_str + '\n')
        except json.JSONDecodeError as e:
            print(f"跳过无法解析的行: {line}\n错误: {e}")
