#step1
import cv2
import numpy as np
import face_recognition
import os

path = 'images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)   
#step 2
def findEncodings (images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)    
print('encoding complete') 
#step 3
cap = cv2.VideoCapture(0)

while True:
    success , img = cap.read()
    smallImg = cv2.resize(img , (0,0), None,0.25,0.25)
    smallImg = cv2.cvtColor(smallImg, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(smallImg)
    encodesCurFrame = face_recognition.face_encodings(smallImg,facesCurFrame)


    for encodeFace , faceLoc in zip(encodesCurFrame,facesCurFrame):
        match = face_recognition.compare_faces(encodeListKnown , encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnown , encodeFace)
        print(faceDistance)
        matchIndex = 

