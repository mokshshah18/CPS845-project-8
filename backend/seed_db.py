from app import app, db
from models import Location, Path

with app.app_context():
    db.drop_all()
    db.create_all()

    locs = [
        Location(name="Library", x=100, y=200),
        Location(name="Science Hall", x=300, y=200),
        Location(name="Gym", x=500, y=400),
    ]
    db.session.add_all(locs)
    db.session.commit()

    paths = [
        Path(start_id=locs[0].id, end_id=locs[1].id, distance=150),
        Path(start_id=locs[1].id, end_id=locs[2].id, distance=250),
    ]
    db.session.add_all(paths)
    db.session.commit()

    print("Database seeded!")
