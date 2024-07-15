from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)


db_config = {
    'host': 'localhost',
    'database': 'air_quality',
    'user': 'root',
    'password': ''  
}

def connect_db():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None

@app.route('/api/esp/data', methods=['GET'])
def receive_data():
    esp_id = request.args.get('ESP-ID')
    pm10 = request.args.get('PM10')
    pm25 = request.args.get('PM25')
    co = request.args.get('CO')
    hc = request.args.get('HC')
    ispu_pm10 = request.args.get('ISPU_PM10')
    ispu_pm25 = request.args.get('ISPU_PM25')
    ispu_co = request.args.get('ISPU_CO')
    ispu_hc = request.args.get('ISPU_HC')

    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        query = """
            INSERT INTO sensor_data (esp_id, pm10, pm25, co, hc, ispu_pm10, ispu_pm25, ispu_co, ispu_hc)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (esp_id, pm10, pm25, co, hc, ispu_pm10, ispu_pm25, ispu_co, ispu_hc))
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
    app.run(host='0.0.0.0', port=5000)