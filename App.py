from flask import Flask, render_template, redirect, url_for, request, jsonify
import sqlite3
from Slogin import slogin
from attendance import attendance_bp
from AddStudent import AddStudent
from webcam_capture import webcam_capture_app
from UpdateRecords import update_records_app
from StudentRecords import student_records_app
from AttendanceRecord import attendance_records_app
from ExportRecords import export_records_app

app = Flask(__name__)
DATABASE = "snapattendance.db"

app.register_blueprint(slogin, url_prefix="/slogin")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(AddStudent, url_prefix="/add_student")
app.register_blueprint(webcam_capture_app, url_prefix="/webcam_capture_app")
app.register_blueprint(update_records_app, url_prefix="/update_records")
app.register_blueprint(student_records_app, url_prefix="/student_records")
app.register_blueprint(attendance_records_app, url_prefix="/attendance_records")
app.register_blueprint(export_records_app, url_prefix="/export_records")


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/login")
def login():
    # Redirect to the Role page when the user clicks on Login
    return redirect(url_for("role_page"))


@app.route("/role")
def role_page():
    return render_template("Role.html")


@app.route("/student_login")
def student_login():
    # Add logic for handling student login
    return render_template("Slogin.html")


@app.route("/teacher_login")
def teacher_login():
    # Add logic for handling teacher login
    return render_template("Tlogin.html")


@app.route("/teacher_dashboard")
def teacher_dashboard():
    # Add any necessary logic here
    return render_template("Tactions.html")


@app.route("/attendance")
def attendance_app():
    return render_template("TakeAttendance.html")


@app.route("/add_student")
def add_student():
    return render_template("AddStudent.html")


@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        try:
            # Get form data
            student_id = request.form.get("StudentID")
            roll_number = request.form.get("rollNumber")
            student_name = request.form.get("StudentName")
            student_dob = request.form.get("StudentDOB")
            student_class = request.form.get("StudentClass")
            student_division = request.form.get("StudentDivision")
            email = request.form.get("email")
            phone = request.form.get("phone")

            # Insert data into the database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO students_record (
                    student_id, student_name, student_dob, roll_number,
                    student_class, student_division, email, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    student_name,
                    student_dob,
                    roll_number,
                    student_class,
                    student_division,
                    email,
                    phone,
                ),
            )

            conn.commit()
            conn.close()

            return jsonify(
                {"status": "success", "message": "Student added successfully"}
            )

        except sqlite3.IntegrityError as e:
            return jsonify(
                {
                    "status": "error",
                    "message": "Duplicate entry for Student ID or Roll Number",
                }
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})


@app.route("/webcam_capture_app/")
def webcam_capture_app():
    return render_template("Capture.html")


@app.route("/update_records")
def update_records():
    return render_template("UpdateRecords.html")


@app.route("/student_records")
def student_records():
    return render_template("StudentRecords.html")


@app.route("/attendance_records")
def attendance_records():
    return render_template("AttendanceRecord.html")


@app.route("/export_records")
def export_records():
    return render_template("ExportRecords.html")


if __name__ == "__main__":
    app.run(debug=True)
