from flask import Blueprint, jsonify
from models import Location

locations_bp = Blueprint("locations", __name__)

@locations_bp.route("/", methods=["GET"])
def list_locations():
    locations = Location.query.all()
    return jsonify([
        {"id": loc.id, "name": loc.name, "x": loc.x, "y": loc.y}
        for loc in locations
    ])
