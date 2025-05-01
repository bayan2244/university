# app/__init__.py
from flask import Flask
from app.models import User

def create_app():
    app = Flask(__name__)
    app.secret_key = "admin123"

    # أنشئ جدول المستخدمين تلقائيًا
    User.create_table()

    from app.routes import main
    app.register_blueprint(main)

    return app
