FROM python:3.11-slim

# 1. Встановлюємо залежності для інсталяції
RUN apt-get update && apt-get install -y curl bash sudo && rm -rf /var/lib/apt/lists/*

# 2. Ставимо Infisical CLI прямо всередину контейнера
RUN curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get update && apt-get install -y infisical

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Оновлений запуск: додаємо python -m та явно вказуємо параметри проєкту
CMD ["infisical", "run", "--projectId=d6d3e764-7ce7-4a6a-b878-33c64433b9de", "--env=dev", "--path=/actual", "--path=/bank", "--path=/database", "--", "python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--interface", "wsgi"]
