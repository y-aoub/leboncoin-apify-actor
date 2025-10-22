# Apify Dockerfile for Leboncoin Universal Scraper
FROM apify/actor-python:3.11

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py ./

# Set the entrypoint
CMD ["python", "-u", "main.py"]

