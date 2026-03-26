# Use the official Python 3.12 image.
FROM python:3.12-slim

# Install OpenJDK for Apache Tika and Tesseract for OCR
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    tesseract-ocr \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# The Functions Framework uses a different entrypoint
ENTRYPOINT ["functions-framework", "--target=ocr_extraction_func", "--port=8080"]