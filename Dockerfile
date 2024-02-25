FROM python

# Creates checks folder
WORKDIR /checks

# Creates unprocessed folder inside checks folder
WORKDIR /checks/unprocessed

# Creates processed folder inside checks folder
WORKDIR /checks/processed

# Creates checks-ocr folder inside checks folder
WORKDIR /checks/checks-ocr

# Copy repository files to image checks-ocr folder
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Move to src folder
WORKDIR /checks/checks-ocr/src

RUN --mount=type=secret,id=TEXTRACT_AWS_ACCESS_KEY_ID \
    TEXTRACT_AWS_ACCESS_KEY_ID=$TEXTRACT_AWS_ACCESS_KEY_ID

RUN --mount=type=secret,id=TEXTRACT_AWS_REGION \
    TEXTRACT_AWS_REGION=$TEXTRACT_AWS_REGION

RUN --mount=type=secret,id=TEXTRACT_AWS_SECRET_ACCESS_KEY_ID \
    TEXTRACT_AWS_SECRET_ACCESS_KEY_ID=$TEXTRACT_AWS_SECRET_ACCESS_KEY_ID

RUN --mount=type=secret,id=OPENAI_API_KEY \
    OPENAI_API_KEY=$OPENAI_API_KEY

# Start the application
CMD ["python3", "main.py"]
