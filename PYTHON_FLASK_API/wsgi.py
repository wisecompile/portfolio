# C:\FlaskInventory\wsgi.py
from app import app          # ← имя вашего файла app.py (с маленькой буквой)

if __name__ == "__main__":
    from waitress import serve
    serve(
        app,
        host="127.0.0.1",     # слушаем только loopback
        port=5051,            # тот же порт, что был у dev-Flask
        threads=4             # можно увеличить при большой нагрузке
    )
    

