import os
import cv2
import face_recognition
import numpy as np
import base64
import gspread
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
SHEET_NAME = "VECTUS MAGIC SHEET MARCH"
FACES_FOLDER = "known_faces"

# 1. Google Sheet Connection (Make sure creds.json is uploaded)
try:
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open(SHEET_NAME)
    wks = sh.sheet1
except Exception as e:
    print(f"Sheet Error: {e}")

# 2. AI: Load Labor Faces from Folder
known_encodings = []
known_names = []

def load_labor():
    if not os.path.exists(FACES_FOLDER): os.makedirs(FACES_FOLDER)
    for file in os.listdir(FACES_FOLDER):
        if file.endswith(('.jpg', '.png', '.jpeg')):
            img = face_recognition.load_image_file(f"{FACES_FOLDER}/{file}")
            encoding = face_recognition.face_encodings(img)[0]
            known_encodings.append(encoding)
            known_names.append(os.path.splitext(file)[0]) # Punching No
load_labor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json['image']
    encoded_data = data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Face Detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locs = face_recognition.face_locations(rgb_frame)
    face_encs = face_recognition.face_encodings(rgb_frame, face_locs)
    
    for face_enc in face_encs:
        matches = face_recognition.compare_faces(known_encodings, face_enc, tolerance=0.5)
        if True in matches:
            worker_id = known_names[matches.index(True)]
            # --- SAVE TO GOOGLE SHEET ---
            now = datetime.now()
            wks.append_row([now.strftime("%d"), worker_id, "0", "P", now.strftime("%H:%M")])
            return jsonify({"status": "Success", "id": worker_id})
            
    return jsonify({"status": "Unknown", "msg": "Chehra Nahi Pehchana!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
