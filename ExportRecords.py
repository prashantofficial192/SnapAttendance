from flask import Blueprint, render_template, request, Response
import sqlite3
import csv
from io import StringIO

export_records_app = Blueprint("export_records", __name__)


# Render ExportRecords.html template
@export_records_app.route("/")
def export_records():
    return render_template("ExportRecords.html")


# New route for exporting records as CSV
@export_records_app.route("/export_csv", methods=["POST"])
def export_csv():
    # Get the student ID range from the form
    from_id = request.form.get("from")
    to_id = request.form.get("to")

    # Fetch records from the database based on the student ID range
    records = fetch_records_from_db(from_id, to_id)

    # Create a CSV file in memory
    csv_data = generate_csv(records)

    # Return the CSV file as a response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=studentrecords.csv"},
    )


# Your existing functions go here...


# New function to fetch records from the database based on the student ID range
def fetch_records_from_db(from_id, to_id):
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # Fetch records from students_record table based on the student ID range
    cursor.execute(
        "SELECT * FROM students_record WHERE student_id BETWEEN ? AND ?",
        (from_id, to_id),
    )
    records = cursor.fetchall()

    conn.close()

    return records


# New function to generate CSV data from records
def generate_csv(records):
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    # Write header to CSV file
    csv_writer.writerow(
        [
            "id",
            "student_id",
            "student_name",
            "student_dob",
            "roll_number",
            "student_class",
            "student_division",
            "email",
            "phone",
        ]
    )

    # Write records to CSV file
    csv_writer.writerows(records)

    return csv_data.getvalue()


@export_records_app.route("/export_attendance_csv", methods=["POST"])
def export_attendance_csv():
    # Get the student ID and date from the form
    student_id = request.form.get("studentID")
    attendance_date = request.form.get("attendanceDate")

    # Fetch attendance records from the database based on the student ID and date
    attendance_records = fetch_attendance_records_from_db(student_id, attendance_date)

    # Create a CSV file in memory
    csv_data = generate_attendance_csv(attendance_records)

    # Return the CSV file as a response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=attendance_records.csv"},
    )


# New function to fetch attendance records from the database based on the student ID and date
def fetch_attendance_records_from_db(student_id, attendance_date):
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # Fetch attendance records from attendance_entry table based on the student ID and date
    cursor.execute(
        "SELECT * FROM attendance_entry WHERE student_id = ? AND date(entry_time) = ?",
        (student_id, attendance_date),
    )
    attendance_records = cursor.fetchall()

    conn.close()

    return attendance_records


# New function to generate CSV data from attendance records
def generate_attendance_csv(attendance_records):
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    # Write header to CSV file
    csv_writer.writerow(
        [
            "id",
            "student_id",
            "entry_time",
            "status",
            "recognize",
            "subject",
            "teacher_name",
        ]
    )

    # Write attendance records to CSV file
    csv_writer.writerows(attendance_records)

    return csv_data.getvalue()


@export_records_app.route("/export_class_div_csv", methods=["POST"])
def export_class_div_csv():
    # Get the student ID range and date from the form
    from_id = request.form.get("from2")
    to_id = request.form.get("to2")
    selected_date = request.form.get("dateSelect")

    # Fetch records from the database based on the student ID range and date
    records = fetch_class_div_records_from_db(from_id, to_id, selected_date)

    # Create a CSV file in memory
    csv_data = generate_attendance_csv(records)  # Use the correct function here

    # Return the CSV file as a response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=class_div_records.csv"},
    )

# New function to fetch records by class and division from the database based on the student ID range and date
def fetch_class_div_records_from_db(from_id, to_id, selected_date):
    conn = sqlite3.connect("snapattendance.db")
    cursor = conn.cursor()

    # Fetch records from attendance_entry table based on the student ID range and date
    cursor.execute(
        "SELECT * FROM attendance_entry WHERE student_id BETWEEN ? AND ? AND date(entry_time) = ?",
        (from_id, to_id, selected_date),
    )
    records = cursor.fetchall()

    conn.close()

    return records

