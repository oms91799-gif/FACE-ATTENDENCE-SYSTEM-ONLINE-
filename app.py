import os
import face_recognition
import cv2
import numpy as np
import base64
import gspread
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
FACES_FOLDER = "known_faces"
if not os.path.exists(FACES_FOLDER): os.makedirs(FACES_FOLDER)

# Google Sheet Connection
gc = gspread.service_account(filename='creds.json')
sh = gc.open("VECTUS MAGIC SHEET MARCH")
wks = sh.sheet1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json['image']
        punch_no = request.json['punch_no']
        encoded_data = data.split(',')[1]
        with open(f"{FACES_FOLDER}/{punch_no}.jpg", "wb") as f:
            f.write(base64.b64decode(encoded_data))
        return jsonify({"status": "Success", "msg": f"ID {punch_no} Registered! ✅"})
    except: return jsonify({"status": "Error"})

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json['image']
    lat = request.json.get('lat', 'Unknown')
    lng = request.json.get('lng', 'Unknown')
    
    # Image process
    nparr = np.frombuffer(base64.b64decode(data.split(',')[1]), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    face_encs = face_recognition.face_encodings(rgb_frame)
    if not face_encs: return jsonify({"status": "No Face"})

    # Face matching
    known_encs = []
    known_names = []
    for file in os.listdir(FACES_FOLDER):
        img = face_recognition.load_image_file(f"{FACES_FOLDER}/{file}")
        known_encs.append(face_recognition.face_encodings(img)[0])
        known_names.append(os.path.splitext(file)[0])

    matches = face_recognition.compare_faces(known_encs, face_encs[0], tolerance=0.5)
    if True in matches:
        worker_id = known_names[matches.index(True)]
        now = datetime.now()
        date_today = now.strftime("%d/%m/%Y")
        time_now = now.strftime("%H:%M:%S")
        location = f"https://www.google.com/maps?q={lat},{lng}"
        
        # In/Out Logic: Sheet mein check karo aaj ki entry hai ya nahi
        records = wks.get_all_values()
        entry_type = "IN"
        for r in reversed(records):
            if r[0] == date_today and r[1] == worker_id:
                entry_type = "OUT" if r[3] == "IN" else "IN"
                break
        
        wks.append_row([date_today, worker_id, time_now, entry_type, location])
        return jsonify({"status": "Success", "id": worker_id, "type": entry_type})
        
    return jsonify({"status": "Unknown"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
