
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.utils import secure_filename
from app.models import User
from app.qa import get_best_answer
import time

main = Blueprint("main", __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route("/")
def home():
    try:
        with sqlite3.connect("db_web.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM colleges ORDER BY CID DESC LIMIT 6")
            colleges = cur.fetchall()
    except Exception as e:
        colleges = []
        print(f"❌ Error loading colleges: {e}")

    return render_template("home.html", datas=colleges)


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username, password)
        if user.save():
            session["user"] = username
            return redirect(url_for("main.dashboard"))
        flash("Username already exists", "danger")
    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.authenticate(username, password):
            session["user"] = username
            return redirect(url_for("main.dashboard"))
        flash("Invalid login credentials", "danger")
    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))


@main.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")


@main.route("/add_college", methods=["GET", "POST"])
def add_college():
    if "user" not in session:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        cname = request.form["cname"]
        dname = request.form["dname"]
        summary = request.form["summary"]
        contact = request.form["contact"]

        image = request.files.get("image_file")
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = image_path
        else:
            image_url = ""

        with sqlite3.connect("db_web.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO colleges (CNAME, DNAME, IMAGE, SUMMARY, CONTACT) VALUES (?, ?, ?, ?, ?)",
                        (cname, dname, image_url, summary, contact))
            con.commit()

        flash("College added successfully!", "success")
        return redirect(url_for("main.admin_college_list"))

    return render_template("add_college.html")


@main.route("/admin/colleges")
def admin_college_list():
    if "user" not in session:
        return redirect(url_for("main.login"))

    with sqlite3.connect("db_web.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM colleges ORDER BY CID DESC")
        colleges = cur.fetchall()
    return render_template("colleges.html", colleges=colleges)


@main.route("/colleges")
def college_list():
    keyword = request.args.get("q", "").strip().lower()

    try:
        with sqlite3.connect("db_web.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            if keyword:
                cur.execute("""
                    SELECT * FROM colleges
                    WHERE LOWER(CNAME) LIKE ? OR LOWER(DNAME) LIKE ?
                    ORDER BY CID DESC
                """, (f"%{keyword}%", f"%{keyword}%"))
            else:
                cur.execute("SELECT * FROM colleges ORDER BY CID DESC")
            colleges = cur.fetchall()
    except Exception as e:
        flash(f"Error loading colleges: {e}", "danger")
        colleges = []

    return render_template("college_list.html", colleges=colleges, keyword=keyword)


@main.route("/college/<int:college_id>")
def college_detail(college_id):
    try:
        with sqlite3.connect("db_web.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM colleges WHERE CID = ?", (college_id,))
            college = cur.fetchone()
            if not college:
                flash("College not found.", "warning")
                return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"Error loading college: {e}", "danger")
        return redirect(url_for('main.home'))

    return render_template("college_detail.html", college=college)

@main.route("/college/edit/<int:college_id>", methods=["GET", "POST"])
def edit_college(college_id):
    if "user" not in session:
        return redirect(url_for("main.login"))

    with sqlite3.connect("db_web.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        if request.method == "POST":
            cname = request.form["cname"]
            dname = request.form["dname"]
            summary = request.form["summary"]
            contact = request.form["contact"]

            cur.execute("""
                UPDATE colleges
                SET CNAME = ?, DNAME = ?, SUMMARY = ?, CONTACT = ?
                WHERE CID = ?
            """, (cname, dname, summary, contact, college_id))

            con.commit()
            flash("College updated successfully!", "success")
            return redirect(url_for("main.admin_college_list"))

        # GET request: عرض تفاصيل الكلية
        cur.execute("SELECT * FROM colleges WHERE CID = ?", (college_id,))
        college = cur.fetchone()
        if not college:
            flash("College not found.", "warning")
            return redirect(url_for("main.admin_college_list"))

    return render_template("edit_college.html", college=college)



@main.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question")
    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    try:
        start = time.time()
        answer = get_best_answer(user_question)
        elapsed = time.time() - start
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "answer": answer,
        "time_taken": f"{elapsed:.3f} seconds"
    })
