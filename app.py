import cv2
import numpy as np
import os
import pyrebase
from datetime import datetime

# Firebase configuration
config = {
    "apiKey": "AIzaSyCZE61YtZWt_lMaZiOq6ANFvLCyrNWYVEQ",
    "authDomain": "sanket-e9152.firebaseapp.com",
    "databaseURL": "https://iotpro-ea2f4-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "sanket-e9152",
    "storageBucket": "sanket-e9152.appspot.com",
    "messagingSenderId": "47809698488",
    "appId": "1:47809698488:web:753c4c7fe364de610e324d"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
database = firebase.database()

# Haar cascade file and dataset
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'

print('Training...')

# Initialize variables
(images, labels, names, id) = ([], [], {}, 0)

# Load images and labels
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir  # Map subdir names to labels
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            label = id
            images.append(cv2.imread(path, 0))  # Load image in grayscale
            labels.append(int(label))  # Store the label
        id += 1  # Increment id for the next person

# Convert lists to numpy arrays
(images, labels) = [np.array(lst) for lst in [images, labels]]

# Initialize the LBPHFaceRecognizer
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# Load the Haar cascade
face_cascade = cv2.CascadeClassifier(haar_file)

# Initialize webcam
webcam = cv2.VideoCapture(0)

# Post data to Firebase
def post_to_firebase(person_name, confidence):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "Person": person_name,
        "Confidence": confidence,
        "Timestamp": timestamp
    }
    try:
        database.child("Face_Recognition").set(data)
        print("Data posted to Firebase:", data)
    except Exception as e:
        print("Failed to post data to Firebase:", e)

# Monitor and post changes
last_posted_confidence = None

while True:
    ret, im = webcam.read()
    if not ret:
        print("Failed to capture image")
        break

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    current_confidence = 0  # Default confidence
    person_name = "No face detected"  # Default person name if no face is detected

    for (x, y, w, h) in faces:
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (130, 100))
        prediction = model.predict(face_resize)

        if prediction[1] < 100:  # If recognized
            person_name = names[prediction[0]]
            current_confidence = prediction[1]
            cv2.putText(im, f"{person_name} - {prediction[1]:.0f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            print(f"{person_name} recognized, Confidence: {prediction[1]:.0f}")

            # Exit loop when "kavin" is detected
            if person_name == "kavin":
                print("Kavin detected. Exiting program...")
                post_to_firebase(person_name, current_confidence)
                webcam.release()
                cv2.destroyAllWindows()
                exit()  # Exit the program immediately
        else:
            person_name = "Unknown"
            cv2.putText(im, person_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            print("Unknown person detected")

        # Draw rectangle around the face
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Post to Firebase only if confidence changes8
    if current_confidence != last_posted_confidence:
        post_to_firebase(person_name, current_confidence)
        last_posted_confidence = current_confidence

    # Show the webcam feed
    cv2.imshow("Face Recognition", im)

    # Press 'Esc' to exit
    if cv2.waitKey(10) & 0xFF == 27:
        break

# Release resources
webcam.release()
cv2.destroyAllWindows()
