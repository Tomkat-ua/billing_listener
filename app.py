import os,logging,requests,threading,time
import pymysql
from flask import Flask, request
from pathlib import Path
from dotenv import load_dotenv

# Вказуємо точний шлях до нашого RAM-диску
env_path = Path("/app/secrets/.env")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("Секрети успішно завантажено в пам'ять процесу!")
else:
    print("Помилка: файл .env не знайдено в оперативці!")

# Вказуємо точний шлях до нашого RAM-диску
env_path = Path("/app/secrets/.env")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("Секрети успішно завантажено в пам'ять процесу!")
else:
    print("Помилка: файл .env не знайдено в оперативці!")



app = Flask(__name__)

env_path = Path("/app/secrets/.env")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("Секрети успішно завантажено в пам'ять процесу!")
else:
    print("Помилка: файл .env не знайдено в оперативці!")


# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Секрети (локально беруться дефолти, в Docker прилетять з Infisical)
X_TOKEN = os.environ.get('MONO_API_KEY', 'erererfvffvfv45454545')
# Зовнішня адреса вашого сервера (наприклад, через Cloudflare Tunnel чи білий IP)
WEBHOOK_URL = os.environ.get('BILL_WEBHOOK_URL', 'http://127.0.0.1:8000/webhook')
WEBHOOK_ROUTE = WEBHOOK_URL.rsplit('/', 1)[-1]


# Замість модуля config — беремо прямо з оточення (Infisical)
DB_CONFIG = {
    'host': os.getenv('DB_HOST','127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 3307)),
    'user': os.getenv('DB_USER','billing_user'),
    'password': os.getenv('DB_PASSWORD','wssASD4TRaS'),
    'database': os.getenv('DB_NAME','billing_system'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def register_webhook():
    """Функція автоматичної реєстрації нашого URL в Monobank"""
    # Даємо серверу Uvicorn 2 секунди, щоб повністю піднятися
    time.sleep(2)

    url = os.getenv('MONO_WEBHOOK_URL', "https://api.monobank.ua/bank/webhook")
    headers = {"X-Token": X_TOKEN}
    payload = {"webHookUrl": WEBHOOK_URL}

    app.logger.info(f"Спроба реєстрації вебхука в Monobank на адресу: {WEBHOOK_URL}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            app.logger.info("Успішно: Monobank підтвердив реєстрацію вебхука!")
        else:
            app.logger.error(f"Помилка реєстрації вебхука: {response.status_code} - {response.text}")
    except Exception as e:
        app.logger.error(f"Не вдалося зв'язатися з API Monobank: {e}")


# Запускаємо реєстрацію в окремому потоці, щоб не заважати старту Flask
#threading.Thread(target=register_webhook, daemon=True).start()


def save_json(raw_payload):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO raw_webhooks (payload) VALUES (%s)"
            cursor.execute(sql, (raw_payload,))
        connection.commit()
    finally:
        connection.close()


@app.route(f'/{WEBHOOK_ROUTE}', methods=['GET', 'POST'])
def monobank_webhook():
    # 1. ОБРОБКА GET-ЗАПИТУ (Валідація від банку під час реєстрації)
    if request.method == 'GET':
        app.logger.info("Отримано GET-запит від Monobank для валідації URL.")
        return "OK", 200

    # 2. ОБРОБКА POST-ЗАПИТУ (Отримання реальних транзакцій)
    if request.method == 'POST':
        try:
            # Отримуємо сирий текст запиту, щоб передати його в базу як чистий JSON-рядок
            raw_data = request.get_data(as_text=True)

            if not raw_data:
                app.logger.warning("Отримано порожній запит POST.")
                return "Empty body", 400

            app.logger.info("Отримано вебхук від Monobank. Запис в MariaDB...")

            # Викликаємо вашу функцію збереження
            save_json(raw_data)

            app.logger.info("Успішно: Транзакцію збережено в raw_webhooks.")
            return "OK", 200

        except pymysql.MySQLError as db_err:
            app.logger.error(f"Помилка бази даних MariaDB (можливо, невалідний JSON): {db_err}")
            return "DB Error", 200

        except Exception as e:
            app.logger.error(f"Загальна помилка при обробці вебхука: {e}")
            return "Error", 200


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)