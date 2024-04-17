#importing libraries and their modules
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
#imported database library
import sqlite3

#creating blueprint for AddStudent for routing
AddStudent = Blueprint("AddStudent", __name__)

#__name__ is a special Python variable that represents the name of the current module. When used as the second argument in the Blueprint constructor, it helps Flask determine the root path for the blueprint's resources (templates, static files, etc.)

# Set your database path
DATABASE = "snapattendance.db"

# creating  a connection to the database
#sqlite3 is a module and cursor() creates cursor object which is used to execute sqlite commands or query

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            student_name TEXT NOT NULL,
            student_dob DATE NOT NULL,
            roll_number TEXT NOT NULL UNIQUE,
            student_class TEXT NOT NULL,
            student_division TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()

# Define the index route to render the AddStudent.html template
@AddStudent.route("/")
def index():
    return render_template("AddStudent.html")

