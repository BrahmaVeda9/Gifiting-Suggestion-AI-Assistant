-- ============================================================
-- Dearly AI — Supabase Migrations
-- Run this entire file once in your Supabase SQL Editor
-- ============================================================

-- Table: note_copies
-- Tracks every time a user copies a personalised note
CREATE TABLE IF NOT EXISTS note_copies (
  id            UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id    TEXT         NOT NULL,
  idea_title    TEXT         NOT NULL,
  user_location TEXT,
  copied_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Table: idea_ratings
-- Stores user star ratings (1-5) and optional written feedback
CREATE TABLE IF NOT EXISTS idea_ratings (
  id            UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id    TEXT         NOT NULL,
  idea_title    TEXT         NOT NULL,
  rating        SMALLINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
  feedback_text TEXT,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security on both tables
ALTER TABLE note_copies   ENABLE ROW LEVEL SECURITY;
ALTER TABLE idea_ratings  ENABLE ROW LEVEL SECURITY;

-- Allow anonymous (anon key) to insert and select
CREATE POLICY "anon_insert_copies"  ON note_copies   FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select_copies"  ON note_copies   FOR SELECT TO anon USING (true);
CREATE POLICY "anon_insert_ratings" ON idea_ratings  FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select_ratings" ON idea_ratings  FOR SELECT TO anon USING (true);

-- Optional: indexes for faster admin queries
CREATE INDEX IF NOT EXISTS idx_note_copies_session   ON note_copies  (session_id);
CREATE INDEX IF NOT EXISTS idx_note_copies_title     ON note_copies  (idea_title);
CREATE INDEX IF NOT EXISTS idx_idea_ratings_session  ON idea_ratings (session_id);
CREATE INDEX IF NOT EXISTS idx_idea_ratings_title    ON idea_ratings (idea_title);
