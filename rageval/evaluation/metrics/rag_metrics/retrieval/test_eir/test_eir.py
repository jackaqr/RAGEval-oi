import json
import numpy as np
import re
from typing import List
from pysbd import Segmenter

segmenter = Segmenter()

class EIR:
    name: str = "EIR"
    
    def __init__(self, threshold=0.2):
        self.threshold = threshold
    
    def count_words(self, text, language):
        if language == 'zh':
            return len(text)
        else:
            return len(text.split())

    def calculate_eir(self, retrieves, ground_truths, language=None) -> float:
        def split_sentences(text: str, language: str) -> List[str]:
            if language == 'en':
                sentences = segmenter.segment(text)
            elif language == 'zh':
                sentences = re.split(r'(?<=[。！？])\s*|\n', text)
            else:
                raise ValueError("Unsupported language")
            return [s.strip() for s in sentences if s.strip()]

        combined_retrieves = ' '.join([r[0] if isinstance(r, list) else r for r in retrieves])
        matched_word_count = 0
        for gt in ground_truths:
            gt_text = gt[0] if isinstance(gt, list) else gt
            sentences = split_sentences(gt_text, language)
            for sentence in sentences:
                if sentence in combined_retrieves:
                    matched_word_count += self.count_words(sentence, language)

        total_word_count = self.count_words(combined_retrieves, language)
        if matched_word_count == 0 or total_word_count == 0:
            return 0.0
        return matched_word_count / total_word_count

    def __call__(self, doc, language=None) -> float:
        retrieves = [r for r in doc.get("prediction", {}).get("references", [])]
        ground_truths = doc.get("ground_truth", {}).get("references", [])

        new_retrieves = []
        new_ground_truths = []

        for r in retrieves:
            if isinstance(r, list):
                if not r:
                    continue
                r = r[0]
            if r:
                if r.startswith('（'):
                    print("Deleting Metadata in Chinese!")
                    end_pos = r.find('）')
                    if end_pos != -1:
                        r = r[end_pos + 1:]
                elif r.startswith('('):
                    print("Deleting Metadata in English!")
                    end_pos = r.find(')')
                    if end_pos != -1:
                        r = r[end_pos + 1:]
            new_retrieves.append(r)

        for g in ground_truths:
            if isinstance(g, list):
                g = g[0]
            new_ground_truths.append(g)

        if not new_retrieves or not new_ground_truths:
            return 0.0

        return self.calculate_eir(new_retrieves, new_ground_truths, language=language)


if __name__ == "__main__":
    # ✅ 在这里定义路径和语言
    file_path = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/metrics/rag_metrics/retrieval/test_eir/test.json"
    language = "zh"  # 可设为 "en" 或 "zh"

    # 读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 判断是单个对象还是多个对象
    if isinstance(data, list):
        scores = [EIR()(doc, language=language) for doc in data]
        average_score = np.mean(scores)
        print(f"🌟 平均 EIR 分数: {average_score:.4f}")
    else:
        score = EIR()(data, language=language)
        print(f"🌟 EIR 分数: {score:.4f}")
