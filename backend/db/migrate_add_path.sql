-- Migration: add path/common_activity support to activities
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE activities ADD COLUMN IF NOT EXISTS path GEOMETRY(LineString, 4326);
ALTER TABLE activities ADD COLUMN IF NOT EXISTS common_activity_id INTEGER;

CREATE TABLE IF NOT EXISTS common_activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    polyline TEXT,
    path GEOMETRY(LineString, 4326),
    distance FLOAT,
    sport_type sport_type
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'activities_common_activity_id_fkey') THEN
    ALTER TABLE activities ADD CONSTRAINT activities_common_activity_id_fkey
      FOREIGN KEY (common_activity_id) REFERENCES common_activities(id);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_activities_path ON activities USING GIST(path);
CREATE INDEX IF NOT EXISTS idx_activities_common_activity_id ON activities(common_activity_id);
CREATE INDEX IF NOT EXISTS idx_common_activities_path ON common_activities USING GIST(path);

GRANT ALL ON common_activities TO runbandits;
GRANT USAGE, SELECT ON SEQUENCE common_activities_id_seq TO runbandits;
