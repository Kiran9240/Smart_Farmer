from flask import Flask, render_template, request, redirect, url_for, jsonify
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

# ---------------- Crop Guidance ----------------
@app.route('/crop')
def crop_guidance():
    return render_template("crops.html")

# ---------------- Articles ----------------
@app.route('/articles')
def articles():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM articles ORDER BY published_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("articles.html", articles=data)

# ---------------- Schemes ----------------
@app.route('/schemes')
def schemes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM schemes")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("Government Schemes.html", schemes=data)

# ---------------- Market Prices Page ----------------
@app.route('/market')
def market():
    return render_template("Market Prices.html")

# ---------------- Market Prices API ----------------
@app.route('/prices')
def get_prices():
    crop = request.args.get("crop")
    market = request.args.get("market")
    if not crop or not market:
        return jsonify({"error": "Missing crop or market"})

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.name AS crop,
               TRIM(m.market_location) AS market,
               m.min_price,
               m.max_price
        FROM market_prices m
        JOIN crops c ON m.crop_id = c.id
        WHERE LOWER(c.name) = LOWER(%s)
          AND LOWER(TRIM(m.market_location)) = LOWER(%s)
        ORDER BY m.recorded_at DESC
        LIMIT 1
    """, (crop, market))
    result = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify(result if result else {"crop": crop, "market": market, "min_price": "Not found", "max_price": "Not found"})

# ---------------- Pest & Disease ----------------
@app.route('/pest')
def pest():
    return render_template("Pest & Disease.html")

# ---------------- Register ----------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (name, mobile, password, verified, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, mobile, password, False, "farmer"))
        except mysql.connector.Error as e:
            print("Database error:", e)
            return render_template("register.html", error="Error registering user")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- Login ----------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE mobile=%s AND password=%s", (mobile, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return render_template("index.html", user=user)
        else:
            return render_template("login.html", error="Invalid mobile or password")

    return render_template("login.html")

# ---------------- Contact API ----------------
@app.route('/contact', methods=["POST"])
def contact():
    data = request.get_json()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contacts (name, mobile, message)
            VALUES (%s, %s, %s)
        """, (data.get("name"), data.get("mobile"), data.get("message")))
    except mysql.connector.Error as e:
        print("Error:", e)
        return jsonify({"status": "error"})
    finally:
        cur.close()
        conn.close()

    return jsonify({"status": "ok"})

# ---------------- Contact Page ----------------
@app.route('/contact-page')
def contact_page():
    return render_template("contact.html")

# ---------------- Weather Page ----------------
@app.route('/weather-page')
def weather_page():
    return render_template("weather.html")

# ---------------- Weather API ----------------
@app.route("/weather")
def weather():
    city = request.args.get("city")
    if not city:
        return jsonify({})

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT city, temperature, humidity, `condition`, rain, created_at
        FROM weather_logs
        WHERE LOWER(city)=LOWER(%s)
        ORDER BY created_at DESC
        LIMIT 1
    """, (city,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(data if data else {})

# ---------------- Crop Calendar ----------------
@app.route('/crop-calendar')
def crop__calendar():
    return render_template("crop_calendar.html")

@app.route("/get_crop_data", methods=["GET"])
def get_crop_data():
    crop_name = request.args.get("crop")
    if not crop_name:
        return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT sowing_month, growing_period, harvest_month
        FROM crop_calendar
        WHERE TRIM(LOWER(crop_name)) = TRIM(LOWER(%s))
    """, (crop_name,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)

# ---------------- Crop Videos ----------------
@app.route("/crop_videos")
def crop_videos():
    return render_template("farming_video.html")

@app.route("/videos", methods=["GET"])
def videos():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM videos")
    videos = cur.fetchall()
    cur.close()
    conn.close()

    video_list = []
    for v in videos:
        video_list.append({
    "id": v["id"],
    "crop_type": v["crop_type"],
    "stage": v["stage"],
    "title": v["title"],
    "description": v["description"],
    "video_url": v["video_url"],
    "thumbnail": v["thumbnail"]   # ✅ हे add कर

        })
    return jsonify(video_list)

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)
