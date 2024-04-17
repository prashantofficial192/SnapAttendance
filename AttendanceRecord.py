from flask import Blueprint, render_template, request
import sqlite3

attendance_records_app = Blueprint("attendance_records", __name__)


# Function to fetch all attendance records
def fetch_all_attendance_records():
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # SQL query to fetch all attendance records
    query = """
    SELECT * FROM attendance_entry
    """

    cursor.execute(query)
    records = cursor.fetchall()

    conn.close()
    return records


# Function to fetch attendance records based on student ID
def fetch_attendance_records(student_id):
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # SQL query to fetch attendance records for the given student ID
    query = """
    SELECT * FROM attendance_entry
    WHERE student_id = ?
    """

    cursor.execute(query, (student_id,))
    records = cursor.fetchall()

    conn.close()
    return records


# Route to handle attendance records
@attendance_records_app.route("attendance_records", methods=["GET", "POST"])
def attendance_records():
    if request.method == "POST":
        search_term = request.form.get("search_term")
        records = fetch_attendance_records(search_term)
        return render_template(
            "AttendanceRecord.html", records=records, search_term=search_term
        )

    # Fetch all records when the page is initially loaded
    records = fetch_all_attendance_records()
    return render_template("AttendanceRecord.html", records=records, search_term=None)
