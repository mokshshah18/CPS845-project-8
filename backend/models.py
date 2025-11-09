from db import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Float)
    y = db.Column(db.Float)

class Path(db.Model):
    __tablename__ = "paths"
    id = db.Column(db.Integer, primary_key=True)
    start_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    end_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    distance = db.Column(db.Float)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_items = db.relationship("SavedItem", backref="user", lazy=True, cascade="all, delete-orphan")
    saved_routes = db.relationship("SavedRoute", backref="user", lazy=True, cascade="all, delete-orphan")

class SavedItem(db.Model):
    __tablename__ = "saved_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Item type: 'location', 'course', 'route', 'professor', 'event', etc.
    item_type = db.Column(db.String(50), nullable=False)
    
    # Flexible storage - can store different types of information
    name = db.Column(db.String(200), nullable=False)  # Course name, location name, etc.
    professor_name = db.Column(db.String(100))  # For courses
    course_code = db.Column(db.String(20))  # e.g., "CPS845"
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    room_number = db.Column(db.String(50))
    
    # Additional metadata stored as JSON
    item_metadata = db.Column(db.Text)  # JSON string for flexible data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For sorting preferences
    custom_order = db.Column(db.Integer, default=0)  # User-defined order
    tags = db.Column(db.String(255))  # Comma-separated tags for filtering
    
    # Relationship
    location = db.relationship("Location", backref="saved_items")
    
    # Indexes for fast sorting
    __table_args__ = (
        db.Index('idx_user_name', 'user_id', 'name'),
        db.Index('idx_user_professor', 'user_id', 'professor_name'),
        db.Index('idx_user_course', 'user_id', 'course_code'),
        db.Index('idx_user_custom', 'user_id', 'custom_order'),
    )

class SavedRoute(db.Model):
    __tablename__ = "saved_routes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200))  # User-given name for the route
    start_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    end_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    route_data = db.Column(db.Text)  # JSON string storing route steps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    use_count = db.Column(db.Integer, default=0)
    
    # Relationships
    start_location = db.relationship("Location", foreign_keys=[start_location_id])
    end_location = db.relationship("Location", foreign_keys=[end_location_id])
