import os
from os.path import join, dirname
from dotenv import load_dotenv

from http import client
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

# Koneksi ke MongoDB

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

connection_string = MongoClient(MONGODB_URI)
db = connection_string[DB_NAME]

app = Flask(__name__)

# Tentukan direktori untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads/'
FOLDER_PROFILE = 'static/profile/'

# Cek dan buat folder jika belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(FOLDER_PROFILE):
    os.makedirs(FOLDER_PROFILE)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FOLDER_PROFILE'] = FOLDER_PROFILE

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/diary', methods=['POST'])
def save_diary():
    title_receive = request.form['title_give']
    desc_receive = request.form['desc_give']
    
    file = request.files['file_give']
    profile = request.files['profile_give']
    
    # Dapatkan nama file untuk keduanya
    filename = file.filename if file else 'default-image.jpeg'
    profilname = profile.filename if profile else 'default-profile.jpeg'
    
    # Simpan file dan profil jika diunggah
    save_to = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    save_profile = os.path.join(app.config['FOLDER_PROFILE'], profilname)

    file.save(save_to) if file else None
    profile.save(save_profile) if profile else None

    # Mengambil waktu saat ini dan memformatnya
    current_time = datetime.now().strftime('%Y.%m.%d %H:%M')
    
    # Simpan dokumen ke MongoDB
    doc = {
        'title': title_receive,
        'description': desc_receive,
        'file_path': save_to,
        'profile_path': save_profile,
        'timestamp': current_time 
    }
    db.diary.insert_one(doc)

    return jsonify({'msg': 'Upload complete!'})

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
