import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def mark_attendance(name):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    csv_filename = f"{current_date}.csv"

    if not os.path.exists(csv_filename):
        with open(csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Name', 'Date'])

    with open(csv_filename, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if row[0] == name and row[1] == current_date:
                messagebox.showinfo("Attendance Error", f"Attendance for {name} on {current_date} already exists!")
                return

    with open(csv_filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([name, current_date])

    messagebox.showinfo("Attendance Marked", f"{name} marked as present on {current_date}!")

def display_attendance():
    def filter_attendance():
        selected_name = name_combobox.get()
        selected_date = date_combobox.get()

        filtered_data = []
        with open(csv_filename, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if (selected_name == "All" or row[0] == selected_name) and (selected_date == "All" or row[1] == selected_date):
                    filtered_data.append(row)

        text_widget.delete('1.0', tk.END)
        for row in filtered_data:
            text_widget.insert(tk.END, f"Name: {row[0]}, Date: {row[1]}\n")

    attendance_window = tk.Tk()
    attendance_window.title("Attendance Checker")

    with open(csv_filename, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        data = [row for row in csv_reader]

    names = ["All"] + sorted(set(row[0] for row in data))
    dates = ["All"] + sorted(set(row[1] for row in data))

    name_label = tk.Label(attendance_window, text="Filter by Name:")
    name_label.pack()
    name_combobox = ttk.Combobox(attendance_window, values=names, state="readonly")
    name_combobox.set("All")
    name_combobox.pack()

    date_label = tk.Label(attendance_window, text="Filter by Date:")
    date_label.pack()
    date_combobox = ttk.Combobox(attendance_window, values=dates, state="readonly")
    date_combobox.set("All")
    date_combobox.pack()

    filter_button = tk.Button(attendance_window, text="Filter", command=filter_attendance)
    filter_button.pack()

    text_widget = tk.Text(attendance_window)
    text_widget.pack()

    for row in data:
        text_widget.insert(tk.END, f"Name: {row[0]}, Date: {row[1]}\n")

    attendance_window.mainloop()

video_capture = cv2.VideoCapture(0)

known_face_encodings = []
known_faces_names = []

known_faces = {
    "garv": "photos/garv.jpg",
    "surbhi": "photos/surbhi.jpg",
    "payal": "photos/payal.jpg"
}

for name, image_path in known_faces.items():
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_faces_names.append(name)

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
csv_filename = f"{current_date}.csv"

attendance_recorded = False

while not attendance_recorded:
    ret, frame = video_capture.read()

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            matched_index = np.argmax(matches)
            name = known_faces_names[matched_index]
            mark_attendance(name)
            attendance_recorded = True
        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Attendance System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

display_attendance()
