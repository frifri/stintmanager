# StintManager

StintManager is a Django application for managing driver stints in motorsport endurance races. It helps teams plan driver rotations, keep track of availability windows, and optimize race strategies.

## Features

- Create and manage race entries
- Track driver availability during race events
- Plan and optimize driver rotations
- Team management for collaborative stint planning
- Timeline visualization of driving assignments
- ...

## Setup

### Prerequisites

- Python 3.12
- Poetry for dependency management

### Quick Setup

For a quick reset and setup (useful during development):

```bash
make reset
```

This command will:
- Delete the existing database
- Run all migrations
- Create a superuser (you'll be prompted for credentials)

## Development

The application will be available at http://127.0.0.1:8000/

### Other useful commands:

```bash
# Collect static files
make static

# Create sample data
make sample-data
```

## Project Structure

- `core/` - Core functionality, user authentication
- `races/` - Race management and stint planning
- `teams/` - Team collaboration features