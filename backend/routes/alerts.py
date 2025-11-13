from flask import Blueprint, request, jsonify
from db import db
from models import Alert, AlertRecipient, StudentIncidentReport, User, SavedItem

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

# Returns list of users depending on audience (by semester or all)
def _pick_recipients(audience_type, semester=None):
    if audience_type == "semester":
        if not semester:
            return []

        fragment = f'"semester": "{semester}"'
        users = (
            db.session.query(User)
            .join(SavedItem, SavedItem.user_id == User.id)
            .filter(
                SavedItem.item_type == "course",
                SavedItem.item_metadata.contains(fragment),
            )
            .distinct()
            .all()
        )
        return [{"user_id": u.id, "user_email": u.email} for u in users]
    return [{"user_id": u.id, "user_email": u.email} for u in User.query.all()]

# Create alert based on an existing student incident report 
@alerts_bp.post("/from-report/<int:report_id>")
def create_alert_from_report(report_id):
    data = request.get_json(force=True)
    report = StudentIncidentReport.query.get_or_404(report_id)

    audience_type = data.get("audience_type") or "semester"
    semester = (data.get("semester") or "").strip()

    if audience_type == "semester" and not semester:
        return jsonify({"error": "semester is required for semester audience"}), 400

    # Create a new alert object
    alert = Alert(
        created_by=data.get("created_by"),
        severity=data.get("severity"),
        audience_type=audience_type,      
        course_code=semester,             
        title=data.get("title") or report.title,
        message=data.get("message") or report.description,
        source_report_id=report.id,
    )
    db.session.add(alert)
    db.session.flush()

    # Pick recipients by semester enrollment
    recipients = _pick_recipients(audience_type, semester=semester)
    db.session.bulk_save_objects([
        AlertRecipient(alert_id=alert.id, user_id=r["user_id"], user_email=r["user_email"])
        for r in recipients
    ])

    # Remove the original incident from the queue
    db.session.delete(report)
    db.session.commit()

    return jsonify({"alert_id": alert.id, "recipient_count": len(recipients)}), 201

# Return list of recipients for chosen alert 
@alerts_bp.get("/<int:alert_id>/recipients")
def list_alert_recipients(alert_id):
    recips = AlertRecipient.query.filter_by(alert_id=alert_id).all()
    return jsonify([{
        "user_id": r.user_id,
        "email": r.user_email,
        "delivered": r.delivered,
        "delivered_at": r.delivered_at.isoformat() if r.delivered_at else None
    } for r in recips])
