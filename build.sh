#!/bin/bash

sudo docker build \
    --secret id=TEXTRACT_AWS_ACCESS_KEY_ID,env=TEXTRACT_AWS_ACCESS_KEY_ID \
    --secret id=TEXTRACT_AWS_REGION,env=TEXTRACT_AWS_REGION \
    --secret id=TEXTRACT_AWS_SECRET_ACCESS_KEY_ID,env=TEXTRACT_AWS_SECRET_ACCESS_KEY_ID \
    --secret id=OPENAI_API_KEY,env=OPENAI_API_KEY \
    -t checks-ocr \
    checks-ocr/
