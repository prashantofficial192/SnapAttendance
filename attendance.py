from flask import Blueprint, render_template, request
import cv2
import sqlite3
import face_recognition
from datetime import datetime
from flask_cors import CORS
from plyer import notification
import numpy as np

attendance_bp = Blueprint(
    "attendance", __name__
)  # Renamed the Blueprint to avoid conflict
CORS(attendance_bp)

CORS(attendance_bp, resources={r"/attendance/take_attendance": {"origins": "*"}})

# Set to store recognized student IDs across the entire session
recognized_students_session = set()

# Set to store recognized student IDs in the current session
recognized_students_current_session = set()


# Function to take attendance
def take_attendance(subject, teacher_name):
    # Connect to the SQLite database
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # Fetch student IDs and photo paths from the students_photo table
    cursor.execute("SELECT student_id, photo_path FROM students_photo")
    rows = cursor.fetchall()

    # Load known face encodings and corresponding student IDs
    known_face_encodings = []
    known_student_ids = []

    # Loop through rows and load known face encodings
    for student_id, photo_path in rows:
        img = face_recognition.load_image_file(photo_path)

        # Check if face encodings are found
        face_encodings = face_recognition.face_encodings(img)
        if face_encodings:
            face_encoding = face_encodings[0]  # Assume only one face per image
            known_face_encodings.append(face_encoding)
            known_student_ids.append(student_id)

    # Connect to the webcam with improved settings
    video_capture = cv2.VideoCapture(0)  # Use 0 for the default webcam
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set the frame width
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set the frame height

    timer_start = None

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Display the current date and time on the top left corner
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, current_time, (10, 30), font, 0.6, (0, 255, 0), 1)

        # Initialize status outside the loop
        status = "Absent"

        # Find all face locations in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Loop through detected faces
        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            # Compare with known face encodings and calculate face distances
            distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )

            # Use np.argmin to find the index of the minimum distance
            min_distance_index = np.argmin(distances)
            min_distance = distances[min_distance_index]

            if min_distance < 0.5:  # Adjust the threshold as needed
                student_id = known_student_ids[min_distance_index]

                # Check if the student has already been recognized in the current session
                if student_id not in recognized_students_current_session:
                    # Mark the student as recognized for the current session
                    recognized_students_current_session.add(student_id)

                    # Check if the student has already been recognized in the entire session
                    if student_id not in recognized_students_session:
                        # Mark the student as recognized for the entire session
                        recognized_students_session.add(student_id)

                        # Insert attendance record into the database
                        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute(
                            """
                            INSERT INTO attendance_entry
                            (student_id, entry_time, status, recognize, subject, teacher_name)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (
                                student_id,
                                entry_time,
                                "Present",
                                "Recognized",
                                subject,
                                teacher_name,
                            ),
                        )

                        notification_title = f"Student {student_id} Attendance"
                        notification_message = (
                            f"Attendance recorded for Student ID: {student_id}"
                        )
                        notification.notify(
                            title=notification_title,
                            message=notification_message,
                            app_icon=None,  # You can provide an icon file path if needed
                            timeout=10,  # Notification timeout in seconds
                        )

                        # Draw rectangle around the face
                        rectangle_color = (255, 0, 0)  # Blue color for recognized faces
                        cv2.rectangle(
                            frame, (left, top), (right, bottom), rectangle_color, 2
                        )

                        # Draw label on the frame for student ID
                        cv2.putText(
                            frame,
                            f"Student ID: {student_id}",
                            (left + 5, bottom + 20),
                            font,
                            0.6,
                            rectangle_color,
                            1,
                        )

                        # Set the status for the frame
                        status = "Present"

                        # Start the timer when a student is recognized
                        timer_start = datetime.now()

            else:
                # Draw rectangle around the unknown face with label "Unknown"
                rectangle_color = (0, 0, 255)  # Red color for unknown faces
                cv2.rectangle(frame, (left, top), (right, bottom), rectangle_color, 2)
                cv2.putText(
                    frame,
                    "Unknown",
                    (left + 5, bottom + 20),
                    font,
                    0.6,
                    rectangle_color,
                    1,
                )

        # Draw labels on the frame for status and recognition on the right side
        cv2.putText(frame, f"Status: {status}", (1000, 50), font, 0.6, (255, 0, 0), 1)
        cv2.putText(
            frame, "Recognition: Recognized", (1000, 80), font, 0.6, (255, 0, 0), 1
        )
        cv2.putText(
            frame, f"Student ID: {student_id}", (1000, 110), font, 0.6, (255, 0, 0), 1
        )

        # Check if the timer has started
        if timer_start:
            # Calculate the elapsed time
            elapsed_time = (datetime.now() - timer_start).total_seconds()

            # If 3 seconds have passed, reset the recognized set for the current session
            if elapsed_time >= 3:
                recognized_students_current_session.clear()
                timer_start = None

        # Commit the changes and close the database connection
        conn.commit()

        # Display the output
        cv2.imshow("Attendance", frame)

        # Check for exit key (press 'q' to exit)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video capture and close the OpenCV window
    video_capture.release()
    cv2.destroyAllWindows()

    # Clear the recognized set at the end of the session
    recognized_students_session.clear()

    # Close the database connection
    conn.close()


# Flask routes


@attendance_bp.route("/attendance")
def index():
    return render_template("TakeAttendance.html")


# New route to handle AJAX request for taking attendance
@attendance_bp.route("/take_attendance", methods=["POST"])
def take_attendance_route():
    print("Take Attendance route reached.")
    subject = request.form.get("subject")
    teacher_name = request.form.get("teacher")
    print(f"Subject: {subject}, Teacher: {teacher_name}")

    # Run the attendance-taking function
    take_attendance(subject, teacher_name)

    return "Attendance taken successfully!", 200
