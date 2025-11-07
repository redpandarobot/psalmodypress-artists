-- Psalmody Press Artists - Prompt Tracking Database Schema

-- Main prompts table - stores all generated prompts with their unique IDs
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_id TEXT UNIQUE NOT NULL,           -- 5-character base-36 ID (e.g., 'EO8HB')
    prompt_type TEXT NOT NULL,                  -- 'suno_lyrics', 'suno_music', 'midjourney', 'typography'
    psalm_number INTEGER NOT NULL,              -- 1-150
    artist_name TEXT NOT NULL,                  -- Artist identifier
    prompt_text TEXT NOT NULL,                  -- The actual prompt sent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                               -- JSON field for additional data
);

-- Index for fast lookups by sequence_id
CREATE INDEX IF NOT EXISTS idx_sequence_id ON prompts(sequence_id);

-- Index for lookups by psalm and artist
CREATE INDEX IF NOT EXISTS idx_psalm_artist ON prompts(psalm_number, artist_name);

-- Index for lookups by prompt type
CREATE INDEX IF NOT EXISTS idx_prompt_type ON prompts(prompt_type);

-- Sequence counter table - tracks the last used sequence number
CREATE TABLE IF NOT EXISTS sequence_counter (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    current_value INTEGER NOT NULL DEFAULT 0,   -- Current sequence number (0 to 60466175)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize sequence counter if not exists
INSERT OR IGNORE INTO sequence_counter (id, current_value) VALUES (1, 0);

-- Generated assets table - links sequence IDs to actual files from Suno/Midjourney
CREATE TABLE IF NOT EXISTS generated_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_id TEXT NOT NULL,                  -- Links to prompts.sequence_id
    asset_type TEXT NOT NULL,                   -- 'suno_song', 'midjourney_image'
    original_filename TEXT,                     -- Original filename from service
    our_filename TEXT,                          -- Our renamed file
    file_path TEXT,                             -- Path to the file
    service_metadata TEXT,                      -- JSON field for service-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sequence_id) REFERENCES prompts(sequence_id)
);

-- Index for asset lookups
CREATE INDEX IF NOT EXISTS idx_asset_sequence ON generated_assets(sequence_id);
CREATE INDEX IF NOT EXISTS idx_asset_type ON generated_assets(asset_type);

-- View for easy prompt lookup with all related info
CREATE VIEW IF NOT EXISTS prompt_lookup AS
SELECT
    p.sequence_id,
    p.prompt_type,
    p.psalm_number,
    p.artist_name,
    p.prompt_text,
    p.created_at,
    p.metadata,
    COUNT(g.id) as asset_count
FROM prompts p
LEFT JOIN generated_assets g ON p.sequence_id = g.sequence_id
GROUP BY p.sequence_id;
