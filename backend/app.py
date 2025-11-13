from flask import Flask
from routes.maps import maps_bp
from flask_cors import CORS
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from db import db
from routes.directions import directions_bp
from routes.locations import locations_bp
from routes.saved_items import saved_items_bp
from routes.user_db import user_db_bp
from routes.report_incidents import report_incidents_bp
from flask import request, jsonify
from models import FacultyUser
from routes.alerts import alerts_bp

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(directions_bp, url_prefix="/api/route")
app.register_blueprint(locations_bp, url_prefix="/api/locations")
app.register_blueprint(maps_bp, url_prefix="/api/maps")
app.register_blueprint(saved_items_bp, url_prefix="/api/saved-items")
app.register_blueprint(user_db_bp, url_prefix="/api/user")
app.register_blueprint(report_incidents_bp)
app.register_blueprint(alerts_bp)

@app.route("/")
def home():
    return {"status": "Campus Navigator API running"}

@app.route("/api/faculty/login", methods=["POST"])
def faculty_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = FacultyUser.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
