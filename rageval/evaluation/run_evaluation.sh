#!/bin/bash

# Parameters
NUM_WORKERS=50 # the number of workers to use for parallel processing for evaluation
LANGUAGE="zh" # the language of the input data, en or zh
INPUT_BASE_URL="data"
USE_MODEL="qwen2.5-7b-instruct-1m"

# PROJECT_NAME="ragflow" # 可以设置一个默认的如benchmark，或者需要就搞个项目的
PROJECT_NAME="chatwiki" # 可以设置一个默认的如benchmark，或者需要就搞个项目的
OUTPUT_BASE_URL="result/${PROJECT_NAME}/internal_result"

FINAL_OUTPUT_FILE="result/${PROJECT_NAME}/final_result.json"

export OPENAI_API_KEY="sk-7a8ce4510f6e413b982cd7b6c73609a4"
export BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1" # if none, set to empty string
# Input files and output file list 
INPUT_FILES=("/${PROJECT_NAME}.jsonl") # file name of the input data

KEYPOINT_VERSION="v3" # default version of the paper

# List of metrics to process
METRICS=( "rouge-l" "precision" "recall" "eir" "keypoint_metrics")   # 

# Function: Get line count of a file
get_line_count() {
    local file=$1
    if [[ -f "$file" ]]; then
        wc -l < "$file"
    else
        echo 0
    fi
}

# 默认不强制删除
FORCE_DELETE_INTERNAL=false

# 解析命令行参数
# 强制删除intermediate.jsonl 文件
for arg in "$@"; do
  if [[ "$arg" == "--force" ]]; then
    FORCE_DELETE_INTERNAL=true
  fi
done


# Process each metric for each input file
for INPUT_FILE in "${INPUT_FILES[@]}"; do
    FULL_INPUT_ORIGIN_PATH="${INPUT_BASE_URL}${INPUT_FILE}"
    FULL_INPUT_PATH="${INPUT_BASE_URL}${INPUT_FILE%.*}_recover.jsonl"

    # Recover the input file
    python recover.py --input_file $FULL_INPUT_ORIGIN_PATH --output_file $FULL_INPUT_PATH

    echo "Processing file: $FULL_INPUT_PATH"

    for METRIC in "${METRICS[@]}"; do
        OUTPUT_FILE="${INPUT_FILE%.*}_${METRIC}_intermediate.jsonl"
        FULL_OUTPUT_PATH="${OUTPUT_BASE_URL}${OUTPUT_FILE}"

        if $FORCE_DELETE_INTERNAL; then
            echo "强制删除: ${FULL_OUTPUT_PATH}"
            rm -f "${FULL_OUTPUT_PATH}"
        else
            echo "不删除文件（无 --force）: ${FULL_OUTPUT_PATH}"
        fi

        # Check if input file exists
        if [[ ! -f "$FULL_INPUT_PATH" ]]; then
            echo "Error: Input file $FULL_INPUT_PATH does not exist."
            exit 1
        fi
        echo "Processing metric: $METRIC"
        echo "Output file: $FULL_OUTPUT_PATH"

        # Set USE_OPENAI based on the metric
        if [[ "$METRIC" == "keypoint_metrics" ]]; then
            USE_OPENAI="--use_openai"
            VERSION="$KEYPOINT_VERSION"
        else
            USE_OPENAI=""
            USE_MODEL=""
            VERSION=""
        fi

        # Initial line counts
        input_line_count=$(get_line_count "$FULL_INPUT_PATH")
        output_line_count=$(get_line_count "$FULL_OUTPUT_PATH")

        # Run Python script until line counts match
        while [[ "$input_line_count" -ne "$output_line_count" ]]; do
            echo "Processing $FULL_INPUT_PATH for metric $METRIC..."
            python main.py --input_file "$FULL_INPUT_PATH" --output_file "$FULL_OUTPUT_PATH" --num_workers $NUM_WORKERS --metric "$METRIC" --language "$LANGUAGE" $USE_OPENAI --model "$USE_MODEL" --version "$VERSION"
            
            # Get updated line counts
            input_line_count=$(get_line_count "$FULL_INPUT_PATH")
            output_line_count=$(get_line_count "$FULL_OUTPUT_PATH")
            
            if [[ "$input_line_count" -ne "$output_line_count" ]]; then
                echo "Line counts do not match for $FULL_INPUT_PATH ($METRIC). Waiting for 3 minutes before retrying..."
                sleep 180
            fi
        done

        echo "Processing complete for $FULL_INPUT_PATH ($METRIC). Input and output line counts match."
    done
done

echo "All files and metrics processed."

python process_intermediate.py --folder_path $OUTPUT_BASE_URL --output_file $FINAL_OUTPUT_FILE

echo "Intermediate results processed. Results are stored in $OUTPUT_BASE_URL"

