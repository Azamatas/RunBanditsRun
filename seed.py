"""Seed the database with sample segments, users, activities and leaderboard efforts."""
import sys
from datetime import datetime, timezone, timedelta
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.activity import Activity, SportType, Visibility
from backend.models.segment import Segment, SegmentEffort
from backend.services.auth_service import hash_password


# ---------------------------------------------------------------------------
# Polyline encoder (Google/Mapbox format)
# ---------------------------------------------------------------------------

def encode_polyline(points):
    result = []
    prev_lat = prev_lon = 0
    for lat, lon in points:
        for val, prev in [(round(lat * 1e5), prev_lat), (round(lon * 1e5), prev_lon)]:
            delta = (val - prev) << 1
            if delta < 0:
                delta = ~delta
            while delta >= 0x20:
                result.append(chr((0x20 | (delta & 0x1f)) + 63))
                delta >>= 5
            result.append(chr(delta + 63))
            if val == round(lat * 1e5):
                prev_lat = round(lat * 1e5)
            else:
                prev_lon = round(lon * 1e5)
    return "".join(result)


def haversine_m(p1, p2):
    import math
    R = 6_371_000
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def route_distance(pts):
    return sum(haversine_m(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ---------------------------------------------------------------------------
# Route definitions  (lat, lon)  — Amsterdam area
# ---------------------------------------------------------------------------

ROUTES = [
    {
        "name": "Vondelpark Loop",
        "points": [
            (52.3579, 4.8686), (52.3591, 4.8653), (52.3608, 4.8629),
            (52.3628, 4.8618), (52.3647, 4.8639), (52.3652, 4.8674),
            (52.3641, 4.8706), (52.3618, 4.8722), (52.3596, 4.8716),
            (52.3579, 4.8686),
        ],
    },
    {
        "name": "Amstel Riverside Sprint",
        "points": [
            (52.3488, 4.9065), (52.3512, 4.9082), (52.3541, 4.9093),
            (52.3569, 4.9101), (52.3597, 4.9108), (52.3622, 4.9115),
        ],
    },
    {
        "name": "IJ Waterfront Run",
        "points": [
            (52.3791, 4.9003), (52.3801, 4.9058), (52.3809, 4.9112),
            (52.3814, 4.9168), (52.3818, 4.9223), (52.3820, 4.9278),
        ],
    },
    {
        "name": "Oosterpark Hill Climb",
        "points": [
            (52.3598, 4.9212), (52.3610, 4.9231), (52.3625, 4.9248),
            (52.3641, 4.9261), (52.3655, 4.9270),
        ],
    },
]

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

USERS = [
    {"username": "marc_runner",  "email": "marc@example.com",  "password": "Password1", "bio": "Marathon addict",         "location": "Amsterdam"},
    {"username": "lisa_pace",    "email": "lisa@example.com",  "password": "Password1", "bio": "5K specialist",           "location": "Utrecht"},
    {"username": "tom_trails",   "email": "tom@example.com",   "password": "Password1", "bio": "Trail & road",            "location": "Haarlem"},
    {"username": "nina_fast",    "email": "nina@example.com",  "password": "Password1", "bio": "Sub-3h marathoner",       "location": "Amsterdam"},
    {"username": "alex_grind",   "email": "alex@example.com",  "password": "Password1", "bio": "Running every day",       "location": "Leiden"},
]

# Elapsed times (seconds) per segment per user — lower is better
TIMES = {
    "Vondelpark Loop":        [612, 638, 655, 671, 698],
    "Amstel Riverside Sprint":[284, 301, 315, 328, 342],
    "IJ Waterfront Run":      [498, 521, 539, 557, 578],
    "Oosterpark Hill Climb":  [193, 208, 217, 229, 241],
}


def run():
    db = SessionLocal()
    try:
        # -- Users -----------------------------------------------------------
        users = []
        for u in USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                users.append(existing)
                print(f"  user exists: {u['username']}")
            else:
                user = User(
                    username=u["username"],
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    bio=u["bio"],
                    location=u["location"],
                )
                db.add(user)
                db.flush()
                users.append(user)
                print(f"  created user: {u['username']}")

        # -- Activities (one per user, generic) ------------------------------
        activities = []
        for i, user in enumerate(users):
            existing = db.query(Activity).filter(
                Activity.owner_id == user.id,
                Activity.title == "Seed Run"
            ).first()
            if existing:
                activities.append(existing)
            else:
                act = Activity(
                    owner_id=user.id,
                    title="Seed Run",
                    sport_type=SportType.RUN,
                    distance=8000,
                    duration=2400,
                    visibility=Visibility.PUBLIC,
                    started_at=datetime.now(timezone.utc) - timedelta(days=i + 1),
                )
                db.add(act)
                db.flush()
                activities.append(act)

        # -- Segments + efforts ----------------------------------------------
        for route in ROUTES:
            pts = route["points"]
            poly = encode_polyline(pts)
            dist = route_distance(pts)
            name = route["name"]

            seg = db.query(Segment).filter(Segment.name == name).first()
            if not seg:
                seg = Segment(name=name, polyline=poly, distance=dist)
                db.add(seg)
                db.flush()
                print(f"  created segment: {name}  ({dist/1000:.2f} km)")
            else:
                print(f"  segment exists: {name}")

            times = TIMES[name]
            for user, act, elapsed in zip(users, activities, times):
                exists = db.query(SegmentEffort).filter(
                    SegmentEffort.segment_id == seg.id,
                    SegmentEffort.athlete_id == user.id,
                ).first()
                if not exists:
                    effort = SegmentEffort(
                        segment_id=seg.id,
                        activity_id=act.id,
                        athlete_id=user.id,
                        elapsed_time=elapsed,
                        started_at=datetime.now(timezone.utc) - timedelta(days=1),
                    )
                    db.add(effort)

        db.commit()
        print("\nDone — database seeded.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
