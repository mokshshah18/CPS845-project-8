from db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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

class UserSavedLocations(db.Model):
    __tablename__ = "user_saved_locations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    building_name = db.Column(db.String(100))
    room_number = db.Column(db.String(50))
    floor_number = db.Column(db.Integer)
    qr_code_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", backref="saved_locations")

class UserRecentSearches(db.Model):
    __tablename__ = "user_recent_searches"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    search_term = db.Column(db.String(255), nullable=False)
    resolved_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref="recent_searches")
    location = db.relationship("Location", backref="recent_searches")

class UserScheduleEntries(db.Model):
    __tablename__ = "user_schedule_entries"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_name = db.Column(db.String(200))
    professor_name = db.Column(db.String(100))
    building_name = db.Column(db.String(100))
    room_number = db.Column(db.String(50))
    event_start_time = db.Column(db.DateTime, nullable=False)
    event_end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", backref="schedule_entries")

class UserPreferences(db.Model):
    __tablename__ = "user_preferences"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    sorting_preference = db.Column(db.String(50), default="name")
    route_preference = db.Column(db.String(50), default="shortest")  # shortest, fastest, accessible
    calendar_sync_enabled = db.Column(db.Boolean, default=False)
    offline_mode_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", backref="preferences", uselist=False)

class StudentIncidentReport(db.Model):
    __tablename__ = "student_incident_reports"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reporter_name = db.Column(db.String(120), nullable=False)
    reporter_email = db.Column(db.String(200), nullable=False)
    reporter_phone = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False) 
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    building_name = db.Column(db.String(120))
    room_number = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    photo_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default="new")   

class FacultyUser(db.Model):
    __tablename__ = "faculty_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)   

class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(200))
    severity = db.Column(db.String(20))          
    audience_type = db.Column(db.String(20))     
    course_code = db.Column(db.String(20))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    source_report_id = db.Column(db.Integer, db.ForeignKey("student_incident_reports.id"))

    recipients = db.relationship("AlertRecipient", backref="alert", cascade="all, delete-orphan")

class AlertRecipient(db.Model):
    __tablename__ = "alert_recipients"
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_email = db.Column(db.String(255))
    delivered = db.Column(db.Boolean, default=True)  
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")

