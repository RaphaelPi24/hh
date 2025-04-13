FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /app

COPY ./src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=775 build/backend/entrypoint.dev.sh /entrypoint.sh
COPY ./src .
COPY build/.env.production .env

CMD ["/entrypoint.sh"]