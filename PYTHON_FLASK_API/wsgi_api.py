# C:\FlaskInventory\wsgi_api.py
from api_app import app   # ← подключаем твой api_app.py

if __name__ == "__main__":
    from waitress import serve
    serve(
        app,
        host="127.0.0.1",
        port=5052,
        threads=4
    )
