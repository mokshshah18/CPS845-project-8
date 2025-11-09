from app import app
from db import db
from routes.maps import Building, RecentSearch

with app.app_context():
    # Ensure tables exist
    db.create_all()
    print("Tables created or already exist.")

    # Add buildings
    if not Building.query.first():
        buildings = [
            Building(name="Engineering Building", map_url="/maps/engineering.png", floor_plan='{"floors":["1F","2F"]}'),
            Building(name="Library", map_url="/maps/library.png", floor_plan='{"floors":["1F","2F","3F"]}'),
            Building(name="Student Centre", map_url="/maps/student_centre.png", floor_plan='{"floors":["1F","2F","3F"]}')
        ]
        db.session.add_all(buildings)
        db.session.commit()
        print("Buildings added:")
        for b in Building.query.all():
            print(f"  {b.id}: {b.name}")
    else:
        print("Buildings already exist.")

    # Add recent searches
    if not RecentSearch.query.first():
        searches = [
            RecentSearch(user_id=1, destination="Engineering Building"),
            RecentSearch(user_id=1, destination="Library")
        ]
        db.session.add_all(searches)
        db.session.commit()
        print("Recent searches added:")
        for s in RecentSearch.query.all():
            print(f"  {s.id}: User {s.user_id} -> {s.destination}")
    else:
        print("Recent searches already exist.")
