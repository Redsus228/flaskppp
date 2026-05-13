gunicorn --bind 0.0.0.0:5000 wsgi:app & APP_PID=$!
sleep 5
echo start client
python3 client.py
sleep 5
echo $APP_PID
exit 0
