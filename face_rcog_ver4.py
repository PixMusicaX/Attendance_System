import cv2
from pymongo import MongoClient
import pymongo
import speech_recognition as sr
import pyttsx3
import pyaudio
import easygui
from datetime import datetime  # Import for timestamp
import os
from dotenv import load_dotenv


load_dotenv()
# Define the connection string
MONGO_CONNECTION_STRING = os.environ['mongo_string']
# Create a MongoClient object and pass the connection string
client = MongoClient(MONGO_CONNECTION_STRING)

# Create a database named "attendance_system"
db = client["attendance_system"]

# Create a collection named "attendance"
attendance_collection = db["attendance"]

def add_attendance(name):
    engine = pyttsx3.init()
    if not name:
        engine.say("Program Terminated.")
        engine.runAndWait()
        return False
    
    # Get the current timestamp
    current_time = datetime.now()

    existing_attendance = attendance_collection.find_one({"name": name, "date": current_time.strftime('%Y-%m-%d')})
    
    if existing_attendance:
        message = f"Attendance already added for {name} today"
    else:
        # Insert both the name and timestamp into the collection
        attendance_collection.insert_one({
            "name": name,
            "timestamp": current_time,  # Store the current timestamp
            "date": current_time.strftime('%Y-%m-%d')  # Store the date separately for easier checking
        })
        message = f"Attendance added for {name}"
    
    engine.say(message)
    engine.runAndWait()
    easygui.msgbox(message, title="Attendance")
    return True

def create_connection():
    try:
        client.admin.command('ping')
        print("Connected to MongoDB Atlas")
        return True
    except pymongo.errors.ConnectionFailure:
        print("Failed to connect to MongoDB Atlas")
        return False

def detect_face():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    engine = pyttsx3.init()
    face_count = 0

    while True:
        ret, img = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            face_count += 1

            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 127, 255), 2)

            if face_count > 100:
                engine.say("Please enter your name")
                engine.runAndWait()
                name = easygui.enterbox("Please enter your name:", title="Enter Name")
                if add_attendance(name):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                face_count = 0

        cv2.imshow('Attendance System', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if create_connection():
        detect_face()
    else:
        print("Exiting due to database connection failure.")
