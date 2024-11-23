import cv2
import os

haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'
sub_data = input("Enter the name:")
path = os.path.join(datasets, sub_data)

# Create the directory if it doesn't exist
if not os.path.isdir(path):
    os.makedirs(path)

(width, height) = (130, 100)
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)  # Camera initialization, use 0 for the default camera

count = 1
while count < 51:
    print(count)
    ret, im = webcam.read()
    if not ret:
        print("Failed to capture image")
        break

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        cv2.imwrite(f'{path}/{count}.png', face_resize)
        count += 1

    cv2.imshow('OpenCV', im)
    key = cv2.waitKey(10)
    if key == 27:  # Press 'ESC' to exit
        break

webcam.release()
cv2.destroyAllWindows()
