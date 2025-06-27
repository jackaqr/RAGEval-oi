import json
from pathlib import Path

def reorder_fields(jsonl_file, output_file=None):
    """
    遍历JSONL文件并将每行最后一个字段移到最前面
    
    Args:
        jsonl_file: 输入的JSONL文件路径
        output_file: 输出文件路径，默认为在原文件名后添加_reordered后缀
    """
    # 处理输出文件路径
    if output_file is None:
        jsonl_path = Path(jsonl_file)
        output_file = str(jsonl_path.with_name(f"{jsonl_path.stem}_reordered{jsonl_path.suffix}"))
    
    # 打开输入和输出文件
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        line_count = 0
        
        # 逐行处理JSONL文件
        for line in infile:
            line_count += 1
            
            try:
                # 解析JSON对象
                data = json.loads(line.strip())
                
                # 如果数据为空或没有字段，直接写入原行
                if not data:
                    outfile.write(line + '\n')
                    continue
                
                # 获取所有字段并分离最后一个字段
                keys = list(data.keys())
                last_field = keys[-1]
                last_value = data.pop(last_field)
                
                # 创建新的有序字典，将最后一个字段放在最前面
                reordered_data = {last_field: last_value}
                for key in keys[:-1]:
                    reordered_data[key] = data[key]
                
                # 将处理后的JSON对象写入输出文件
                outfile.write(json.dumps(reordered_data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError:
                print(f"警告: 第{line_count}行不是有效的JSON格式，已跳过")
            except Exception as e:
                print(f"处理第{line_count}行时发生错误: {str(e)}")
    
    print(f"处理完成! 共处理{line_count}行，结果已保存至: {output_file}")

import json
from pathlib import Path

def filter_and_reorder_fields_simple(jsonl_file, output_file=None):
    if output_file is None:
        p = Path(jsonl_file)
        output_file = p.with_name(f"{p.stem}_filtered_reordered{p.suffix}")

    with open(jsonl_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        # 给jsonl文件按照query中的query id 排序，排序之后再把最后一个字段放到最前面 
        lines = infile.readlines()
        lines.sort(key=lambda x: json.loads(x)['query']['query_id'])
        for line in lines:
            data = json.loads(line.strip())
            keys = list(data.keys())
            last_key = keys[-1]
            final_data = {last_key: data[last_key]}
            final_data.update(data)
            outfile.write(json.dumps(final_data, ensure_ascii=False) + '\n')


    print(f"处理完成，结果已保存至：{output_file}")
if __name__ == "__main__":
    # 直接在代码中定义文件路径
    input_file = '/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/result/dify_native/k10_s0.25/internal_result/k10_s0.25_recovered_precision_intermediate.jsonl'
    output_file = '/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/result/dify_native/k10_s0.25/internal_result/k10_s0.25_recovered_precision_intermediate_reordered.jsonl'
    
    # 调用处理函数
    filter_and_reorder_fields_simple(input_file, output_file)