# Use official Python 3.12 image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY . .
RUN pip install poetry && poetry install --no-root

# Copy bot files into the container

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app/src"
