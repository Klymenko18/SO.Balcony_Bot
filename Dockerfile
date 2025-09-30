# ---- Base image ----
FROM python:3.12-slim

# Timezone та базові ENV
ENV TZ=Europe/Bratislava \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Системні залежності
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Нерутовий користувач
RUN useradd -m appuser

WORKDIR /app

# Кеш інсталяції залежностей
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Код застосунку
COPY . /app

# Безпека: запуск під non-root
USER appuser

# Healthcheck: перевірка наявності токена
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import os,sys; sys.exit(0 if os.getenv('BOT_TOKEN') else 1)"

# Старт
CMD ["python", "main.py"]
