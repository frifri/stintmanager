.PHONY: reset static help sample-data

PYTHON = python

# Default target
help:
	@echo "Available commands:"
	@echo "  make reset       - Reset the database, run migrations and create a superuser"
	@echo "  make static      - Collect static files"
	@echo "  make sample-data - Create sample data for testing"

# Reset the database, run migrations and create a superuser
reset:
	@echo "Resetting the database..."
	$(PYTHON) scripts/reset_db.py

# Collect static files
static:
	@echo "Collecting static files..."
	python manage.py collectstatic --noinput

# Create sample data
sample-data:
	@echo "Creating sample data..."
	$(PYTHON) scripts/create_sample_data.py