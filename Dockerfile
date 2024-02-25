FROM python

# Creates checks folder
WORKDIR /checks

# Creates checks-ocr folder inside checks folder
WORKDIR /checks/checks-ocr

# Copy requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Creates unprocessed folder inside checks folder
WORKDIR /checks/unprocessed

# Creates processed folder inside checks folder
WORKDIR /checks/processed

# Copy repository files to image checks-ocr folder
COPY . .

# Move to src folder
WORKDIR /checks/checks-ocr/src

# Start the application
ENTRYPOINT ["python3", "main.py"]
