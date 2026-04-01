# Phase 2: Database Setup

This folder contains the Supabase connection setup and SQL schemas.

## Overview
- `database.py`: Supabase client initialization.
- `schema.sql`: SQL commands to run in the Supabase Dashboard to create tables for Users, Recipients, Interactions, etc.
- `crud.py`: Basic CRUD operations for the database.
- `tests/test_db.py`: Mock tests for database interactions to ensure logic is sound without hitting real DB.

## Getting Started
1. Run `schema.sql` inside the Supabase SQL editor.
2. Ensure you have `SUPABASE_URL` and `SUPABASE_KEY` set in your `.env` file before executing DB logic.

## Testing
1. Install requirements: `pip install -r requirements.txt`
2. Run mock tests: `pytest`
