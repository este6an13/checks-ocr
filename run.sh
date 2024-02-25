#!/bin/bash

sudo docker run \
    -v .:/checks \
    -v /checks-ocr/images:/checks-ocr/images \
    -v checks-ocr-vectordb:/checks-ocr/src/llm/vectordb \
    -v checks-ocr-llm-cache:/checks-ocr/src/llm/cache \
    -v checks-ocr-tecxtract-cache:/checks-ocr/cache \
    -v checks-ocr-data:/checks-ocr/data/data \
    checks-ocr
