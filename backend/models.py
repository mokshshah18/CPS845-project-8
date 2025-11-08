from db import db

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
