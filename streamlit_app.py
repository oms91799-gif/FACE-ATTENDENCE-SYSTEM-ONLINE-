import streamlit as st
import face_recognition
import os
import gspread
from datetime import datetime
from PIL import Image

# Google Sheet Connection
gc = gspread.service_account(filename='creds.json')
sh = gc.open("VECTUS MAGIC SHEET MARCH")
wks = sh.sheet1

st.set_page_config(page_title="VECTUS AI", layout="centered")
st.title("🛡️ VECTUS AI ATTENDANCE")

# 1. NAYA BANDE KO SAVE KARNA (Registration)
st.sidebar.header("➕ Register New Labor")
new_id = st.sidebar.text_input("Enter Punching No (e.g. 120001)")
reg_img = st.sidebar.camera_input("Register Photo")

if st.sidebar.button("Save to System") and reg_img and new_id:
    if not os.path.exists("known_faces"): os.makedirs("known_faces")
    img = Image.open(reg_img)
    img.save(f"known_faces/{new_id}.jpg")
    st.sidebar.success(f"ID {new_id} is now Registered! ✅")

# 2. AUTOMATIC ATTENDANCE (Scanning)
st.header("📸 Scan Face (Auto ID)")
att_img = st.camera_input("Look at Camera to Mark Attendance")

if att_img:
    st.info("Searching ID in Database... ⏳")
    test_img = face_recognition.load_image_file(att_img)
    test_encs = face_recognition.face_encodings(test_img)
    
    if test_encs:
        found = False
        # Sare saved faces check karo
        for file in os.listdir("known_faces"):
            if file.endswith(".jpg"):
                known_img = face_recognition.load_image_file(f"known_faces/{file}")
                known_enc = face_recognition.face_encodings(known_img)[0]
                
                # Match mila?
                results = face_recognition.compare_faces([known_enc], test_encs[0], tolerance=0.5)
                if results[0]:
                    worker_id = file.split(".")[0] # ID photo ke naam se utha li
                    now = datetime.now()
                    wks.append_row([now.strftime("%d/%m/%Y"), worker_id, now.strftime("%H:%M:%S"), "P"])
                    st.success(f"✅ ID {worker_id} Ki Attendance Lag Gayi!")
                    found = True
                    break
        if not found: st.error("❌ Anjaan Chehra! Pehle Register karein.")
    else:
        st.warning("Chehra nahi dikha, sahi se khade ho.")
