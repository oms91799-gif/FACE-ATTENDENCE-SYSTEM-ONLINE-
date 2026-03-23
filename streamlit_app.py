import streamlit as st
import face_recognition
import cv2
import numpy as np
import gspread
from datetime import datetime
import os
from PIL import Image

# Google Sheet Connection
try:
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open("VECTUS MAGIC SHEET MARCH")
    wks = sh.sheet1
except:
    st.error("creds.json file nahi mili ya Sheet access nahi hai!")

st.title("🛡️ VECTUS AI ATTENDANCE")

# Register Section
st.sidebar.header("➕ Register Labor")
new_id = st.sidebar.text_input("Punching Number")
reg_img = st.sidebar.camera_input("Take Photo to Register")

if st.sidebar.button("Save Employee") and reg_img and new_id:
    if not os.path.exists("known_faces"): os.makedirs("known_faces")
    img = Image.open(reg_img)
    img.save(f"known_faces/{new_id}.jpg")
    st.sidebar.success(f"ID {new_id} Registered! ✅")

# Attendance Section
st.header("📸 Scan Face for Attendance")
att_img = st.camera_input("Look at Camera")

if att_img:
    st.info("Scanning... ⏳")
    test_img = face_recognition.load_image_file(att_img)
    test_encs = face_recognition.face_encodings(test_img)
    
    if test_encs:
        found = False
        for file in os.listdir("known_faces"):
            if file.endswith(".jpg"):
                known_img = face_recognition.load_image_file(f"known_faces/{file}")
                known_enc = face_recognition.face_encodings(known_img)[0]
                
                results = face_recognition.compare_faces([known_enc], test_encs[0], tolerance=0.5)
                if results[0]:
                    worker_id = file.split(".")[0]
                    now = datetime.now()
                    wks.append_row([now.strftime("%d/%m/%Y"), worker_id, now.strftime("%H:%M:%S"), "P"])
                    st.success(f"✅ Attendance Marked: ID {worker_id}")
                    found = True
                    break
        if not found: st.error("❌ Chehra nahi mila! Pehle Register karein.")
    else:
        st.warning("Chehra nahi dikha, dobara try karein.")
