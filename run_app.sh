#!/bin/bash

# This script automates the setup and execution of the Cap Table Management Backend
# for local testing. It now dynamically creates and exports the DATABASE_URL
# environment variable for the application to use.

# --- Configuration ---
PROJECT_DIR="."  # Assuming you are running the script from the project root
VENV_DIR="venv"
DB_NAME="captable_db"
REQUIREMENTS_FILE="requirements.txt"
ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"

# --- Functions ---
function print_status() {
    echo "--- $1 ---"
}

# --- Main Script ---
set -e # Exit immediately if a command exits with a non-zero status.

print_status "Starting Cap Table Backend setup script"

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it to proceed."
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "Error: psql is not installed. Please ensure PostgreSQL is installed and in your PATH."
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory not found. Please run this script from the root of the project."
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 2. Install Dependencies
# Ensure python-dotenv is installed along with the other requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    print_status "Installing Python dependencies..."
    pip install -r "$REQUIREMENTS_FILE"
    pip install python-dotenv
else
    echo "Error: $REQUIREMENTS_FILE not found. Cannot install dependencies."
    exit 1
fi

# 3. Setup Environment Variables
if [ ! -f "$ENV_FILE" ]; then
    print_status "Creating a .env file from .env.example..."
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
        echo "A new .env file has been created. Please edit it with your database credentials and JWT secret."
    else
        echo "Error: .env.example not found. Cannot create environment file."
        exit 1
    fi
fi

# Load database credentials from .env and create DATABASE_URL
# This loop handles simple key=value or key="value" pairs
# Note: It assumes the database host is 'localhost' unless specified in .env
print_status "Constructing DATABASE_URL from .env variables..."
DB_USER=""
DB_PASSWORD=""
DB_NAME=""
DB_HOST="localhost" # Default host if not specified in .env

while read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^# ]] || [[ -z "$line" ]]; then
        continue
    fi
    # Use a case statement to handle each variable
    case "$line" in
        DB_USER=*) DB_USER=$(echo "$line" | cut -d'=' -f2- | tr -d '"') ;;
        DB_PASSWORD=*) DB_PASSWORD=$(echo "$line" | cut -d'=' -f2- | tr -d '"') ;;
        DB_NAME=*) DB_NAME=$(echo "$line" | cut -d'=' -f2- | tr -d '"') ;;
        DB_HOST=*) DB_HOST=$(echo "$line" | cut -d'=' -f2- | tr -d '"') ;;
    esac
done < "$ENV_FILE"

# Construct the full DATABASE_URL
if [ -n "$DB_USER" ] && [ -n "$DB_PASSWORD" ] && [ -n "$DB_NAME" ]; then
    DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}/${DB_NAME}"
    export DATABASE_URL
    print_status "DATABASE_URL environment variable set."
else
    echo "Warning: DB_USER, DB_PASSWORD, or DB_NAME not found in .env. DATABASE_URL not set."
fi


# 4. Create PostgreSQL Database
print_status "Attempting to create PostgreSQL database: $DB_NAME"
# Use a quieter psql command to avoid verbose output if the DB already exists
psql -c "CREATE DATABASE $DB_NAME" > /dev/null 2>&1 || echo "Note: Database $DB_NAME may already exist."

# 5. Reminder for Redis
print_status "Setup complete. Remember to ensure your Redis server is running!"

# 6. Run the Application using uvicorn with dotenv
print_status "Starting the FastAPI application with uvicorn..."
print_status "API available at http://localhost:8000"
print_status "API docs at http://localhost:8000/docs"
print_status "Use 'Ctrl+C' to stop the server."
print_status "Seeded credentials: Admin (admin/adminpass), Shareholder (shareholder1/shpass)."

# Use the `dotenv` command to load the remaining variables from .env and then run uvicorn.
# This ensures all environment variables are correctly set for the process.
dotenv run -- uvicorn app.main:app --host "0.0.0.0" --port 8000 --workers 4

