FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY hypercorn.toml .
COPY backend ./backend
COPY static ./static

EXPOSE 8000

CMD ["hypercorn", "--config", "hypercorn.toml", "backend.main:app"]
