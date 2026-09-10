FROM python:3.9-slim

WORKDIR /app

# Копируем файлы с зависимостями
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Даём права на выполнение st.sh
RUN chmod +x st.sh

# Открываем порт 5000
EXPOSE 5000

# Запускаем Gunicorn (сервер будет работать постоянно, без kill)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]