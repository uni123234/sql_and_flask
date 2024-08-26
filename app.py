"""
This module contains a Flask web application with routes for 
registering participants and viewing registered participants.
"""

import sqlite3
from flask import Flask, g, render_template, request

app = Flask(__name__)

DATABASE = "test_db.db"
CITIES = {
    1: "Kyiv",
    2: "Lviv",
    3: "Khmelnitskiy",
    4: "Kharkiv",
    5: "Dnipro",
}


def get_db():
    """
    Get a database connection for the current Flask app context.
    If the connection does not exist, create a new one.
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enable named column access
    return db


def create_db():
    """
    Create the database and the participants table if they do not exist.
    """
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS participants (
                name TEXT NOT NULL, 
                email TEXT NOT NULL, 
                city INTEGER NOT NULL, 
                order_name TEXT NOT NULL, 
                phone TEXT NOT NULL
            )
        """
        )
        connection.commit()


@app.teardown_appcontext
def close_connection(_):
    """
    Close the database connection at the end of the request context.
    """
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    """
    Render the index page.
    """
    return render_template("index.html")


@app.route("/join/", methods=["GET", "POST"])
def join():
    """
    Render the join form and handle the form submission.
    If the request method is POST, save the form data to the database.
    """
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        city = request.form.get("city")
        phone = request.form.get("phone")
        order = request.form.get("order")

        db = get_db()
        db.execute(
            """
            INSERT INTO participants (name, email, city, phone, order_name) 
            VALUES (?, ?, ?, ?, ?)
        """,
            (name, email, city, phone, order),
        )
        db.commit()

        return render_template("index.html")

    return render_template("join.html", cities=CITIES)


@app.route("/participants/")
def participants():
    """
    Display the list of participants.
    Fetches all participants from the database and passes them to the template.
    """
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM participants")
    data = cursor.fetchall()

    return render_template("participants.html", participants=data, cities=CITIES)


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
