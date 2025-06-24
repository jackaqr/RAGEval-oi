#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
过滤 JSONL 行：
1. 若 ground_truth.references 非空且 prediction.references 为空 → 丢弃该行
2. 其余行：对 prediction.references 去重后写入新文件
"""

import json
import re
from typing import Any, List

# ====== 在此处修改文件路径 ======
INPUT_PATH  = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/data/with_p3_en.jsonl"     # 原始文件
OUTPUT_PATH = "/Users/liuxuanzi/Desktop/RAG Benchmark/RAGEval/rageval/evaluation/data/with_p5_en.jsonl"     # 过滤后文件
# =================================

def is_empty_refs(refs: Any) -> bool:
    """判断 references 是否为空：空字符串、空列表、None 都算空"""
    if refs is None:
        return True
    if isinstance(refs, str):
        return refs.strip() == ""
    if isinstance(refs, list):
        return len(refs) == 0
    return False

def dedup_list(seq: List[str]) -> List[str]:
    """保持顺序地去重列表"""
    seen = set()
    deduped = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped

_SPLIT_RE = re.compile(r"[;,，；\n]+")

def dedup_refs(refs: Any) -> Any:
    """
    去重 prediction.references：
    - list: 顺序去重
    - str : 先按分隔符（逗号/分号/换行等）拆分，去重后再用 "; " 拼回
    - 其他类型原样返回
    """
    if is_empty_refs(refs):
        return refs

    # 列表去重
    if isinstance(refs, list):
        return dedup_list(refs)

    # 字符串去重
    if isinstance(refs, str):
        parts = [p.strip() for p in _SPLIT_RE.split(refs) if p.strip()]
        deduped = dedup_list(parts)
        return "; ".join(deduped)

    return refs  # 其余类型（dict 等）保持不变

def should_keep(record: dict) -> bool:
    """True = 保留该行；False = 丢弃"""
    gt_refs   = record.get("ground_truth", {}).get("references", [])
    pred_refs = record.get("prediction",   {}).get("references", [])

    # ground_truth 引用非空 且 prediction 引用为空 → 丢弃
    return not (gt_refs and is_empty_refs(pred_refs))

def filter_and_dedup_jsonl(in_path: str, out_path: str) -> None:
    with open(in_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)

            # 过滤规则
            if not should_keep(record):
                continue

            # 去重 prediction.references
            pred = record.get("prediction", {})
            pred["references"] = dedup_refs(pred.get("references"))
            record["prediction"] = pred

            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    filter_and_dedup_jsonl(INPUT_PATH, OUTPUT_PATH)
    print(f"过滤与去重完成，结果已保存至：{OUTPUT_PATH}")
