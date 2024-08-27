from flask import Flask, request, jsonify, render_template
from db import connect_db  
from datetime import datetime

app = Flask(__name__)



@app.route('/api/esp/data', methods=['POST'])
def receive_data():
    data = request.json
    esp_id = data.get('ESP-ID')
    pm10 = data.get('PM10')
    pm25 = data.get('PM25')
    co = data.get('CO')
    hc = data.get('HC')
    o3 = data.get('O3')  
    ispu_pm10 = data.get('ISPU_PM10')
    ispu_pm25 = data.get('ISPU_PM25')
    ispu_co = data.get('ISPU_CO')
    ispu_hc = data.get('ISPU_HC')
    ispu_o3 = data.get('ISPU_O3')  
    
    # Mengambil waktu saat ini untuk timestamp
    timestamp = datetime.now()

    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Insert into data_polusi table dengan timestamp
            insert_polusi_query = """
                INSERT INTO data_polusi (esp_id, pm10, pm25, co, hc, o3, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_polusi_query, (esp_id, pm10, pm25, co, hc, o3, timestamp))
            polusi_id = cursor.lastrowid  # Get the last inserted id

            # Insert into ispu_data table
            insert_ispu_query = """
                INSERT INTO ispu_data (polusi_id, ispu_pm10, ispu_pm25, ispu_co, ispu_hc, ispu_o3)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_ispu_query, (polusi_id, ispu_pm10, ispu_pm25, ispu_co, ispu_hc, ispu_o3))

            # Commit the transaction
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  # Rollback in case of error
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500


@app.route('/')
def ispu_data():
    connection = connect_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        select_query = """
            SELECT dp.*, ispu.ispu_pm10, ispu.ispu_pm25, ispu.ispu_co, ispu.ispu_hc, ispu.ispu_o3
            FROM data_polusi dp
            JOIN ispu_data ispu ON dp.data_id = ispu.polusi_id
            ORDER BY dp.data_id DESC
        """
        cursor.execute(select_query)
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', data=records)

    return "Error connecting to the database", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
