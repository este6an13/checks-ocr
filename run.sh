#!/bin/bash

# Initialize variables
LLM=""
UPDATE=()
MODEL_NAME=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --llm)
        LLM="--llm"
        shift
        ;;
        --update)
        UPDATE+=("$2")
        shift
        shift
        ;;
        --model-name)
        MODEL_NAME="--model-name $2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Construct --update arguments
UPDATE_ARGS=""
for file in "${UPDATE[@]}"; do
    UPDATE_ARGS="$UPDATE_ARGS --update $file"
done

# Docker run command with parsed arguments
sudo docker run \
    --name "checks-ocr" \
    --rm \
    -v .:/checks \
    -v /checks-ocr/images:/checks-ocr/images \
    -v /data/checks-ocr-vectordb:/checks-ocr/src/llm/vectordb \
    -v /data/checks-ocr-llm-cache:/checks-ocr/src/llm/cache \
    -v /data/checks-ocr-tecxtract-cache:/checks-ocr/cache \
    -v /data/checks-ocr-data:/checks-ocr/data/data \
    -e TEXTRACT_AWS_ACCESS_KEY_ID="$TEXTRACT_AWS_ACCESS_KEY_ID" \
    -e TEXTRACT_AWS_REGION="$TEXTRACT_AWS_REGION" \
    -e TEXTRACT_AWS_SECRET_ACCESS_KEY_ID="$TEXTRACT_AWS_SECRET_ACCESS_KEY_ID" \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    checks-ocr \
    $LLM \
    $UPDATE_ARGS \
    $MODEL_NAME
