# Використовуємо легкий образ Python на базі Alpine Linux
FROM python:3.11-alpine

# Встановлюємо системні залежності для pymysql та роботи з мережею
# Alpine потребує gcc та musl-dev для деяких пакетів, але для pymysql зазвичай достатньо чистого пітона
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev

# Створюємо робочу директорію
WORKDIR /app

# Спочатку копіюємо лише requirements, щоб кешувати встановлення бібліотек
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо основний код додатка
COPY app.py .

# Створюємо папку для секретів (куди буде монтуватися tmpfs)
RUN mkdir -p /app/secrets

# Відкриваємо порт 8000
EXPOSE 8000

# Запускаємо сервер.
# Використовуємо --interface wsgi, бо ми працюємо з Flask через Uvicorn
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--interface", "wsgi"]


# Запускаємо чистий Gunicorn з синхронними воркерами
# -w 4: для пре-проду на mini-PC можна поставити 2-4 воркери
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]