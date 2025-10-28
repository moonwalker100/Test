FROM python:3.12-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y git
# Set permissions (optional)
RUN chmod -R 777 /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Ensure start.sh is executable
RUN chmod +x start.sh

# Start the script
CMD ["sh", "start.sh"]