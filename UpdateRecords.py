from flask import Blueprint, render_template, request, jsonify
import sqlite3

update_records_app = Blueprint("update_records_app", __name__)


def fetch_student_data(student_id):
    connection = sqlite3.connect("snapattendance.db")
    cursor = connection.cursor()

    # Fetch student data based on student_id
    cursor.execute("SELECT * FROM students_record WHERE student_id = ?", (student_id,))
    student_data = cursor.fetchone()

    connection.close()

    return student_data

# Function to update student record in the database
def update_student_record_in_db(data):
    connection = sqlite3.connect("snapattendance.db")
    cursor = connection.cursor()

    # Update student record in the database
    cursor.execute(
        """
        UPDATE students_record
        SET student_name=?, student_dob=?, roll_number=?, student_class=?,
            student_division=?, email=?, phone=?
        WHERE student_id=?
    """,
        (
            data["student_name"],
            data["student_dob"],
            data["roll_number"],
            data["student_class"],
            data["student_division"],
            data["email"],
            data["phone"],
            data["student_id"],
        ),
    )

    connection.commit()
    connection.close()

def delete_student_record_from_db(student_id):
    connection = sqlite3.connect("snapattendance.db")
    cursor = connection.cursor()

    # Delete student record from the database
    cursor.execute("DELETE FROM students_record WHERE student_id = ?", (student_id,))

    connection.commit()
    connection.close()


@update_records_app.route("/update_records")
def update_records_form():
    return render_template("UpdateRecords.html")


@update_records_app.route("/fetch_student_data", methods=["POST"])
def fetch_student_data_route():
    student_id = request.form.get("student_id")
    student_data = fetch_student_data(student_id)

    # Return the student data as JSON
    return jsonify(student_data)


@update_records_app.route("/update_student_record", methods=["POST"])
def update_student_record():
    try:
        data = request.get_json()

        # Check if the received data is in the correct format
        if not all(
            key in data
            for key in [
                "student_id",
                "student_name",
                "student_dob",
                "roll_number",
                "student_class",
                "student_division",
                "email",
                "phone",
            ]
        ):
            raise ValueError("Invalid data format")

        update_student_record_in_db(data)

        # Return a success message
        return jsonify({"message": "Student record updated successfully"})
    except Exception as e:
        # Return an error message if an exception occurs
        return jsonify({"error": str(e)}), 500



@update_records_app.route("/delete_student_record", methods=["POST"])
def delete_student_record():
    # Implement the logic to delete the student record from the database
    student_id = request.form.get("student_id")
    delete_student_record_from_db(student_id)

    # Return a success message
    return jsonify({"message": "Student record deleted successfully"})
