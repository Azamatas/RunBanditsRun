-- PostgreSQL data population script for RunBanditsRun
-- INSERTs ONLY - no DDL
-- Run this AFTER init_db.sql to populate with seed data

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
    (4, 'diana_hiker', 'diana@example.com', '$2b$12$dummyhashdiana', 'Trail runner and mountain hiker. Love the great outdoors!', 'Denver, CO', CURRENT_TIMESTAMP - INTERVAL '15 days'),
    (5, 'eve_walker', 'eve@example.com', '$2b$12$dummyhasheve', 'Casual walker, love city walks and nature trails.', 'New York, NY', CURRENT_TIMESTAMP - INTERVAL '10 days'),
    (6, 'frank_runner', 'frank@example.com', '$2b$12$dummyhashfrank', '5K and 10K specialist. Always chasing a new PR!', 'Chicago, IL', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    (7, 'grace_triathlete', 'grace@example.com', '$2b$12$dummyhashgrace', 'Ironman finisher. Bike, run, repeat.', 'Austin, TX', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    (8, 'henry_cyclist', 'henry@example.com', '$2b$12$dummyhashhenry', 'Gravel rider and bike packer.', 'Portland, OR', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- Common Activities (auto-generated from frequent routes)
INSERT INTO common_activities (id, name, polyline, path, distance, sport_type) VALUES
    (1, 'Auto: run Path 1', 'Encoded polyline for common run route 1', ST_Transform(ST_LineFromEncodedPolyline('Encoded polyline for common run route 1'), 3857), 5.0, 'run'),
    (2, 'Auto: ride Path 1', 'Encoded polyline for common ride route 1', ST_Transform(ST_LineFromEncodedPolyline('Encoded polyline for common ride route 1'), 3857), 25.0, 'ride');

-- Activities with realistic data
INSERT INTO activities (id, owner_id, title, sport_type, distance, duration, elevation, polyline, visibility, started_at, created_at, common_activity_id) VALUES
    -- Alice's activities (runner)
    (1, 1, 'Morning Long Run', 'run', 16.5, 6240, 85.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '2 days 2 hours', CURRENT_TIMESTAMP - INTERVAL '2 days', 1),
    (2, 1, 'Tempo Run on Esplanade', 'run', 8.2, 2400, 15.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '5 days 6 hours', CURRENT_TIMESTAMP - INTERVAL '5 days', NULL),
    (3, 1, 'Recovery Run', 'run', 5.0, 2520, 5.0, 'Encoded polyline', 'friends', CURRENT_TIMESTAMP - INTERVAL '8 days 7 hours', CURRENT_TIMESTAMP - INTERVAL '8 days', NULL),
    -- Bob's activities (cyclist)
    (4, 2, 'Mount Tam ride', 'ride', 56.0, 15600, 1450.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '1 day 3 hours', CURRENT_TIMESTAMP - INTERVAL '1 day', 2),
    (5, 2, 'Golden Gate Bridge loops', 'ride', 42.3, 9800, 620.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '4 days 4 hours', CURRENT_TIMESTAMP - INTERVAL '4 days', NULL),
    (6, 2, 'Commute to work', 'ride', 12.5, 2400, 55.0, 'Encoded polyline', 'private', CURRENT_TIMESTAMP - INTERVAL '7 days 8 hours', CURRENT_TIMESTAMP - INTERVAL '7 days', NULL),
    -- Diana's activities (hiker)
    (9, 4, 'Longs Peak Ascent', 'hike', 14.5, 28800, 1450.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '10 days 5 hours', CURRENT_TIMESTAMP - INTERVAL '10 days', NULL),
    (10, 4, 'Rocky Mountain National Park Trail', 'hike', 8.7, 14400, 620.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '12 days 7 hours', CURRENT_TIMESTAMP - INTERVAL '12 days', NULL),
    -- Eve's activities (walker)
    (11, 5, 'Central Park Walk', 'walk', 5.0, 6000, 10.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '1 day 10 hours', CURRENT_TIMESTAMP - INTERVAL '1 day', NULL),
    (12, 5, 'Hudson River Greenway', 'walk', 3.8, 4200, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '3 days 14 hours', CURRENT_TIMESTAMP - INTERVAL '3 days', NULL),
    -- Frank's activities (runner)
    (13, 6, '5K Race', 'run', 5.0, 1260, 0.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '2 days 18 hours', CURRENT_TIMESTAMP - INTERVAL '2 days', NULL),
    (14, 6, 'Lakefront 10K', 'run', 10.0, 2700, 5.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '5 days 9 hours', CURRENT_TIMESTAMP - INTERVAL '5 days', NULL),
    -- Grace's activities (triathlete)
    (15, 7, 'Ironman Training - Long Bike', 'ride', 112.0, 288000, 2000.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '15 days 6 hours', CURRENT_TIMESTAMP - INTERVAL '15 days', NULL),
    (17, 7, 'Brick Workout - Bike to Run', 'run', 10.0, 3000, 25.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '17 days 8 hours', CURRENT_TIMESTAMP - INTERVAL '17 days', NULL),
    -- Henry's activities (cyclist)
    (18, 8, 'Gravel Century', 'ride', 100.0, 36000, 3200.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '20 days 4 hours', CURRENT_TIMESTAMP - INTERVAL '20 days', NULL),
    (19, 8, 'Forest Park Loops', 'ride', 25.5, 6600, 240.0, 'Encoded polyline', 'public', CURRENT_TIMESTAMP - INTERVAL '22 days 5 hours', CURRENT_TIMESTAMP - INTERVAL '22 days', NULL);

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
    (2, 1, 4, 'accepted', CURRENT_TIMESTAMP - INTERVAL '18 days'),
    (3, 2, 1, 'accepted', CURRENT_TIMESTAMP - INTERVAL '24 days'),
    (4, 2, 4, 'accepted', CURRENT_TIMESTAMP - INTERVAL '15 days'),
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
    (2, 1, 4, CURRENT_TIMESTAMP - INTERVAL '2 days 2 hours'),
    (3, 1, 6, CURRENT_TIMESTAMP - INTERVAL '2 days 30 minutes'),
    -- Bob's GG Bridge ride gets kudos
    (4, 4, 1, CURRENT_TIMESTAMP - INTERVAL '1 day 2 hours'),
    (5, 4, 7, CURRENT_TIMESTAMP - INTERVAL '1 day 30 minutes'),
    (6, 4, 8, CURRENT_TIMESTAMP - INTERVAL '23 hours'),
    -- Diana's Longs Peak hike gets kudos
    (7, 9, 1, CURRENT_TIMESTAMP - INTERVAL '10 days 4 hours'),
    (8, 9, 2, CURRENT_TIMESTAMP - INTERVAL '10 days 3 hours'),
    -- Frank's 5K race gets kudos
    (9, 13, 1, CURRENT_TIMESTAMP - INTERVAL '2 days 17 hours'),
    (10, 13, 2, CURRENT_TIMESTAMP - INTERVAL '2 days 16 hours'),
    (11, 13, 6, CURRENT_TIMESTAMP - INTERVAL '2 days 15 hours'),
    -- Grace's Ironman bike gets kudos
    (12, 15, 1, CURRENT_TIMESTAMP - INTERVAL '15 days 5 hours'),
    (13, 15, 2, CURRENT_TIMESTAMP - INTERVAL '15 days 4 hours'),
    (14, 15, 8, CURRENT_TIMESTAMP - INTERVAL '15 days 3 hours');

-- ========================================================================================
-- SEQUENCES (reset to max id + 1)
-- ============================================

SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1);
SELECT setval('activities_id_seq', COALESCE((SELECT MAX(id) FROM activities), 0) + 1);
SELECT setval('common_activities_id_seq', COALESCE((SELECT MAX(id) FROM common_activities), 0) + 1);
SELECT setval('friendships_id_seq', COALESCE((SELECT MAX(id) FROM friendships), 0) + 1);
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
--   - distance: in kilometers (run/walk/hike/ride)
