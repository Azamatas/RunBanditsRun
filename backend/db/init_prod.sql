-- PostgreSQL initialization script for RunBanditsRun production database
-- This script creates tables (if not exist) and populates with sensible seed data

-- ============================================
-- ENUMS (must be created before tables)
-- ============================================

CREATE TYPE sport_type AS ENUM ('run', 'ride', 'swim', 'walk', 'hike');
CREATE TYPE visibility AS ENUM ('public', 'friends', 'private');
CREATE TYPE friendship_status AS ENUM ('pending', 'accepted');

-- ============================================
-- TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    location VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    sport_type sport_type NOT NULL,
    distance FLOAT,
    duration INTEGER,
    elevation FLOAT,
    polyline TEXT,
    visibility visibility DEFAULT 'public',
    started_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    addressee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status friendship_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (requester_id, addressee_id)
);

CREATE TABLE IF NOT EXISTS segments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    polyline TEXT,
    distance FLOAT
);

CREATE TABLE IF NOT EXISTS segment_efforts (
    id SERIAL PRIMARY KEY,
    segment_id INTEGER NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    athlete_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    elapsed_time INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS kudos (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (activity_id, user_id)
);

CREATE TABLE IF NOT EXISTS activity_athletes (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, user_id)
);

-- ============================================
-- INDEXES (for performance)
-- ============================================

CREATE INDEX IF NOT EXISTS idx_activities_owner_id ON activities(owner_id);
CREATE INDEX IF NOT EXISTS idx_activities_started_at ON activities(started_at);
CREATE INDEX IF NOT EXISTS idx_activities_visibility ON activities(visibility);
CREATE INDEX IF NOT EXISTS idx_friendships_requester_id ON friendships(requester_id);
CREATE INDEX IF NOT EXISTS idx_friendships_addressee_id ON friendships(addressee_id);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status);
CREATE INDEX IF NOT EXISTS idx_kudos_activity_id ON kudos(activity_id);
CREATE INDEX IF NOT EXISTS idx_kudos_user_id ON kudos(user_id);
CREATE INDEX IF NOT EXISTS idx_segment_efforts_segment_id ON segment_efforts(segment_id);
CREATE INDEX IF NOT EXISTS idx_segment_efforts_activity_id ON segment_efforts(activity_id);

-- ============================================
-- DATA INSERTION
-- ============================================

-- Helper function to generate a password hash (placeholder - use bcrypt in app)
-- In production, use: python -c "from backend.services.auth_service import get_password_hash; print(get_password_hash('password'))"
-- For this script, we use a dummy hash that the app should replace

-- Users
-- Note: password_hash should be bcrypt hashed. Use backend auth to generate real ones.
INSERT INTO users (id, username, email, password_hash, bio, location, created_at) VALUES
    (1, 'alice_runner', 'alice@example.com', '$2b$12$dummyhashalice', 'Marathon enthusiast and coffee addict. Training for Boston 2026!', 'Boston, MA', CURRENT_TIMESTAMP - INTERVAL '30 days'),
    (2, 'bob_cyclist', 'bob@example.com', '$2b$12$dummyhashbob', 'Road cyclist. Love climbing hills and long century rides.', 'San Francisco, CA', CURRENT_TIMESTAMP - INTERVAL '25 days'),
    (3, 'charlie_swimmer', 'charlie@example.com', '$2b$12$dummyhashcharlie', 'Open water swimmer and triathlete.', 'Miami, FL', CURRENT_TIMESTAMP - INTERVAL '20 days'),
    (4, 'diana_hiker', 'diana@example.com', '$2b$12$dummyhashdiana', 'Trail runner and mountain hiker. Love the great outdoors!', 'Denver, CO', CURRENT_TIMESTAMP - INTERVAL '15 days'),
    (5, 'eve_walker', 'eve@example.com', '$2b$12$dummyhasheve', 'Casual walker, love city walks and nature trails.', 'New York, NY', CURRENT_TIMESTAMP - INTERVAL '10 days'),
    (6, 'frank_runner', 'frank@example.com', '$2b$12$dummyhashfrank', '5K and 10K specialist. Always chasing a new PR!', 'Chicago, IL', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (7, 'grace_triathlete', 'grace@example.com', '$2b$12$dummyhashgrace', 'Ironman finisher. Swim, bike, run, repeat.', 'Austin, TX', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (8, 'henry_cyclist', 'henry@example.com', '$2b$12$dummyhashhenry', 'Gravel rider and bike packer.', 'Portland, OR', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- Segments (popular running/cycling routes)
INSERT INTO segments (id, name, polyline, distance) VALUES
    (1, 'Boston Esplanade Loop', 'Encoded polyline for Boston Esplanade', 5.2),
    (2, 'Golden Gate Bridge Climb', 'Encoded polyline for GG Bridge', 2.8),
    (3, 'Central Park Loop', 'Encoded polyline for Central Park', 6.1),
    (4, 'Lakefront Trail - Chicago', 'Encoded polyline for Chicago lakefront', 18.5),
    (5, 'Pacific Coast Highway', 'Encoded polyline for PCH segment', 45.0),
    (6, 'Boulder Creek Path', 'Encoded polyline for Boulder Creek', 13.2),
    (7, 'Hawthorn Hill Climb', 'Encoded polyline for Hawthorn Hill', 3.1);

-- Activities with realistic data
INSERT INTO activities (id, owner_id, title, sport_type, distance, duration, elevation, polyline, visibility, started_at, created_at) VALUES
    -- Alice's activities (runner)
    (1, 1, 'Morning Long Run', 'run', 16.5, 6240, 85.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '2 days 2 hours', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (2, 1, 'Tempo Run on Esplanade', 'run', 8.2, 2400, 15.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '5 days 6 hours', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (3, 1, 'Recovery Run', 'run', 5.0, 2520, 5.0, 'Encoded polyline', 'friends', CURRENT_TIMESTAMP - INTERVAL '8 days 7 hours', CURRENT_TIMESTAMP - INTERVAL '8 days'),
    -- Bob's activities (cyclist)
    (4, 2, 'Mount Tam ride', 'ride', 56.0, 15600, 1450.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '1 day 3 hours', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (5, 2, 'Golden Gate Bridge loops', 'ride', 42.3, 9800, 620.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '4 days 4 hours', CURRENT_TIMESTAMP - INTERVAL '4 days'),
    (6, 2, 'Commute to work', 'ride', 12.5, 2400, 55.0, 'Encoded polyline', 'private', CURRENT_TIMESTAMP - INTERVAL '7 days 8 hours', CURRENT_TIMESTAMP - INTERVAL '7 days'),
    -- Charlie's activities (swimmer)
    (7, 3, 'Open Water Swim - Key Biscayne', 'swim', 3.2, 5400, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '3 days 9 hours', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (8, 3, 'Pool Session - Intervals', 'swim', 2.5, 4800, 0.0, NULL, 'friends', CURRENT_TIMESTAMP - INTERVAL '6 days 10 hours', CURRENT_TIMESTAMP - INTERVAL '6 days'),
    -- Diana's activities (hiker)
    (9, 4, 'Longs Peak Ascent', 'hike', 14.5, 28800, 1450.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '10 days 5 hours', CURRENT_TIMESTAMP - INTERVAL '10 days'),
    (10, 4, 'Rocky Mountain National Park Trail', 'hike', 8.7, 14400, 620.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '12 days 7 hours', CURRENT_TIMESTAMP - INTERVAL '12 days'),
    -- Eve's activities (walker)
    (11, 5, 'Central Park Walk', 'walk', 5.0, 6000, 10.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '1 day 10 hours', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (12, 5, 'Hudson River Greenway', 'walk', 3.8, 4200, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '3 days 14 hours', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    -- Frank's activities (runner)
    (13, 6, '5K Race', 'run', 5.0, 1260, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '2 days 18 hours', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (14, 6, 'Lakefront 10K', 'run', 10.0, 2700, 5.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '5 days 9 hours', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    -- Grace's activities (triathlete)
    (15, 7, 'Ironman Training - Long Bike', 'ride', 112.0, 288000, 2000.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '15 days 6 hours', CURRENT_TIMESTAMP - INTERVAL '15 days'),
    (16, 7, 'Open Water Swim Training', 'swim', 3.8, 7800, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '16 days 7 hours', CURRENT_TIMESTAMP - INTERVAL '16 days'),
    (17, 7, 'Brick Workout - Bike to Run', 'run', 10.0, 3000, 25.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '17 days 8 hours', CURRENT_TIMESTAMP - INTERVAL '17 days'),
    -- Henry's activities (cyclist)
    (18, 8, 'Gravel Century', 'ride', 100.0, 36000, 3200.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '20 days 4 hours', CURRENT_TIMESTAMP - INTERVAL '20 days'),
    (19, 8, 'Forest Park Loops', 'ride', 25.5, 6600, 240.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '22 days 5 hours', CURRENT_TIMESTAMP - INTERVAL '22 days');

-- Activity-Athlete many-to-many (tagged users in activities)
INSERT INTO activity_athletes (activity_id, user_id) VALUES
    (1, 6),   -- Frank tagged in Alice's long run
    (4, 2),   -- Bob tagged in his own ride (self)
    (4, 1),   -- Alice tagged in Bob's ride
    (9, 4),   -- Diana tagged in her own hike
    (9, 1),   -- Alice tagged in Diana's hike
    (15, 7),  -- Grace tagged in her own bike
    (15, 2);  -- Bob tagged in Grace's bike

-- Friendships (accepted relationships)
INSERT INTO friendships (id, requester_id, addressee_id, status, created_at) VALUES
    (1, 1, 2, 'accepted', CURRENT_TIMESTAMP - INTERVAL '25 days'),
    (2, 1, 3, 'accepted', CURRENT_TIMESTAMP - INTERVAL '20 days'),
    (3, 1, 4, 'accepted', CURRENT_TIMESTAMP - INTERVAL '18 days'),
    (4, 2, 1, 'accepted', CURRENT_TIMESTAMP - INTERVAL '24 days'),
    (5, 2, 3, 'accepted', CURRENT_TIMESTAMP - INTERVAL '15 days'),
    (6, 3, 1, 'accepted', CURRENT_TIMESTAMP - INTERVAL '19 days'),
    (7, 3, 2, 'accepted', CURRENT_TIMESTAMP - INTERVAL '16 days'),
    (8, 4, 1, 'accepted', CURRENT_TIMESTAMP - INTERVAL '17 days'),
    (9, 4, 5, 'accepted', CURRENT_TIMESTAMP - INTERVAL '10 days'),
    (10, 5, 4, 'accepted', CURRENT_TIMESTAMP - INTERVAL '9 days'),
    (11, 6, 1, 'accepted', CURRENT_TIMESTAMP - INTERVAL '8 days'),
    (12, 1, 6, 'accepted', CURRENT_TIMESTAMP - INTERVAL '7 days'),
    (13, 7, 2, 'accepted', CURRENT_TIMESTAMP - INTERVAL '6 days'),
    (14, 2, 7, 'accepted', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (15, 8, 2, 'accepted', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (16, 2, 8, 'accepted', CURRENT_TIMESTAMP - INTERVAL '2 days');

-- Pending friendship requests
INSERT INTO friendships (id, requester_id, addressee_id, status, created_at) VALUES
    (17, 5, 1, 'pending', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    (18, 6, 2, 'pending', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    (19, 7, 1, 'pending', CURRENT_TIMESTAMP - INTERVAL '12 hours');

-- Kudos (likes on activities)
INSERT INTO kudos (id, activity_id, user_id, created_at) VALUES
    -- Alice's long run gets kudos
    (1, 1, 2, CURRENT_TIMESTAMP - INTERVAL '2 days 1 hour'),
    (2, 1, 3, CURRENT_TIMESTAMP - INTERVAL '2 days 1 hour 30 minutes'),
    (3, 1, 4, CURRENT_TIMESTAMP - INTERVAL '2 days 2 hours'),
    (4, 1, 6, CURRENT_TIMESTAMP - INTERVAL '2 days 30 minutes'),
    -- Bob's GG Bridge ride gets kudos
    (5, 4, 1, CURRENT_TIMESTAMP - INTERVAL '1 day 2 hours'),
    (6, 4, 3, CURRENT_TIMESTAMP - INTERVAL '1 day 1 hour'),
    (7, 4, 7, CURRENT_TIMESTAMP - INTERVAL '1 day 30 minutes'),
    (8, 4, 8, CURRENT_TIMESTAMP - INTERVAL '23 hours'),
    -- Diana's Longs Peak hike gets kudos
    (9, 9, 1, CURRENT_TIMESTAMP - INTERVAL '10 days 4 hours'),
    (10, 9, 2, CURRENT_TIMESTAMP - INTERVAL '10 days 3 hours'),
    (11, 9, 3, CURRENT_TIMESTAMP - INTERVAL '10 days 2 hours'),
    -- Frank's 5K race gets kudos
    (12, 13, 1, CURRENT_TIMESTAMP - INTERVAL '2 days 17 hours'),
    (13, 13, 2, CURRENT_TIMESTAMP - INTERVAL '2 days 16 hours'),
    (14, 13, 6, CURRENT_TIMESTAMP - INTERVAL '2 days 15 hours'),
    -- Grace's Ironman bike gets kudos
    (15, 15, 1, CURRENT_TIMESTAMP - INTERVAL '15 days 5 hours'),
    (16, 15, 2, CURRENT_TIMESTAMP - INTERVAL '15 days 4 hours'),
    (17, 15, 8, CURRENT_TIMESTAMP - INTERVAL '15 days 3 hours');

-- Segment Efforts
INSERT INTO segment_efforts (id, segment_id, activity_id, athlete_id, elapsed_time, started_at) VALUES
    -- Alice's effort on Boston Esplanade
    (1, 1, 1, 1, 1440, CURRENT_TIMESTAMP - INTERVAL '2 days 2 hours 30 minutes'),
    (2, 1, 2, 1, 600, CURRENT_TIMESTAMP - INTERVAL '5 days 6 hours 45 minutes'),
    -- Bob's effort on Golden Gate Bridge
    (3, 2, 4, 2, 900, CURRENT_TIMESTAMP - INTERVAL '1 day 3 hours 30 minutes'),
    (4, 2, 5, 2, 720, CURRENT_TIMESTAMP - INTERVAL '4 days 4 hours 45 minutes'),
    -- Diana's effort on Boulder Creek
    (5, 6, 9, 4, 5400, CURRENT_TIMESTAMP - INTERVAL '10 days 5 hours 1 hour'),
    -- Frank's effort on Lakefront Trail
    (6, 4, 14, 6, 2700, CURRENT_TIMESTAMP - INTERVAL '5 days 9 hours'),
    -- Grace's effort on Pacific Coast Highway
    (7, 5, 15, 7, 28800, CURRENT_TIMESTAMP - INTERVAL '15 days 6 hours'),
    -- Henry's effort on Hawthorn Hill
    (8, 7, 18, 8, 1800, CURRENT_TIMESTAMP - INTERVAL '20 days 4 hours 2 hours');

-- ============================================
-- SEQUENCES (reset to max id + 1)
-- ============================================

SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1);
SELECT setval('activities_id_seq', COALESCE((SELECT MAX(id) FROM activities), 0) + 1);
SELECT setval('friendships_id_seq', COALESCE((SELECT MAX(id) FROM friendships), 0) + 1);
SELECT setval('segments_id_seq', COALESCE((SELECT MAX(id) FROM segments), 0) + 1);
SELECT setval('segment_efforts_id_seq', COALESCE((SELECT MAX(id) FROM segment_efforts), 0) + 1);
SELECT setval('kudos_id_seq', COALESCE((SELECT MAX(id) FROM kudos), 0) + 1);

-- ============================================
-- COMMENTS / NOTES
-- ============================================

-- Password hashes in this script are PLACEHOLDERS.
-- In production, generate real bcrypt hashes using:
--   python -c "from backend.services.auth_service import get_password_hash; print(get_password_hash('your_password'))"
-- Then update the password_hash values above.
-- Default password for all users in this script is 'password' (but hashed properly in app).

-- Polyline fields contain placeholder text. In production, replace with real
-- encoded polylines from GPS tracks.

-- Time values:
--   - duration: in seconds
--   - elevation: in meters
--   - distance: in kilometers (run/swim/walk/hike) or km (ride)
