#!/usr/bin/env bash
# Simple setup script for StintManager

# Exit on error
set -e

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python 3.12 or later."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install Poetry first."
    echo "Visit https://python-poetry.org/docs/#installation for instructions."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Activate the virtual environment
echo "Activating virtual environment..."
poetry shell

# Run the reset script
echo "Resetting the database..."
python scripts/reset_db.py

# Run the development server
echo "Starting the development server..."
python manage.py runserver