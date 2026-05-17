FROM python:3.11-slim

# 1. Встановлюємо залежності для інсталяції
RUN apt-get update && apt-get install -y curl bash sudo && rm -rf /var/lib/apt/lists/*

# 2. Ставимо Infisical CLI прямо всередину контейнера
RUN curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get update && apt-get install -y infisical

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py

# 3. ЗАМІСТЬ звичайного "python main.py" ми запускаємо додаток через INFISICAL RUN!
# Ми кажемо йому стягнути дані з трьох папок одночасно
#CMD ["infisical", "run", "--path=/actual", "--path=/bank", "--path=/database", "--", "python", "main.py"]
# ... (твоє встановлення залежностей та копіювання коду) ...

# Замість старого CMD загортаємо запуск uvicorn в утиліту Infisical
CMD ["infisical", "run", "--path=/actual", "--path=/bank", "--path=/database", "--", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--interface", "wsgi"]

