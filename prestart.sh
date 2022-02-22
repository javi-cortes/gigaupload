#! /usr/bin/env bash

cd /app

# Create tables DB
python app/db/database.py

# Create dummy stubs
python app/initial_mock_data.py

# Run migrations
alembic upgrade head
