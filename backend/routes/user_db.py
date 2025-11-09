from flask import Blueprint, request, jsonify
from models import (
    User, UserSavedLocations, UserRecentSearches,
    UserScheduleEntries, UserPreferences, Location
)
from db import db
from datetime import datetime
import json

user_db_bp = Blueprint("user_db", __name__)

# ============ User Saved Locations ============

@user_db_bp.route("/saved-locations", methods=["GET"])
def get_saved_locations():
    """Get all saved locations for a user"""
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    locations = UserSavedLocations.query.filter_by(user_id=user_id).order_by(UserSavedLocations.created_at.desc()).all()
    
    result = []
    for loc in locations:
        result.append({
            "id": loc.id,
            "location_name": loc.location_name,
            "building_name": loc.building_name,
            "room_number": loc.room_number,
            "floor_number": loc.floor_number,
            "qr_code_id": loc.qr_code_id,
            "created_at": loc.created_at.isoformat() if loc.created_at else None
        })
    
    return jsonify(result)

@user_db_bp.route("/saved-locations", methods=["POST"])
def save_location():
    """Save a new location for a user"""
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    new_location = UserSavedLocations(
        user_id=user_id,
        location_name=data.get("location_name"),
        building_name=data.get("building_name"),
        room_number=data.get("room_number"),
        floor_number=data.get("floor_number"),
        qr_code_id=data.get("qr_code_id")
    )
    
    db.session.add(new_location)
    db.session.commit()
    
    return jsonify({
        "message": "Location saved",
        "id": new_location.id
    }), 201

@user_db_bp.route("/saved-locations/<int:location_id>", methods=["PUT"])
def update_saved_location(location_id):
    """Update a saved location"""
    location = UserSavedLocations.query.get_or_404(location_id)
    data = request.json
    
    if "location_name" in data:
        location.location_name = data["location_name"]
    if "building_name" in data:
        location.building_name = data["building_name"]
    if "room_number" in data:
        location.room_number = data["room_number"]
    if "floor_number" in data:
        location.floor_number = data["floor_number"]
    if "qr_code_id" in data:
        location.qr_code_id = data["qr_code_id"]
    
    db.session.commit()
    return jsonify({"message": "Location updated"})

@user_db_bp.route("/saved-locations/<int:location_id>", methods=["DELETE"])
def delete_saved_location(location_id):
    """Delete a saved location"""
    location = UserSavedLocations.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": "Location deleted"})

# ============ User Recent Searches ============

@user_db_bp.route("/recent-searches", methods=["GET"])
def get_recent_searches():
    """Get recent searches for a user (limited to last 10)"""
    user_id = request.args.get("user_id", type=int)
    limit = request.args.get("limit", 10, type=int)
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    searches = UserRecentSearches.query.filter_by(user_id=user_id)\
        .order_by(UserRecentSearches.timestamp.desc())\
        .limit(limit).all()
    
    result = []
    for search in searches:
        search_data = {
            "id": search.id,
            "search_term": search.search_term,
            "timestamp": search.timestamp.isoformat() if search.timestamp else None
        }
        if search.location:
            search_data["location"] = {
                "id": search.location.id,
                "name": search.location.name,
                "x": search.location.x,
                "y": search.location.y
            }
        result.append(search_data)
    
    return jsonify(result)

@user_db_bp.route("/recent-searches", methods=["POST"])
def add_recent_search():
    """Add a new recent search"""
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    # Check if search already exists for this user
    existing = UserRecentSearches.query.filter_by(
        user_id=user_id,
        search_term=data.get("search_term")
    ).first()
    
    if existing:
        # Update timestamp
        existing.timestamp = datetime.utcnow()
        if "resolved_location_id" in data:
            existing.resolved_location_id = data["resolved_location_id"]
        db.session.commit()
        return jsonify({"message": "Recent search updated", "id": existing.id})
    
    new_search = UserRecentSearches(
        user_id=user_id,
        search_term=data.get("search_term"),
        resolved_location_id=data.get("resolved_location_id")
    )
    
    db.session.add(new_search)
    db.session.commit()
    
    return jsonify({
        "message": "Recent search added",
        "id": new_search.id
    }), 201

@user_db_bp.route("/recent-searches/<int:search_id>", methods=["DELETE"])
def delete_recent_search(search_id):
    """Delete a recent search"""
    search = UserRecentSearches.query.get_or_404(search_id)
    db.session.delete(search)
    db.session.commit()
    return jsonify({"message": "Recent search deleted"})

# ============ User Schedule Entries ============

@user_db_bp.route("/schedule", methods=["GET"])
def get_schedule():
    """Get schedule entries for a user"""
    user_id = request.args.get("user_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    query = UserScheduleEntries.query.filter_by(user_id=user_id)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(UserScheduleEntries.event_start_time >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(UserScheduleEntries.event_end_time <= end_dt)
        except:
            pass
    
    entries = query.order_by(UserScheduleEntries.event_start_time.asc()).all()
    
    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "course_name": entry.course_name,
            "professor_name": entry.professor_name,
            "building_name": entry.building_name,
            "room_number": entry.room_number,
            "event_start_time": entry.event_start_time.isoformat() if entry.event_start_time else None,
            "event_end_time": entry.event_end_time.isoformat() if entry.event_end_time else None,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        })
    
    return jsonify(result)

@user_db_bp.route("/schedule", methods=["POST"])
def add_schedule_entry():
    """Add a new schedule entry"""
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    try:
        start_time = datetime.fromisoformat(data["event_start_time"].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data["event_end_time"].replace('Z', '+00:00'))
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid event_start_time or event_end_time"}), 400
    
    new_entry = UserScheduleEntries(
        user_id=user_id,
        course_name=data.get("course_name"),
        professor_name=data.get("professor_name"),
        building_name=data.get("building_name"),
        room_number=data.get("room_number"),
        event_start_time=start_time,
        event_end_time=end_time
    )
    
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({
        "message": "Schedule entry added",
        "id": new_entry.id
    }), 201

@user_db_bp.route("/schedule/<int:entry_id>", methods=["PUT"])
def update_schedule_entry(entry_id):
    """Update a schedule entry"""
    entry = UserScheduleEntries.query.get_or_404(entry_id)
    data = request.json
    
    if "course_name" in data:
        entry.course_name = data["course_name"]
    if "professor_name" in data:
        entry.professor_name = data["professor_name"]
    if "building_name" in data:
        entry.building_name = data["building_name"]
    if "room_number" in data:
        entry.room_number = data["room_number"]
    if "event_start_time" in data:
        try:
            entry.event_start_time = datetime.fromisoformat(data["event_start_time"].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid event_start_time format"}), 400
    if "event_end_time" in data:
        try:
            entry.event_end_time = datetime.fromisoformat(data["event_end_time"].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid event_end_time format"}), 400
    
    db.session.commit()
    return jsonify({"message": "Schedule entry updated"})

@user_db_bp.route("/schedule/<int:entry_id>", methods=["DELETE"])
def delete_schedule_entry(entry_id):
    """Delete a schedule entry"""
    entry = UserScheduleEntries.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Schedule entry deleted"})

# ============ User Preferences ============

@user_db_bp.route("/preferences", methods=["GET"])
def get_preferences():
    """Get user preferences"""
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserPreferences(
            user_id=user_id,
            sorting_preference="name",
            route_preference="shortest",
            calendar_sync_enabled=False,
            offline_mode_enabled=False
        )
        db.session.add(preferences)
        db.session.commit()
    
    return jsonify({
        "id": preferences.id,
        "user_id": preferences.user_id,
        "sorting_preference": preferences.sorting_preference,
        "route_preference": preferences.route_preference,
        "calendar_sync_enabled": preferences.calendar_sync_enabled,
        "offline_mode_enabled": preferences.offline_mode_enabled,
        "created_at": preferences.created_at.isoformat() if preferences.created_at else None,
        "updated_at": preferences.updated_at.isoformat() if preferences.updated_at else None
    })

@user_db_bp.route("/preferences", methods=["PUT"])
def update_preferences():
    """Update user preferences"""
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreferences(user_id=user_id)
        db.session.add(preferences)
    
    if "sorting_preference" in data:
        preferences.sorting_preference = data["sorting_preference"]
    if "route_preference" in data:
        preferences.route_preference = data["route_preference"]
    if "calendar_sync_enabled" in data:
        preferences.calendar_sync_enabled = data["calendar_sync_enabled"]
    if "offline_mode_enabled" in data:
        preferences.offline_mode_enabled = data["offline_mode_enabled"]
    
    preferences.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"message": "Preferences updated"})

