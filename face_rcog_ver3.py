import cv2
from pymongo import MongoClient
import pymongo as pymongo
import speech_recognition as sr
import pyttsx3
import pyaudio as pyaudio
import easygui

# define the connection string
MONGO_CONNECTION_STRING = "mongodb+srv://"
# create a MongoClient object and pass the connection string
client = MongoClient(MONGO_CONNECTION_STRING)

# create a database named "attendance_system"
db = client["attendance_system"]

# create a collection named "attendance"
attendance_collection = db["attendance"]

# function to insert a document in the "attendance" collection
def add_attendance(name):
    engine= pyttsx3.init()
    attendance = {"name": name}
    if name == "" or name is None:
        engine.say("Program Terminated.")
        engine.runAndWait()
        exit(0)
    existing_attendance = attendance_collection.find_one({"name": name})
    if existing_attendance:
        with sr.Microphone() as source:
            engine.say("Attendence already added for")
            engine.say(name)
            engine.runAndWait()
            easygui.msgbox("Attendance already added for " + name, title="Attendance")
    else:
        attendance_collection.insert_one(attendance)
        with sr.Microphone() as source:
            engine.say("Attendence Added for")
            engine.say(name)
            engine.runAndWait()
            easygui.msgbox("Attendance added for " + name, title="Attendance")

# function to create a connection with the MongoDB cluster
def create_connection():
    try:
        client.admin.command('ping')
        print("Connected to MongoDB Atlas")
    except pymongo.errors.ConnectionFailure:
        print("Failed to connect to MongoDB Atlas")

# function to capture image and detect face
def detect_face():
    # capture frames from a camera
    cap = cv2.VideoCapture(0)
    face_count = 0

    # load the required trained XML classifiers
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml') 

    #Intializing the Speech Recognizer and Text to speech Engine
    r= sr.Recognizer()
    engine= pyttsx3.init()

    # initialize a variable to keep track of the number of faces detected
    num_faces_detected = 0

    # loop runs if capturing has been initialized.
    while True:
        # check if the required number of faces have been detected
        if num_faces_detected == 1:
            break
        ret, img = cap.read() 
  
        # convert to gray scale of each frames
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
        # Detects faces of different sizes in the input image
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # loop through each face detected
        for (x, y, w, h) in faces:
            # To draw a rectangle in a face 
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2) 
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            face_count += 1
  
            # Detects eyes of different sizes in the input image
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5)
  
            #To draw a rectangle in eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 127, 255), 2)

            if face_count > 100:
                with sr.Microphone() as source:
                    engine.say("Please enter your name")
                    engine.runAndWait()

                # get the name of the person from the user via voice input
                name = easygui.enterbox("Please enter your name:", title="Enter Name")
                
                # add the name to the attendance database
                add_attendance(name)
                num_faces_detected += 1

        # Display an image in a window
        cv2.imshow('img', img)

        # Wait for Esc key to stop
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    # Close the window
    cap.release()
  
    # De-allocate any associated memory usage
    cv2.destroyAllWindows()

# create a connection with the MongoDB Atlas cluster
create_connection()

# detect face and take attendance
detect_face()
