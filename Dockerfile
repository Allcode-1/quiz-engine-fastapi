# python 3.11
FROM python:3.11-slim

# main directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .

# run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]