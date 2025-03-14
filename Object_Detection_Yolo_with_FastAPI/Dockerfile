# Use the Python image
FROM python:3.10

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1

# Copy application files into the Docker image
COPY . /app

# Specify the directory where the application will run
WORKDIR /app

# Install necessary Python packages
RUN pip install -r requirements.txt

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
