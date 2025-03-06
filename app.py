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
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500

@app.route('/home')
def home():
    connection = connect_db()
    cursor = connection.cursor()
    try:
        # Ambil hanya 1 data terbaru untuk ditampilkan di kartu
        cursor.execute("SELECT timestamp, so2, no2, pm10, pm25, hc, co, o3, klasifikasi FROM klasifikasi ORDER BY timestamp DESC LIMIT 1")
        latest_data = cursor.fetchone()  # Ambil 1 baris terbaru

        print("DATA TERBARU:", latest_data)  # DEBUGGING

        # Ambil 7 data terakhir untuk grafik
        cursor.execute("SELECT timestamp, so2, no2, pm10, pm25, hc, co, o3 FROM klasifikasi ORDER BY timestamp DESC LIMIT 7")
        klasifikasi_data = cursor.fetchall()  # Semua data untuk grafik

        print("DATA UNTUK GRAFIK:", klasifikasi_data)  # DEBUGGING

        # Ambil timestamp untuk grafik
        timestamps = [row[0] for row in klasifikasi_data]  # Ambil timestamp dari setiap baris
        
        # Label untuk parameter
        labels = ['so2', 'no2', 'pm10', 'pm25', 'hc', 'co', 'o3']
        datasets = []

        # Siapkan data untuk grafik
        for idx, label in enumerate(labels):
            data_for_chart = [row[idx + 1] for row in klasifikasi_data]  # Data kolom ke-(idx+1)
            datasets.append({
                'label': label.upper(),
                'data': data_for_chart,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'tension': 0.3
            })

        return render_template('dashboard.html', 
                               latest_data=latest_data,  # Data terbaru untuk card
                               datasets=datasets,  # Data untuk grafik
                               timestamps=timestamps)  # Timestamp untuk grafik

    except Exception as e:
        print(f"Error fetching data: {e}")
        return render_template('dashboard.html', latest_data={}, datasets=[], timestamps=[])

    finally:
        cursor.close()
        connection.close()



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
    # Koneksi ke database untuk mengambil data terbaru
    connection = connect_db()
    cursor = connection.cursor()
    try:
        # Ambil data klasifikasi terbaru (tergantung pada bagaimana struktur tabel)
        cursor.execute("SELECT timestamp, so2, no2, pm10, pm25, hc, co, o3, klasifikasi FROM klasifikasi ORDER BY timestamp DESC LIMIT 7")  # Ambil data terbaru
        klasifikasi_data = cursor.fetchall()

        # Ambil data untuk grafik
        timestamps = [row[0] for row in klasifikasi_data]  # Ambil timestamp untuk sumbu X
        labels = ['so2', 'no2', 'pm10', 'pm25', 'hc', 'co', 'o3']
        datasets = []

        # Sesuaikan data untuk grafik
        for idx, label in enumerate(labels):
            data_for_chart = [row[idx + 1] for row in klasifikasi_data]  # Ambil data berdasarkan kolom untuk grafik
            datasets.append({
                'label': label,
                'data': data_for_chart,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'tension': 0.3
            })

        # Kirimkan data klasifikasi ke template
        return render_template('dashboard.html', klasifikasi_data=klasifikasi_data, datasets=datasets, timestamps=timestamps)

    except Exception as e:
        print(f"Error fetching data: {e}")
        return render_template('dashboard.html', klasifikasi_data=[], datasets=[], timestamps=[])

    finally:
        cursor.close()
        connection.close()



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
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        # Contoh query: mengambil semua kolom kecuali timestamp (atau sertakan jika perlu)
        cursor.execute("""
            SELECT id, so2, no2, o3, co, pm10, pm25, hc, klasifikasi
            FROM klasifikasi
            ORDER BY id DESC
        """)
        data = cursor.fetchall()  # data akan berbentuk list of tuples
        cursor.close()
        connection.close()

        # Kirim data ke template
        return render_template('clasification.html', data=data)
    else:
        return "Database connection error", 500

@app.route('/edit-klasifikasi/<id>', methods=['PUT'])
def edit_klasifikasi(id):
    data = request.get_json()

    # Ambil data yang dikirim
    pm10 = data.get('pm10')
    pm25 = data.get('pm25')
    co = data.get('co')
    hc = data.get('hc')
    o3 = data.get('o3')
    no2 = data.get('no2')
    so2 = data.get('so2')

    # Prediksi menggunakan model
    input_data = pd.DataFrame([[pm10, pm25, co, hc, o3, no2, so2]], 
                                  columns=['pm10', 'pm25', 'co', 'hc', 'o3', 'no2', 'so2'])
    
    # Prediksi menggunakan model SVM yang sudah dilatih
    prediction = model.predict(input_data)
    klasifikasi = prediction[0]  # Hasil klasifikasi

    # Koneksi ke database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Update data di tabel klasifikasi dan set klasifikasi yang baru
            update_query = """
                UPDATE klasifikasi
                SET pm10 = %s, pm25 = %s, co = %s, hc = %s, o3 = %s, no2 = %s, so2 = %s, klasifikasi = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (pm10, pm25, co, hc, o3, no2, so2, klasifikasi, id))
            connection.commit()

            cursor.close()
            connection.close()
            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()
            cursor.close()
            connection.close()
            return jsonify({"status": "failed", "reason": str(e)}), 500
    else:
        return jsonify({"status": "failed", "reason": "Database connection error"}), 500

@app.route('/delete-klasifikasi/<id>', methods=['DELETE'])
def delete_klasifikasi(id):
    # Koneksi ke database
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            delete_query = """
                DELETE FROM klasifikasi WHERE id = %s
            """
            cursor.execute(delete_query, (id,))
            connection.commit()

            cursor.close()
            connection.close()
            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()
            cursor.close()
            connection.close()
            return jsonify({"status": "failed", "reason": str(e)}), 500
    else:
        return jsonify({"status": "failed", "reason": "Database connection error"}), 500


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

@app.route('/logout')
def logout():
    # Hapus semua data dari session
    session.clear()
    # Kembali ke halaman index
    return redirect('/')

@app.route('/')
def ispu_data():
    connection = connect_db()
    cursor = connection.cursor()
    try:
        # Ambil hanya 1 data terbaru untuk ditampilkan di kartu
        cursor.execute("SELECT timestamp, so2, no2, pm10, pm25, hc, co, o3, klasifikasi FROM klasifikasi ORDER BY timestamp DESC LIMIT 1")
        latest_data = cursor.fetchone()  # Ambil 1 baris terbaru

        print("DATA TERBARU:", latest_data)  # DEBUGGING

        # Ambil 7 data terakhir untuk grafik
        cursor.execute("SELECT timestamp, so2, no2, pm10, pm25, hc, co, o3 FROM klasifikasi ORDER BY timestamp DESC LIMIT 7")
        klasifikasi_data = cursor.fetchall()  # Semua data untuk grafik

        print("DATA UNTUK GRAFIK:", klasifikasi_data)  # DEBUGGING

        # Ambil timestamp untuk grafik
        timestamps = [row[0] for row in klasifikasi_data]  # Ambil timestamp dari setiap baris
        
        # Label untuk parameter
        labels = ['so2', 'no2', 'pm10', 'pm25', 'hc', 'co', 'o3']
        datasets = []

        # Siapkan data untuk grafik
        for idx, label in enumerate(labels):
            data_for_chart = [row[idx + 1] for row in klasifikasi_data]  # Data kolom ke-(idx+1)
            datasets.append({
                'label': label.upper(),
                'data': data_for_chart,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'tension': 0.3
            })

        return render_template('index.html', 
                               latest_data=latest_data,  # Data terbaru untuk card
                               datasets=datasets,  # Data untuk grafik
                               timestamps=timestamps)  # Timestamp untuk grafik

    except Exception as e:
        print(f"Error fetching data: {e}")
        return render_template('index.html', latest_data={}, datasets=[], timestamps=[])

    finally:
        cursor.close()
        connection.close()


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

@app.route('/add-klasifikasi', methods=['POST'])
def add_klasifikasi():
    data = request.get_json()

    # Ambil data dari request
    pm10 = float(data.get('pm10', 0))
    pm25 = float(data.get('pm25', 0))
    co   = float(data.get('co', 0))
    hc   = float(data.get('hc', 0))
    o3   = float(data.get('o3', 0))
    no2  = float(data.get('no2', 0))
    so2  = float(data.get('so2', 0))

    # Buat DataFrame untuk input model
    input_data = pd.DataFrame([[pm10, pm25, co, hc, o3, no2, so2]],
                              columns=['pm10', 'pm25', 'co', 'hc', 'o3', 'no2', 'so2'])

    # Lakukan prediksi
    try:
        prediction = model.predict(input_data)
        klasifikasi = prediction[0]  # Hasil klasifikasi

        # Simpan data dan hasil ke database
        connection = connect_db()
        if connection:
            cursor = connection.cursor()
            try:
                insert_query = """
                    INSERT INTO klasifikasi (so2, no2, pm10, pm25, hc, co, o3, klasifikasi, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Timestamp sekarang
                current_time = datetime.now()

                cursor.execute(insert_query, (so2, no2, pm10, pm25, hc, co, o3, klasifikasi, current_time))
                connection.commit()

                cursor.close()
                connection.close()
                return jsonify({"status": "success"}), 200
            except Exception as e:
                connection.rollback()
                cursor.close()
                connection.close()
                return jsonify({"status": "failed", "reason": str(e)}), 500
        else:
            return jsonify({"status": "failed", "reason": "Database connection error"}), 500
    except Exception as e:
        return jsonify({"status": "failed", "reason": str(e)}), 500

@app.route('/edit-esp/<id>', methods=['PUT'])
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
            # Query untuk update data lokasi berdasarkan esp_id (string)
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


@app.route('/delete-esp/<id>', methods=['DELETE'])
def delete_esp(id):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        try:
            # Query untuk menghapus data berdasarkan esp_id (string)
            delete_query = """
                DELETE FROM esp
                WHERE esp_id = %s
            """
            cursor.execute(delete_query, (id,))
            connection.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            connection.rollback()  # Rollback jika terjadi error
            return jsonify({"status": "failed", "reason": str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"status": "failed", "reason": "database connection error"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
