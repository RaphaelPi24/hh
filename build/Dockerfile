FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY build/.env.production .env
COPY . .

CMD ["python", "app.py"]
