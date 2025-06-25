import os
import json
import argparse


# 恢复句号的函数
def recover(source: str, s: str) -> str:
    filtered = ""
    idx_map = []
    for i, ch in enumerate(source):
        if ch == "。":
            continue
        idx_map.append(i)
        filtered += ch
    idx = filtered.find(s)
    if idx < 0:
        raise Exception("not found")
    idx = idx_map[idx]
    origin = ""
    j = 0
    for i in range(idx, len(source)):
        if source[i] == "。":
            origin += source[i]
            continue
        j += 1
        if j > len(s):
            break
        origin += source[i]
    return origin


def recover_jsonl(source_folders, input_file, output_file):
    source_files = {}
    for source_folder in source_folders:
        file_names = os.listdir(source_folder)
        files_only = [
            f for f in file_names if os.path.isfile(os.path.join(source_folder, f))
        ]
        for file_name in files_only:
            source_files[file_name] = source_folder

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            data = json.loads(line)

            references_res = []

            for ref in data["prediction"]["references"]:
                title = os.path.basename(
                    ref.get("title")
                )  # "doc/0/公司年报_环保_0.txt" --> 公司年报_环保_0.txt
                raw_content = ref.get("content", "").replace("\n", "").replace("\r", "")

                if not title or not raw_content or title not in source_files:
                    continue

                source_folder = source_files[title]
                src_path = os.path.join(source_folder, title)
                with open(src_path, "r", encoding="utf-8") as sf:
                    source_text = sf.read().replace("\n", "")
                try:
                    restored = recover(source_text, raw_content)
                    references_res.append(restored)
                    data["prediction"]["references"] = references_res
                except Exception as e:
                    print(f"[!] 恢复失败（{title}）：{raw_content[:40]}...")
                    raise e

            f.write(json.dumps(data, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recover file.")
    parser.add_argument("--input_file", help="Path to the input JSONL file")
    parser.add_argument("--output_file", help="Path to the output JSONL file")
    args = parser.parse_args()

    source_folders = [
        "../qar_generation/data/finance/zh/doc/0",
        "../qar_generation/data/finance/zh/doc/1",
    ]  # 源本文目录
    recover_jsonl(source_folders, args.input_file, args.output_file)
