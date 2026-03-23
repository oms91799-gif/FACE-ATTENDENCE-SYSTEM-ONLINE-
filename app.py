import os, cv2, face_recognition, numpy as np, base64, gspread
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

# --- NAYA EMPLOYEE ADD KARNA ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json['image']
    p_no = request.json['punch_no']
    img_data = base64.b64decode(data.split(',')[1])
    with open(f"{FACES_FOLDER}/{p_no}.jpg", "wb") as f:
        f.write(img_data)
    return jsonify({"status": "Success", "msg": f"ID {p_no} Registered! ✅"})

# --- ATTENDANCE LAGANA ---
@app.route('/scan', methods=['POST'])
def scan():
    data = request.json['image']
    lat = request.json.get('lat', '0')
    lng = request.json.get('lng', '0')
    
    nparr = np.frombuffer(base64.b64decode(data.split(',')[1]), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    face_encs = face_recognition.face_encodings(rgb_frame)
    if not face_encs: return jsonify({"status": "No Face", "msg": "Chehra nahi dikha!"})

    # Saved faces load karke match karna
    known_encs, known_names = [], []
    for file in os.listdir(FACES_FOLDER):
        img = face_recognition.load_image_file(f"{FACES_FOLDER}/{file}")
        encs = face_recognition.face_encodings(img)
        if encs:
            known_encs.append(encs[0])
            known_names.append(os.path.splitext(file)[0])

    matches = face_recognition.compare_faces(known_encs, face_encs[0], tolerance=0.5)
    if True in matches:
        worker_id = known_names[matches.index(True)]
        now = datetime.now()
        # In/Out Logic aur Location link
        loc_url = f"https://www.google.com/maps?q={lat},{lng}"
        wks.append_row([now.strftime("%d/%m/%Y"), worker_id, now.strftime("%H:%M:%S"), "P", loc_url])
        return jsonify({"status": "Success", "id": worker_id})
        
    return jsonify({"status": "Unknown", "msg": "Anjaan Chehra!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
