-- PostgreSQL schema initialization for RunBanditsRun
-- DDL ONLY - no data insertion

-- ============================================
-- EXTENSIONS
-- ============================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- ENUMS (must be created before tables)
-- ============================================

CREATE TYPE sport_type AS ENUM ('run', 'ride', 'walk', 'hike');
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

CREATE TABLE IF NOT EXISTS common_activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    polyline TEXT,
    path GEOMETRY(LineString, 3857),   -- Web Mercator (meter units)
    distance FLOAT,
    sport_type sport_type
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
    path GEOMETRY(LineString, 3857),   -- Web Mercator (meter units)
    visibility visibility DEFAULT 'public',
    started_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    common_activity_id INTEGER REFERENCES common_activities(id)
);

CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    addressee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status friendship_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (requester_id, addressee_id)
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

CREATE INDEX IF NOT EXISTS idx_users_id ON users(id);
CREATE INDEX IF NOT EXISTS idx_activities_owner_id ON activities(owner_id);
CREATE INDEX IF NOT EXISTS idx_activities_started_at ON activities(started_at);
CREATE INDEX IF NOT EXISTS idx_activities_visibility ON activities(visibility);
CREATE INDEX IF NOT EXISTS idx_activities_path ON activities USING GIST(path);
CREATE INDEX IF NOT EXISTS idx_activities_common_activity_id ON activities(common_activity_id);
CREATE INDEX IF NOT EXISTS idx_common_activities_path ON common_activities USING GIST(path);
CREATE INDEX IF NOT EXISTS idx_friendships_requester_id ON friendships(requester_id);
CREATE INDEX IF NOT EXISTS idx_friendships_addressee_id ON friendships(addressee_id);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status);
CREATE INDEX IF NOT EXISTS idx_kudos_activity_id ON kudos(activity_id);
CREATE INDEX IF NOT EXISTS idx_kudos_user_id ON kudos(user_id);

-- ============================================
-- FUNCTIONS
-- ============================================

CREATE OR REPLACE FUNCTION decode_polyline_to_geom(encoded TEXT)
RETURNS GEOMETRY(LineString, 3857) AS $$
  SELECT ST_Transform(ST_LineFromEncodedPolyline(encoded), 3857);
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION update_activity_path()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.polyline IS NOT NULL THEN
    NEW.path := decode_polyline_to_geom(NEW.polyline);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_activity_path
BEFORE INSERT OR UPDATE ON activities
FOR EACH ROW EXECUTE FUNCTION update_activity_path();

CREATE OR REPLACE FUNCTION update_common_activity_path()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.polyline IS NOT NULL THEN
    NEW.path := decode_polyline_to_geom(NEW.polyline);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_common_activity_path
BEFORE INSERT OR UPDATE ON common_activities
FOR EACH ROW EXECUTE FUNCTION update_common_activity_path();
