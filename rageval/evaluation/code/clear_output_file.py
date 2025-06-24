import argparse
import json, shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
from metrics import get_metric

def clear_output_file(output_file):
    output_path =  Path(output_file)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 清空文件夹内容（保留文件夹结构）
    for item in output_dir.iterdir():
        if item.is_file():
            item.unlink()  # 删除文件
        elif item.is_dir():
            shutil.rmtree(item)  # 递归删除子目录
                
            
def main():
    parser = argparse.ArgumentParser(description="Process JSONL file and evaluate completeness.")
    
    parser.add_argument("--output_file", help="Path to the output JSONL file")

    args = parser.parse_args()
    
    clear_output_file(args.output_file)

if __name__ == "__main__":
    main()