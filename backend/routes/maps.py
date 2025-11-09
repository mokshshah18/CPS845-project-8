from flask import Blueprint, jsonify, request
from db import db

maps_bp = Blueprint("maps_bp", __name__)

class Building(db.Model):
    __tablename__ = "buildings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    map_url = db.Column(db.String(255))
    floor_plan = db.Column(db.Text)

class RecentSearch(db.Model):
    __tablename__ = "recent_searches"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    destination = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

@maps_bp.route("/buildings", methods=["GET"])
def get_buildings():
    buildings = Building.query.all()
    result = [{"id": b.id, "name": b.name, "map_url": b.map_url, "floor_plan": b.floor_plan} for b in buildings]
    return jsonify(result)

@maps_bp.route("/recent-searches/<int:user_id>", methods=["GET"])
def get_recent_searches(user_id):
    searches = RecentSearch.query.filter_by(user_id=user_id).order_by(RecentSearch.timestamp.desc()).limit(10).all()
    result = [{"destination": s.destination, "timestamp": s.timestamp} for s in searches]
    return jsonify(result)

@maps_bp.route("/recent-searches", methods=["POST"])
def add_recent_search():
    data = request.json
    new_search = RecentSearch(user_id=data["user_id"], destination=data["destination"])
    db.session.add(new_search)
    db.session.commit()
    return jsonify({"message": "Recent search added!"}), 201
