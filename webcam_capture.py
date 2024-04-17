# cv2 is used to capture images from webcam. it handles all the activities related to webcam
import cv2
import os   
# os used to interact with operating system
import sqlite3
from flask import Blueprint, render_template, request, jsonify
import face_recognition

# Creating a Blueprint for the webcam_capture Flask app
webcam_capture_app = Blueprint("webcam_capture_app", __name__)

def capture_images(student_id, num_images=15):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the webcam")
        return False, {"error": "Unable to access the webcam"}

    folder_path = create_student_folder(student_id)

    #cap is the connection to the webcam or video file.
    #cap.read() captures a frame from the video source.
    #ret is a boolean (True or False) indicating if the frame was captured successfully.
    #frame is the actual image data (frame) from the webcam.
    
    for image_count in range(1, num_images + 1):
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from the webcam")
            return False, {"error": "Failed to capture frame from the webcam"}

        # Save the image
        image_path = os.path.join(folder_path, f"{student_id}_{image_count}.jpg")
        try:
            #cv2.imwrite is a function from the OpenCV (cv2) library that is used to save an image to a file.
            #image_path is the path where the image file will be saved.
            #frame is the image data (frame) that you want to save.
            cv2.imwrite(image_path, frame)
            print(f"Image {image_count} captured for student ID: {student_id}")

            # Store photo path in the database
            db_connection = sqlite3.connect("snapattendance.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "INSERT INTO students_photo (student_id, photo_path) VALUES (?, ?)",
                (student_id, image_path),
            )
            db_connection.commit()
            db_connection.close()

        except Exception as e:
            print(f"Error capturing image: {e}")
            return False, {"error": f"Error capturing image: {e}"}

    cap.release()
    cv2.destroyAllWindows()

    return True, {"success": f"Images captured and stored for student ID: {student_id}"}



# Function to create a folder for a student
def create_student_folder(student_id):
    folder_path = os.path.join("static", "students_photos", student_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


# Route to render the capture page
@webcam_capture_app.route("/")
def index():
    return render_template("Capture.html")


# Route to capture images when the button is pressed
@webcam_capture_app.route("/capture", methods=["POST"])
def capture_images_route():
    student_id = request.form.get("studentId")

    # Check if the student ID exists in the students_record table
    db_connection = sqlite3.connect("snapattendance.db")
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "SELECT * FROM students_record WHERE student_id = ?", (student_id,)
    )
    existing_student = db_cursor.fetchone()
    db_connection.close()

    if existing_student:
        # Run the face capture process for registered students
        success, message = capture_images(student_id)
        if success:
            return jsonify(message)
        else:
            return jsonify(message)
    else:
        # Return a message if the student ID is not found
        return jsonify({"error": "Student not found"})
