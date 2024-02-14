#!/bin/bash

sudo docker run \
    -v .:/checks \
    -v /checks-ocr/images:/checks-ocr/images \
    -e TEXTRACT_AWS_ACCESS_KEY_ID="$TEXTRACT_AWS_ACCESS_KEY_ID" \
    -e TEXTRACT_AWS_REGION="$TEXTRACT_AWS_REGION" \
    -e TEXTRACT_AWS_SECRET_ACCESS_KEY="$TEXTRACT_AWS_SECRET_ACCESS_KEY" \
    checks-ocr
