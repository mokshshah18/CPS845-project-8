from flask import Blueprint, request, jsonify
from models import SavedItem, User, Location
from db import db
from sqlalchemy import or_, and_, func
import json

saved_items_bp = Blueprint("saved_items", __name__)

# Get all saved items with sorting options
@saved_items_bp.route("/", methods=["GET"])
def get_saved_items():
    user_id = request.args.get("user_id", type=int)
    sort_by = request.args.get("sort_by", "name")  # name, professor, course_code, created_at, custom
    order = request.args.get("order", "asc")  # asc or desc
    item_type = request.args.get("type")  # Optional filter by type
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    query = SavedItem.query.filter_by(user_id=user_id)
    
    # Filter by type if provided
    if item_type:
        query = query.filter_by(item_type=item_type)
    
    # Sorting logic
    if sort_by == "name":
        query = query.order_by(SavedItem.name.asc() if order == "asc" else SavedItem.name.desc())
    elif sort_by == "professor":
        query = query.order_by(SavedItem.professor_name.asc() if order == "asc" else SavedItem.professor_name.desc())
    elif sort_by == "course_code":
        query = query.order_by(SavedItem.course_code.asc() if order == "asc" else SavedItem.course_code.desc())
    elif sort_by == "created_at":
        query = query.order_by(SavedItem.created_at.desc() if order == "desc" else SavedItem.created_at.asc())
    elif sort_by == "custom":
        query = query.order_by(SavedItem.custom_order.asc() if order == "asc" else SavedItem.custom_order.desc())
    else:
        query = query.order_by(SavedItem.name.asc())
    
    items = query.all()
    
    result = []
    for item in items:
        item_data = {
            "id": item.id,
            "item_type": item.item_type,
            "name": item.name,
            "professor_name": item.professor_name,
            "course_code": item.course_code,
            "room_number": item.room_number,
            "location_id": item.location_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "tags": item.tags.split(",") if item.tags else []
        }
        if item.location:
            item_data["location"] = {
                "id": item.location.id,
                "name": item.location.name,
                "x": item.location.x,
                "y": item.location.y
            }
        if item.item_metadata:
            try:
                item_data["metadata"] = json.loads(item.item_metadata)
            except:
                item_data["metadata"] = {}
        result.append(item_data)
    
    return jsonify(result)

# Save a new item
@saved_items_bp.route("/", methods=["POST"])
def save_item():
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    new_item = SavedItem(
        user_id=user_id,
        item_type=data.get("item_type", "location"),
        name=data.get("name"),
        professor_name=data.get("professor_name"),
        course_code=data.get("course_code"),
        location_id=data.get("location_id"),
        room_number=data.get("room_number"),
        tags=",".join(data.get("tags", [])) if isinstance(data.get("tags"), list) else data.get("tags", ""),
        item_metadata=json.dumps(data.get("metadata", {}))
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({"message": "Item saved", "id": new_item.id}), 201

# Update an item (including custom order for sorting)
@saved_items_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = SavedItem.query.get_or_404(item_id)
    data = request.json
    
    if "name" in data:
        item.name = data["name"]
    if "professor_name" in data:
        item.professor_name = data["professor_name"]
    if "course_code" in data:
        item.course_code = data["course_code"]
    if "custom_order" in data:
        item.custom_order = data["custom_order"]
    if "tags" in data:
        item.tags = ",".join(data["tags"]) if isinstance(data["tags"], list) else data["tags"]
    if "location_id" in data:
        item.location_id = data["location_id"]
    if "room_number" in data:
        item.room_number = data["room_number"]
    if "metadata" in data:
        item.item_metadata = json.dumps(data["metadata"])
    
    db.session.commit()
    return jsonify({"message": "Item updated"})

# Delete an item
@saved_items_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = SavedItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"})

# Bulk update custom order (for drag-and-drop sorting)
@saved_items_bp.route("/reorder", methods=["PUT"])
def reorder_items():
    data = request.json
    user_id = data.get("user_id")
    item_orders = data.get("orders")  # List of {id: item_id, order: new_order}
    
    if not user_id or not item_orders:
        return jsonify({"error": "user_id and orders required"}), 400
    
    for item_order in item_orders:
        item = SavedItem.query.filter_by(id=item_order["id"], user_id=user_id).first()
        if item:
            item.custom_order = item_order["order"]
    
    db.session.commit()
    return jsonify({"message": "Items reordered"})

# Get sorting options available
@saved_items_bp.route("/sort-options", methods=["GET"])
def get_sort_options():
    return jsonify({
        "sort_options": [
            {"value": "name", "label": "Name (Alphabetical)"},
            {"value": "professor", "label": "Professor Name"},
            {"value": "course_code", "label": "Course Code"},
            {"value": "created_at", "label": "Date Created"},
            {"value": "custom", "label": "Custom Order"}
        ]
    })
