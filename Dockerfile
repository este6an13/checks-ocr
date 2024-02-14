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

# Start the application
CMD ["python3", "main.py"]
