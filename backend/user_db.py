from app import app, db
from models import (
    Location, Path, User, SavedItem,
    UserSavedLocations, UserRecentSearches, 
    UserScheduleEntries, UserPreferences
)
import json
from datetime import datetime, timedelta

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
    
    # Seed user-specific data
    user_saved_locations = [
        UserSavedLocations(
            user_id=test_user.id,
            location_name="Favorite Study Spot",
            building_name="Library",
            room_number="LIB-301",
            floor_number=3,
            qr_code_id="LIB301_QR001"
        ),
        UserSavedLocations(
            user_id=test_user.id,
            location_name="Project Lab",
            building_name="Engineering Building",
            room_number="ENG-405",
            floor_number=4,
            qr_code_id="ENG405_QR002"
        )
    ]
    db.session.add_all(user_saved_locations)
    
    user_recent_searches = [
        UserRecentSearches(
            user_id=test_user.id,
            search_term="library study rooms",
            resolved_location_id=locs[0].id
        ),
        UserRecentSearches(
            user_id=test_user.id,
            search_term="engineering lab",
            resolved_location_id=locs[3].id
        )
    ]
    db.session.add_all(user_recent_searches)
    
    # Schedule entries for next week
    next_week = datetime.utcnow() + timedelta(days=7)
    user_schedule_entries = [
        UserScheduleEntries(
            user_id=test_user.id,
            course_name="Advanced Database Systems",
            professor_name="Dr. Smith",
            building_name="Library",
            room_number="LIB-301",
            event_start_time=next_week.replace(hour=10, minute=0),
            event_end_time=next_week.replace(hour=11, minute=30)
        ),
        UserScheduleEntries(
            user_id=test_user.id,
            course_name="Machine Learning",
            professor_name="Dr. Johnson",
            building_name="Science Hall",
            room_number="SCI-205",
            event_start_time=next_week.replace(hour=13, minute=0),
            event_end_time=next_week.replace(hour=14, minute=30)
        )
    ]
    db.session.add_all(user_schedule_entries)
    
    # User preferences
    user_preferences = UserPreferences(
        user_id=test_user.id,
        sorting_preference="name",
        route_preference="shortest",
        calendar_sync_enabled=True,
        offline_mode_enabled=False
    )
    db.session.add(user_preferences)
    
    db.session.commit()
    
    print("Database seeded!")
    print(f"Created {len(locs)} locations, {len(paths)} paths, 1 user, {len(saved_items)} saved items")
    print(f"Plus {len(user_saved_locations)} user saved locations, {len(user_recent_searches)} recent searches")
    print(f"{len(user_schedule_entries)} schedule entries, and 1 user preference")
    print(f"Test user ID: {test_user.id} (use this for testing saved items API)")