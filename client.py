import requests
import time

# Даем серверу gunicorn секунду на полный запуск
time.sleep(2)

try:
    # Делаем проверочный запрос на главную страницу (где находится капча)
    res = requests.get('http://localhost:5000/')
    print(f"Тест пройден! Статус ответа сервера: {res.status_code}")
    if res.ok:
        print("Сервер Flask работает корректно и отвечает.")
except Exception as e:
    print(f"Ошибка при тестировании сервера: {e}")
    # Выходим с ошибкой, если сервер вообще не ответил
    exit(1)