FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies needed by the fill script
COPY 06-seed/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy only what the fill script needs
COPY 06-seed /app/06-seed
COPY 01-api /app/01-api
COPY 04-authentication /app/04-authentication

CMD ["python", "06-seed/script_remplissage.py"]
