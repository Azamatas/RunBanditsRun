CREATE TYPE sport_type AS ENUM ('run', 'ride', 'swim', 'walk', 'hike');
CREATE TYPE visibility AS ENUM ('public', 'friends', 'private');
CREATE TYPE friendship_status AS ENUM ('pending', 'accepted');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    sport_type sport_type NOT NULL,
    distance FLOAT,
    duration INTEGER,
    elevation FLOAT,
    polyline TEXT,
    visibility visibility DEFAULT 'public',
    started_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX ix_activities_owner_id ON activities (owner_id);

CREATE TABLE friendships (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id),
    addressee_id INTEGER NOT NULL REFERENCES users(id),
    status friendship_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX ix_friendships_requester_id ON friendships (requester_id);
CREATE INDEX ix_friendships_addressee_id ON friendships (addressee_id);

CREATE TABLE kudos (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activities(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT (now() AT TIME ZONE 'utc')
);
CREATE INDEX ix_kudos_activity_id ON kudos (activity_id);
CREATE INDEX ix_kudos_user_id ON kudos (user_id);

CREATE TABLE segments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    polyline TEXT,
    distance FLOAT
);

CREATE TABLE segment_efforts (
    id SERIAL PRIMARY KEY,
    segment_id INTEGER NOT NULL REFERENCES segments(id),
    activity_id INTEGER NOT NULL REFERENCES activities(id),
    athlete_id INTEGER NOT NULL REFERENCES users(id),
    elapsed_time INTEGER NOT NULL,
    started_at TIMESTAMP
);
CREATE INDEX ix_segment_efforts_segment_id ON segment_efforts (segment_id);
CREATE INDEX ix_segment_efforts_activity_id ON segment_efforts (activity_id);
CREATE INDEX ix_segment_efforts_athlete_id ON segment_efforts (athlete_id);

CREATE TABLE activity_athletes (
    activity_id INTEGER REFERENCES activities(id),
    user_id INTEGER REFERENCES users(id),
    PRIMARY KEY (activity_id, user_id)
);