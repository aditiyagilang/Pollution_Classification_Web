from flask import Flask, request, jsonify, render_template, redirect, session
from flask_bcrypt import Bcrypt
from db import connect_db  # Pastikan Anda memiliki fungsi untuk koneksi ke database
from datetime import datetime
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = 'b3c69c0b-8e72-492f-b9f4-a13e447dcadf'

bcrypt = Bcrypt(app)

# Load model untuk prediksi
model = joblib.load('svc_rbf.pkl')

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
    timestamp = datetime.now()

    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            insert_polusi_query = """
                INSERT INTO data_polusi (esp_id, pm10, pm25, co, hc, o3, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_polusi_query, (esp_id, pm10, pm25, co, hc, o3, timestamp))
            polusi_id = cursor.lastrowid 
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

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/sign-in')
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = connect_db()
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
                # Ambil data user berdasarkan username
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (username,))
                user = cursor.fetchone()

                if user and bcrypt.check_password_hash(user['password'], password):
                    # Jika valid, simpan user_id dan username ke session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect('/home')
                else:
                    # Jika tidak valid, tampilkan pesan error
                    return render_template('login.html', error="Invalid username or password")
            except Exception as e:
                return f"Error: {e}"
            finally:
                cursor.close()
                connection.close()

        return jsonify({"status": "failed", "reason": "database connection error"}), 500

    # Tampilkan halaman login jika request method adalah GET
    return render_template('login.html')

@app.route('/data')
def data():
    return render_template('dashboard.html')

@app.route('/lokasi')
def location():
    # Mengambil data lokasi dari database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM esp")  # Mengambil data dari tabel esp
        lokasi_list = cursor.fetchall()  # Menyimpan hasil query
        cursor.close()
        connection.close()
        
        # Kirim data lokasi ke template
        return render_template('location.html', lokasi_list=lokasi_list)
    else:
        return "Database connection failed", 500

@app.route('/polusi')
def pollution():
    return render_template('pollution.html')

@app.route('/klasifikasi')
def clasification():
    return render_template('clasification.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Ambil input dari form
        pm10 = float(request.form.get('pm10', 0))
        pm25 = float(request.form.get('pm25', 0))
        co = float(request.form.get('co', 0))
        hc = float(request.form.get('hc', 0))
        o3 = float(request.form.get('o3', 0))
        no2 = float(request.form.get('no2', 0))  # Tambahkan no2
        so2 = float(request.form.get('so2', 0))  # Tambahkan so2
        
        # Siapkan data untuk prediksi
        input_data = pd.DataFrame([[pm10, pm25, co, hc, o3, no2, so2]], 
                                  columns=['pm10', 'pm25', 'co', 'hc', 'o3', 'no2', 'so2'])
        
        # Prediksi menggunakan model
        prediction = model.predict(input_data)
        prediction_result = prediction[0]
        
        return render_template('predict.html', prediction=prediction_result)
    
    return render_template('predict.html', prediction=None)

@app.route('/login')
def login():
    return render_template('login.html')

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

# Fungsi untuk mendaftar user baru
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = connect_db()
        if connection:
            cursor = connection.cursor()
            try:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username, hashed_password))
                connection.commit()
                return redirect('/sign-in')
            except Exception as e:
                return f"Error: {e}"
            finally:
                cursor.close()
                connection.close()

        return jsonify({"status": "failed", "reason": "database connection error"}), 500

    return render_template('sign-up.html')

@app.route('/add-esp', methods=['POST'])
def add_esp():
    data = request.get_json()

    # Ambil data dari request
    esp_id = data.get('id')
    nama = data.get('nama')

    # Pastikan data ada
    if not esp_id or not nama:
        return jsonify({"status": "failed", "reason": "ID dan Nama harus diisi"}), 400

    # Koneksi ke database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Query untuk insert data ke tabel esp
            insert_query = """
                INSERT INTO esp (esp_id, location) 
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (esp_id, nama))
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  # Rollback jika ada error
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500

@app.route('/edit-esp/<int:id>', methods=['PUT'])
def edit_esp(id):
    data = request.get_json()

    # Ambil data dari request
    nama = data.get('nama')

    if not nama:
        return jsonify({"status": "failed", "reason": "Nama harus diisi"}), 400

    # Koneksi ke database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Query untuk update data lokasi berdasarkan ID
            update_query = """
                UPDATE esp
                SET location = %s
                WHERE esp_id = %s
            """
            cursor.execute(update_query, (nama, id))
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  # Rollback jika ada error
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500
    
@app.route('/delete-esp/<int:id>', methods=['DELETE'])
def delete_esp(id):
    # Koneksi ke database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Query untuk menghapus data lokasi berdasarkan ID
            delete_query = """
                DELETE FROM esp
                WHERE esp_id = %s
            """
            cursor.execute(delete_query, (id,))
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  # Rollback jika ada error
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
