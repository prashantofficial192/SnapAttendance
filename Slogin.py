from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3  

slogin = Blueprint('slogin', __name__)


@slogin.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return redirect(url_for("student_login"))
    return render_template("Slogin.html", message="")


# Function to get the database connection
def get_connection():
    try:
        connection = sqlite3.connect("snapattendance.db", check_same_thread=False)
        return connection
    except sqlite3.Error as e:
        print(e)
    return None


# Function to check student login credentials
def check_student_login(connection, student_id, roll_number):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM students_record WHERE student_id = ? AND roll_number = ?"
        cursor.execute(query, (student_id, roll_number))
        student = cursor.fetchone()
        return student  # Return the student details if login is successful
    except sqlite3.Error as e:
        print(f"Error checking login credentials: {e}")
        return None


# Route for handling student login
@slogin.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        connection = get_connection()

        if connection:
            student_id = request.form.get("sid")
            roll_number = request.form.get("roll")

            # Check student login credentials
            student = check_student_login(connection, student_id, roll_number)

            if student:
                return redirect(
                    url_for(
                        "slogin.student_dashboard",
                        success_message="Login successful",
                        student_id=student_id,
                    )
                )
            else:
                return render_template("Slogin.html", message="Invalid credentials")

        return render_template("Slogin.html")

    return render_template("Slogin.html")


@slogin.route("/student-dashboard")
def student_dashboard():
    success_message = request.args.get("success_message", None)
    student_id = request.args.get("student_id", None)

    if success_message and student_id:
        # Fetch student details from the students_record table
        connection = get_connection()
        cursor = connection.cursor()
        student_query = "SELECT * FROM students_record WHERE student_id = ?"
        cursor.execute(student_query, (student_id,))
        student_details = cursor.fetchone()

        # Fetch recent attendance records for the student from the attendance_entry table
        recent_records_query = "SELECT * FROM attendance_entry WHERE student_id = ? ORDER BY entry_time DESC LIMIT 8"
        cursor.execute(recent_records_query, (student_id,))
        recent_records = cursor.fetchall()
        
        total_lectures = 8
        attendance_count = sum(1 for record in recent_records if record[3] == 'Present')
        
        attendance_percentage = (attendance_count / total_lectures) * 100 if total_lectures > 0 else 0

        # Close the connection
        connection.close()

        # Check if the student details are found
        if student_details:
            # Unpack the fetched data from the tuple
            student_name, roll_number, student_class, student_division = (
                student_details[2],
                student_details[4],
                student_details[5],
                student_details[6],
            )

            # Render the template with the fetched data
            return render_template(
                "Sdashboard.html",
                success_message=success_message,
                student_id=student_id,
                student_name=student_name,
                roll_number=roll_number,
                student_class=student_class,
                student_division=student_division,
                recent_records=recent_records,
                attendance_count=attendance_count,
                attendance_percentage=attendance_percentage,
            )       
        else:
            # Redirect to login if student details are not found
            return redirect(url_for("student_login"))
    else:
        # Redirect to login if missing parameters
        return redirect(url_for("student_login"))
    
@slogin.route("/logout")
def logout():
    # You can perform any additional logout logic here if needed
    return redirect(url_for("student_login"))