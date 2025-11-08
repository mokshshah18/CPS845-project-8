from flask import Blueprint, request, jsonify
from models import Location, Path
from sqlalchemy import or_

directions_bp = Blueprint("directions", __name__)

@directions_bp.route("/", methods=["GET"])
def compute_route():
    start_id = request.args.get("start")
    end_id = request.args.get("end")

    if not start_id or not end_id:
        return jsonify({"error": "start and end required"}), 400

    start = Location.query.get(start_id)
    end = Location.query.get(end_id)
    if not start or not end:
        return jsonify({"error": "invalid locations"}), 404

    # Basic placeholder route
    path = Path.query.filter(
        or_(
            (Path.start_id == start.id) & (Path.end_id == end.id),
            (Path.start_id == end.id) & (Path.end_id == start.id),
        )
    ).first()

    steps = [
        f"Start at {start.name}",
        "Walk straight for 200m",
        f"Arrive at {end.name}",
    ]
    if path:
        steps.insert(1, f"Follow the main path for {path.distance} meters")

    return jsonify({"route": {"steps": steps}})
