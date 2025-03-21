#!/usr/bin/env python
"""
Script to reset the database, run migrations, and create a superuser.
"""
import os
import sys
import subprocess
import getpass
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database path
DB_PATH = BASE_DIR / 'db.sqlite3'

def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {' '.join(command)}")
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"Error: {process.stderr}")
        sys.exit(1)
    return process.stdout.strip()

def reset_database():
    """Delete the database file if it exists."""
    if DB_PATH.exists():
        print(f"Removing database: {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print("No database file to remove.")

def run_migrations():
    """Run makemigrations and migrate commands."""
    print("Running makemigrations...")
    run_command(['python', 'manage.py', 'makemigrations'])
    
    print("Running migrate...")
    run_command(['python', 'manage.py', 'migrate'])

def create_superuser():
    """Create a superuser with default credentials or prompt for custom ones."""
    print("\nDo you want to create a superuser with default credentials?")
    print("Default: admin@example.com / admin123")
    user_choice = input("Use default credentials? (y/n): ").strip().lower()
    
    if user_choice == 'y':
        email = 'admin@example.com'
        password = 'admin123'
        first_name = 'Admin'
        last_name = 'User'
    else:
        email = input("Email: ").strip()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        password = getpass.getpass("Password: ")
    
    # Create a Python script to create the superuser
    script = f"""
from core.models import User
User.objects.create_superuser(
    email='{email}',
    password='{password}',
    first_name='{first_name}',
    last_name='{last_name}'
)
print("Superuser created successfully.")
"""
    
    # Run the script using Django's shell
    print("Creating superuser...")
    process = subprocess.run(
        ['python', 'manage.py', 'shell'],
        input=script,
        text=True,
        capture_output=True
    )
    
    if process.returncode != 0:
        print(f"Error creating superuser: {process.stderr}")
        sys.exit(1)
    else:
        print(process.stdout)

def create_sample_data():
    """Ask if sample data should be created."""
    print("\nDo you want to create sample data? (y/n): ")
    user_choice = input().strip().lower()
    
    if user_choice == 'y':
        print("Creating sample data...")
        try:
            # Run the sample data script as a subprocess
            script_path = os.path.join(BASE_DIR, 'scripts', 'create_sample_data.py')
            result = subprocess.run(['python', script_path], check=True)
            if result.returncode != 0:
                print("Error creating sample data.")
        except Exception as e:
            print(f"Error creating sample data: {e}")
    else:
        print("Skipping sample data creation.")

def main():
    """Main function to reset the database and set up the project."""
    print("=== Database Reset Tool ===")
    
    # Confirm before proceeding
    print("\nWARNING: This will delete your database and all data!")
    confirm = input("Are you sure you want to continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Reset database
    reset_database()
    
    # Run migrations
    run_migrations()
    
    # Create superuser
    create_superuser()
    
    # Optionally create sample data
    create_sample_data()
    
    print("\n=== Database reset complete! ===")
    print("You can now run the development server with:")
    print("python manage.py runserver")

if __name__ == "__main__":
    main()