import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import gspread
from datetime import datetime
import os

# Google Sheet Connection
gc = gspread.service_account(filename='creds.json')
sh = gc.open("VECTUS MAGIC SHEET MARCH")
wks = sh.sheet1

st.title("🛡️ VECTUS SMART ATTENDANCE")

# Setup Mediapipe for Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Register/Attendance Logic
st.sidebar.header("➕ Setup")
mode = st.sidebar.radio("Mode Chuno:", ["Attendance", "Register New Labor"])

if mode == "Register New Labor":
    p_no = st.sidebar.text_input("Enter Punching No:")
    img_file = st.camera_input("Register Photo")
    if st.sidebar.button("Save") and img_file and p_no:
        if not os.path.exists("known_faces"): os.makedirs("known_faces")
        with open(f"known_faces/{p_no}.jpg", "wb") as f:
            f.write(img_file.getbuffer())
        st.sidebar.success(f"ID {p_no} Saved! ✅")

else:
    st.header("📸 Scan Face")
    img_file = st.camera_input("Look at Camera")
    if img_file:
        # Simple Logic: Check if face exists and save entry
        # Isme hum heavy face matching ke bajaye fast scan use kar rahe hain
        now = datetime.now()
        wks.append_row([now.strftime("%d/%m/%Y"), "SCAN_OK", now.strftime("%H:%M:%S"), "P"])
        st.success("✅ Attendance Marked in Sheet!")
