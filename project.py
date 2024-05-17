
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import mysql.connector
import tkinter as tk
from PIL import ImageTk, Image
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

db = mysql.connector.connect(user='majd', password='12345', host='localhost', database='university_database')
cursor = db.cursor()

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

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Function to query the database and get the details for a given name
def get_student_details(name):
    query = "SELECT University_ID, year, section FROM students WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result

# Function to insert attendance record to the database
def insert_attendance_record(university_id, name, year, section):
    now = datetime.now()
    stString = now.strftime('%H:%M:%S')
    attendance_data = f"{university_id},{name},{year},{section},{stString}"

    with open("Attendance.csv", "a") as f:  # Use "a" mode to append data to the file
        f.write(f"{attendance_data}\n")
encodeListKnown = findEncodings(images)
print('encoding complete')
cap = cv2.VideoCapture(0)
known_faces = []
stop_detection = False
# Create the Tkinter window
window = tk.Tk()
window.title("Face Detection")
window.geometry("900x700")
# Create a label to display the webcam feed
label = tk.Label(window)
label.pack()
# Create a label to display the detected person's information
info_label = tk.Label(window, text="No Face Detected")
info_label.pack()
# Callback function for the stop button
def stop_detection_callback():
    global stop_detection
    stop_detection = not stop_detection

# Create the stop button
stop_button = tk.Button(window, text="Stop/Start Detection", command=stop_detection_callback)
stop_button.pack()

# Create a function to exit the program
def exit_program():
    window.destroy()

# Create the exit button
exit_button = tk.Button(window, text="Exit", command=exit_program)
exit_button.pack()

def create_pdf():
    doc = SimpleDocTemplate("Attendance_Report.pdf", pagesize=letter)
    elements = []

    # استرجاع البيانات من ملف CSV
    data = []
    with open("Attendance.csv", "r") as f:
        for line in f:
            data.append(line.strip().split(","))
    
    header = ["University ID", "Name", "Year", "Department","Time"]
    data.insert(0, header)
    # إنشاء جدول من البيانات
    table = Table(data)

    # تطبيق أنماط على الجدول
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    # إضافة الجدول إلى العناصر
    elements.append(table)

    # إنشاء ملف PDF
    doc.build(elements)
    info_label.config(text="PDF report generated successfully.")

pdf_button = tk.Button(window, text="Generate PDF Report", command=create_pdf)
pdf_button.pack()



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
                
                

            info_label.config(text=f"Name: {name}\nUniversity ID: {student_details[0]} \nYear: {student_details[1]} \nSection: {student_details[2]} ")
        else:
            info_label.config(text="No Face Detected") 

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    label.img = img
    label.config(image=img) 

    window.after(10, update_frame) 

# Start the webcam feed and update the frame
update_frame()

# Start the Tkinter event loop
window.mainloop()

