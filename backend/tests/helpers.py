from backend.models.activity import Activity, SportType, Visibility


def create_activity(db, owner_id, **kwargs):
    defaults = {
        "owner_id": owner_id,
        "title": "Test Run",
        "sport_type": SportType.RUN,
        "distance": 5000.0,
        "duration": 1800,
        "visibility": Visibility.PUBLIC,
    }
    defaults.update(kwargs)
    activity = Activity(**defaults)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity