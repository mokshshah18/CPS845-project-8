from flask import Blueprint, request, jsonify
from datetime import datetime
from db import db
from models import StudentIncidentReport

report_incidents_bp = Blueprint("report_incidents", __name__, url_prefix="/api/report-incidents")

# Create new student incident report 
@report_incidents_bp.post("/students")
def create_report_student():
    data = request.get_json(silent=True) or request.form.to_dict()
    reporter_name  = data.get("name") or data.get("reporter_name")
    reporter_email = data.get("email") or data.get("reporter_email")
    reporter_phone = data.get("phone") or data.get("reporter_phone")
    category       = data.get("category")
    title          = data.get("title")
    description    = data.get("description")
    building_name  = data.get("building_name") or data.get("building")
    room_number    = data.get("room_number") or data.get("room")
    lat            = data.get("lat")
    lng            = data.get("lng")

    # Validation
    if not reporter_name or not reporter_email or not category or not title or not description:
        return jsonify({"error": "Missing required fields"}), 400

    # Create the new incident report model
    new_report = StudentIncidentReport(
        reporter_name=reporter_name,
        reporter_email=reporter_email,
        reporter_phone=reporter_phone,
        category=category,
        title=title,
        description=description,
        building_name=building_name,
        room_number=room_number,
        lat=float(lat) if lat else None,
        lng=float(lng) if lng else None,
    )

    # Save to the database
    db.session.add(new_report)
    db.session.commit()

    return jsonify({"message": "Report created", "id": new_report.id}), 201

#Return a list of all incident reports by newest to oldest 
@report_incidents_bp.get("/")
def list_reports():
    reports = StudentIncidentReport.query.order_by(StudentIncidentReport.created_at.desc()).all()
    return jsonify([{
        "id": r.id,
        "created_at": r.created_at.isoformat(),
        "category": r.category,
        "title": r.title,
        "building_name": r.building_name,
        "room_number": r.room_number,
        "lat": r.lat,
        "lng": r.lng
    } for r in reports])

