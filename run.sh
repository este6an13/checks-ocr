#!/bin/bash

# Set default values for arguments
UPDATE=()
MODEL_NAME=""
LLM=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --update)
            UPDATE+=("$2")
            shift
            ;;
        --model-name)
            MODEL_NAME="$2"
            shift
            ;;
        --llm)
            LLM="--llm"
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Run the Docker command
sudo docker run \
    -v .:/checks \
    -v /checks-ocr/images:/checks-ocr/images \
    -v checks-ocr-vectordb:/checks-ocr/src/llm/vectordb \
    -v checks-ocr-llm-cache:/checks-ocr/src/llm/cache \
    -v checks-ocr-tecxtract-cache:/checks-ocr/cache \
    -v checks-ocr-data:/checks-ocr/data/data \
    checks-ocr $LLM "${UPDATE[@]}" --model-name="$MODEL_NAME"
