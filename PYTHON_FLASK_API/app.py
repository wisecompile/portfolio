from flask import Flask, request, render_template
import pyodbc
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
conn_str = os.environ.get('CONN_STR')
if not conn_str:
    raise RuntimeError("Connection string not found. Please set CONN_STR in your .env file.")

app = Flask(__name__)

# Logging setup
LOG_FOLDER = r"C:\FlaskInventory"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER, "http_requests.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@app.template_filter('price_fmt')
def price_fmt(value):
    try:
        return f"{int(value):,}".replace(',', "'")
    except (TypeError, ValueError):
        return "–"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    sku = ""
    brand = request.headers.get("X-Brand")

    if request.method == "POST":
        sku = request.form.get("sku")
        client_ip = request.headers.get("X-Real-Ip", request.remote_addr)
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            if brand == "KUCHENSTERN":
                # Only KUCHENSTERN
                cursor.execute(
                    "SELECT BRAND, SKU, DSC, PRC, QTY_1, QTY_2, QTY_3 FROM dbo.InventoryList WHERE SKU = ? AND BRAND = ?",
                    sku, brand
                )
            else:
                # All except KUCHENSTERN
                cursor.execute(
                    "SELECT BRAND, SKU, DSC, PRC, QTY_1, QTY_2, QTY_3 FROM dbo.InventoryList WHERE SKU = ? AND BRAND <> ?",
                    sku, "KUCHENSTERN"
                )
            row = cursor.fetchone()
            if row:
                result = {
                    "BRAND": row.BRAND,
                    "SKU": row.SKU,
                    "DSC": row.DSC,
                    "PRC": row.PRC,
                    "QTY_1": row.QTY_1,
                    "QTY_2": row.QTY_2,
                    "QTY_3": row.QTY_3,
                }
                logging.info(f"Request from {client_ip}, SKU={sku}, BRAND={brand}, STATUS=FOUND")
            else:
                error = "Артикул не найден"
                logging.info(f"Request from {client_ip}, SKU={sku}, BRAND={brand}, STATUS=NOT_FOUND")
            conn.close()
        except Exception as e:
            error = f"Ошибка при подключении к базе: {e}"
            logging.error(f"Request from {client_ip}, SKU={sku}, BRAND={brand}, STATUS=ERROR, MESSAGE={e}")

    return render_template("index.html", result=result, error=error, sku=sku)

if __name__ == '__main__':
    # NOTE: Set host and port in production via external configuration
    # Example:
    # port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    # app.run(host='127.0.0.1', port=port, debug=False)
    app.run(host='127.0.0.1', port=PORT, debug=False)  # PORT should be set via environment or config
