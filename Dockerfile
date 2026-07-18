# 🐳 Step 1: Use an official Python slim base image for high efficiency and speed
FROM python:3.11-slim

# 🐳 Step 2: Set the working directory inside the container for all subsequent commands
WORKDIR /app

# 🐳 Step 3: Set environment variables to prevent Python from writing pyc files and to ensure output is flushed immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🐳 Step 4: Install build-essential or libraries if needed, then clean up apt cache to keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 🐳 Step 5: Copy the requirements.txt file to install python packages
COPY requirements.txt /app/

# 🐳 Step 6: Install the python packages into the container environment using pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 🐳 Step 7: Copy the rest of the application codebase to the working directory in the container
COPY . /app/

# 🐳 Step 8: Expose the network port 8000 for the FastAPI server
EXPOSE 8000

# 🐳 Step 9: Launch the FastAPI application using Uvicorn ASGI server bound to port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
