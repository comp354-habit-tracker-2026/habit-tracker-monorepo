PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,

    name TEXT NOT NULL,
    
    type TEXT NOT NULL,
    start_time TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL CHECK(duration_seconds >= 0),
    distance_meters INTEGER,
    calories INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (provider, external_id)
);

CREATE INDEX IF NOT EXISTS idx_activities_user_start_time
ON activities(user_id, start_time DESC);

CREATE INDEX IF NOT EXISTS idx_activities_provider_external
ON activities(provider, external_id);

CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    target_value INTEGER NOT NULL CHECK(target_value > 0),
    period_start TEXT NOT NULL,
    period_end TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_goals_user_id
ON goals(user_id);