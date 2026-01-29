from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
from db import get_db_connection

app = Flask(__name__, template_folder="../templates")
app.config["SECRET_KEY"] = "SMART_FARMER_SECRET"

# ---------------- Root ----------------
@app.route('/')
def root():
    return redirect(url_for("login"))

# ---------------- Home ----------------
@app.route('/index')
def home():
    return render_template("index.html")

# ---------------- Register (JSON) ----------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    try:
        # JSON request (fetch)
        if request.is_json:
            data = request.get_json()
            name = data.get("name")
            mobile = data.get("mobile")
            password = data.get("password")
        else:
            # HTML form submit
            name = request.form.get("name")
            mobile = request.form.get("mobile")
            password = request.form.get("password")

        if not name or not mobile or not password:
            return jsonify({"message": "All fields required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (name, mobile, password, verified, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, mobile, password, False, "farmer"))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Registration successful"}), 200

    except mysql.connector.Error as e:
        print("Database error:", e)
        return jsonify({"message": "User already exists or DB error"}), 400

# ---------------- Login (JSON) ----------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    try:
        # JSON (fetch)
        if request.is_json:
            data = request.get_json()
            mobile = data.get("mobile")
            password = data.get("password")
        else:
            # HTML form submit
            mobile = request.form.get("mobile")
            password = request.form.get("password")

        if not mobile or not password:
            return jsonify({"message": "Mobile and password required"}), 400

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE mobile=%s AND password=%s",
            (mobile, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid mobile or password"}), 401

    except mysql.connector.Error as e:
        print("Login error:", e)
        return jsonify({"message": "Server error during login"}), 500

# ---------------- Example Pages ----------------
@app.route('/crop')
def crop_guidance():
    return render_template("crops.html")

@app.route('/articles')
def articles():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM articles ORDER BY published_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("articles.html", articles=data)

@app.route('/schemes')
def schemes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM schemes")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("Government Schemes.html", schemes=data)

@app.route('/market')
def market():
    return render_template("Market Prices.html")

@app.route('/pest')
def pest():
    return render_template("Pest & Disease.html")

@app.route('/contact-page')
def contact_page():
    return render_template("contact.html")

@app.route('/weather-page')
def weather_page():
    return render_template("weather.html")

@app.route('/crop-calendar')
def crop_calendar():
    return render_template("crop_calendar.html")

@app.route('/crop_videos')
def crop_videos():
    return render_template("farming_video.html")

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)


