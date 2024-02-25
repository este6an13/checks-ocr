#!/bin/bash

sudo docker run \
    -v .:/checks \
    -v /checks-ocr/images:/checks-ocr/images \
    -v checks-ocr-vectordb:/checks-ocr/src/llm/vectordb \
    -v checks-ocr-llm-cache:/checks-ocr/src/llm/cache \
    -v checks-ocr-tecxtract-cache:/checks-ocr/cache \
    -v checks-ocr-data:/checks-ocr/data/data \
    -e TEXTRACT_AWS_ACCESS_KEY_ID="$TEXTRACT_AWS_ACCESS_KEY_ID" \
    -e TEXTRACT_AWS_REGION="$TEXTRACT_AWS_REGION" \
    -e TEXTRACT_AWS_SECRET_ACCESS_KEY_ID="$TEXTRACT_AWS_SECRET_ACCESS_KEY_ID" \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    checks-ocr
