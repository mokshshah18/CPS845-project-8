from app import app, db
from models import Location, Path, User, SavedItem
import json

with app.app_context():
    db.drop_all()
    db.create_all()

    locs = [
        Location(name="Library", x=100, y=200),
        Location(name="Science Hall", x=300, y=200),
        Location(name="Gym", x=500, y=400),
        Location(name="Engineering Building", x=200, y=300),
        Location(name="Student Centre", x=400, y=100),
    ]
    db.session.add_all(locs)
    db.session.commit()

    paths = [
        Path(start_id=locs[0].id, end_id=locs[1].id, distance=150),
        Path(start_id=locs[1].id, end_id=locs[2].id, distance=250),
    ]
    db.session.add_all(paths)
    db.session.commit()

    # Create a test user
    test_user = User(email="test@ryerson.ca", name="Test User")
    db.session.add(test_user)
    db.session.commit()

    # Create sample saved items for testing sorting
    saved_items = [
        SavedItem(
            user_id=test_user.id,
            item_type="course",
            name="Advanced Database Systems",
            professor_name="Dr. Smith",
            course_code="CPS845",
            location_id=locs[0].id,
            room_number="LIB-301",
            tags="database,graduate",
            item_metadata=json.dumps({"semester": "Fall 2024", "credits": 3})
        ),
        SavedItem(
            user_id=test_user.id,
            item_type="course",
            name="Machine Learning",
            professor_name="Dr. Johnson",
            course_code="CPS803",
            location_id=locs[1].id,
            room_number="SCI-205",
            tags="ai,graduate",
            item_metadata=json.dumps({"semester": "Fall 2024", "credits": 3})
        ),
        SavedItem(
            user_id=test_user.id,
            item_type="course",
            name="Software Engineering",
            professor_name="Dr. Williams",
            course_code="CPS847",
            location_id=locs[2].id,
            room_number="GYM-101",
            tags="software,graduate",
            item_metadata=json.dumps({"semester": "Winter 2025", "credits": 3})
        ),
        SavedItem(
            user_id=test_user.id,
            item_type="location",
            name="Library Study Room",
            location_id=locs[0].id,
            room_number="LIB-201",
            tags="study,quiet",
        ),
        SavedItem(
            user_id=test_user.id,
            item_type="location",
            name="Engineering Lab",
            location_id=locs[3].id,
            room_number="ENG-405",
            tags="lab,equipment",
        ),
    ]
    db.session.add_all(saved_items)
    db.session.commit()

    print("Database seeded!")
    print(f"Created {len(locs)} locations, {len(paths)} paths, 1 user, and {len(saved_items)} saved items")
    print(f"Test user ID: {test_user.id} (use this for testing saved items API)")
