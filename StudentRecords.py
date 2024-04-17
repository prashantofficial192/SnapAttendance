from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

student_records_app = Blueprint("student_records", __name__)


# Function to fetch data from the database
def get_student_records(search_term=None):
    try:
        # Connect to the database
        connection = sqlite3.connect("snapattendance.db")
        cursor = connection.cursor()

        # Query to select records based on the search term
        query = "SELECT * FROM students_record"
        if search_term:
            query += f" WHERE student_id LIKE '{search_term}%'"

        cursor.execute(query)

        # Fetch all records
        records = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        return records

    except Exception as e:
        # Handle any exceptions that may occur
        print("Error:", str(e))
        return []


# Route to render the HTML file and pass data to it
@student_records_app.route("/student_records", methods=["GET", "POST"])
def student_records():
    if request.method == "POST":
        # If the form is submitted, handle the search request
        search_term = request.form.get("search_term")
        # Redirect to the same route to avoid resubmission on refresh
        return redirect(
            url_for("student_records.student_records", search_term=search_term)
        )

    # If it's a GET request, or if the form is not submitted, render the template with records
    search_term = request.args.get("search_term")
    records = get_student_records(search_term)
    return render_template(
        "StudentRecords.html", records=records, search_term=search_term
    )
