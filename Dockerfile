FROM python:3.12-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

CMD ["sh", "start.sh"]
