from flask import Flask, request, jsonify
import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
conn_str = os.environ.get('CONN_STR')
if not conn_str:
    raise RuntimeError("Connection string not found. Please set CONN_STR in your .env file.")

app = Flask(__name__)

@app.route('/api/bulk', methods=['GET'])
def get_bulk():
    # 1. Get API key
    api_key = request.headers.get('Authorization', '').replace('Api-Key ', '')
    if not api_key:
        api_key = request.args.get('api_key', '')

    if not api_key:
        return jsonify({"error": "API key required"}), 401

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 2. Validate API key and fetch allowed brands
        cursor.execute("""
            SELECT Brand1, Brand2, Brand3, Brand4 FROM dbo.BrandEmails WHERE API_KEY = ?
        """, api_key)
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Invalid API key"}), 403

        allowed_brands = [b for b in row if b]

        if not allowed_brands:
            return jsonify({"error": "No brands assigned for this key"}), 403

        # 3. Query products only for allowed brands
        placeholders = ','.join(['?'] * len(allowed_brands))
        sql = f"""
            SELECT SKU, DSC, PRC, QTY_1, QTY_2, QTY_3, BRAND
            FROM dbo.InventoryList
            WHERE BRAND IN ({placeholders})
        """
        cursor.execute(sql, allowed_brands)
        products = cursor.fetchall()

        # 4. Convert results to JSON array
        result = [
            {
                "SKU": product.SKU,
                "DSC": product.DSC,
                "PRC": product.PRC,
                "QTY_1": product.QTY_1,
                "QTY_2": product.QTY_2,
                "QTY_3": product.QTY_3,
                "BRAND": product.BRAND
            }
            for product in products
        ]

        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # NOTE: Set host and port in production via external configuration
    app.run(host='127.0.0.1', port=PORT)  # PORT should be set via environment or config
    # Example:
    # port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    # app.run(host='127.0.0.1', port=port)
