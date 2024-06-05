def update_frame():
    success, img = cap.read()
    smallImg = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    smallImg = cv2.cvtColor(smallImg, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(smallImg)
    encodesCurFrame = face_recognition.face_encodings(smallImg, facesCurFrame) 

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        if stop_detection:
            break 

        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDistance)
        matchIndex = np.argmin(faceDistance) 

        if not any(matches):
            name = "Unknown"
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            info_label.config(text="Unknown")

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4 

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2) 

            student_details = list(get_student_details(name))
            print(student_details)
            if student_details and name not in known_faces:
                university_id, year, section = student_details
                known_faces.append(name)
                insert_attendance_record(university_id, name, year, section) 
              