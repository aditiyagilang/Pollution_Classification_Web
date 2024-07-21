
from flask import Flask, request, jsonify, render_template
from db import connect_db  # Import fungsi connect_db dari db.py


@app.route('/api/esp/data', methods=['POST'])
def receive_data():
    data = request.json
    esp_id = data.get('ESP-ID')
    pm10 = data.get('PM10')
    pm25 = data.get('PM25')
    co = data.get('CO')
    hc = data.get('HC')
    o3 = data.get('O3')  # Tambahkan data O3
    ispu_pm10 = data.get('ISPU_PM10')
    ispu_pm25 = data.get('ISPU_PM25')
    ispu_co = data.get('ISPU_CO')
    ispu_hc = data.get('ISPU_HC')
    ispu_o3 = data.get('ISPU_O3')  # Tambahkan ISPU-O3

    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        query = """
            INSERT INTO sensor_data (esp_id, pm10, pm25, co, hc, o3, ispu_pm10, ispu_pm25, ispu_co, ispu_hc, ispu_o3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (esp_id, pm10, pm25, co, hc, o3, ispu_pm10, ispu_pm25, ispu_co, ispu_hc, ispu_o3))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500
  
   
@app.route('/')
def ispu_data():
    connection = connect_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        select_query = "SELECT * FROM sensor_data"
        cursor.execute(select_query)
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', data=records)

    return "Error connecting to the database", 500
    

if __name__ == '__main__':
    app.run(host='192.168.2.12', port=5000)
