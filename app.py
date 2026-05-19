import logging,pymysql
import config as c
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Зовнішня адреса
WEBHOOK_URL = c.params.get('bill_webhook_url')
WEBHOOK_ROUTE = WEBHOOK_URL.rsplit('/', 1)[-1]

DB_CONFIG = {
    'host'    : c.params.get('db_host'),
    'port'    : c.params.get('db_port'),
    'user'    : c.params.get('db_user'),
    'password': c.params.get('db_password'),
    'database': c.params.get('db_name'),
    'charset' : 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


# def register_webhook():
#     """Функція автоматичної реєстрації нашого URL в Monobank"""
#     # Даємо серверу Uvicorn 2 секунди, щоб повністю піднятися
#     time.sleep(2)
#
#     url = c.params.get('MONO_WEBHOOK_URL')
#     headers = {"X-Token": X_TOKEN}
#     payload = {"webHookUrl": WEBHOOK_URL}
#
#     app.logger.info(f"Спроба реєстрації вебхука в Monobank на адресу: {WEBHOOK_URL}")
#     try:
#         response = requests.post(url, headers=headers, json=payload, timeout=10)
#         if response.status_code == 200:
#             app.logger.info("Успішно: Monobank підтвердив реєстрацію вебхука!")
#         else:
#             app.logger.error(f"Помилка реєстрації вебхука: {response.status_code} - {response.text}")
#     except Exception as e:
#         app.logger.error(f"Не вдалося зв'язатися з API Monobank: {e}")


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
            raw_data = request.get_data(as_text=True)
            if not raw_data:
                app.logger.warning("Отримано порожній запит POST.")
                return "Empty body", 400
            app.logger.info("Отримано вебхук від Monobank. Запис в MariaDB...")
            save_json(raw_data)
            app.logger.info("Успішно: Транзакцію збережено в raw_webhooks.")
            return "OK", 200

        except pymysql.MySQLError as db_err:
            app.logger.error(f"Помилка бази даних MariaDB (можливо, невалідний JSON): {db_err}")
            return "DB Error", 200

        except Exception as e:
            app.logger.error(f"Загальна помилка при обробці вебхука: {e}")
            return "Error", 200
