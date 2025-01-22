# Base image with Python 3.10
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for dlib and other packages
RUN apt-get update && apt-get install -y \
    build-essential cmake pkg-config \
    python3.10 python3.10-dev python3.10-venv &&
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libx264-dev \
    libblas-dev liblapack-dev gfortran libatlas-base-dev \
    libssl-dev libcurl4-openssl-dev gcc g++ \
    libpq-dev libsqlite3-dev \
    git zlib1g-dev libffi-dev \
    libxml2-dev libxslt-dev \
    nodejs npm texlive-xetex && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    pip install dlib face-recognition


# Set working directory to root directory
WORKDIR /

# Copy all files to the container
COPY . /

# Upgrade pip
RUN pip install --upgrade pip

# Install project dependencies
RUN pip install -r requirements.txt

# Expose the application port (adjust based on your app)
EXPOSE 10000

# Set the default command to run your app
CMD ["python", "app.py"]
