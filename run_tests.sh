#!/bin/bash

# --- Configuration ---
PROJECT_DIR="."
ENV_FILE=".env"

# --- Functions ---
function print_status() {
    echo "--- $1 ---"
}

# --- Main Script ---
set -e # Exit immediately if a command exits with a non-zero status.

print_status "Starting Cap Table Backend test setup script"

# 3. Setup Environment Variables
if [ ! -f "$ENV_FILE" ]; then
    print_status "Creating a .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp ".env.example" "$ENV_FILE"
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
    print_status "DATABASE_URL environment variable set to $DATABASE_URL"
else
    echo "Warning: DB_USER, DB_PASSWORD, or DB_NAME not found in .env. DATABASE_URL not set."
fi

# 6. Run the Tests
print_status "Running tests with pytest..."
export PYTHONPATH=$PYTHONPATH:/workspace/_CAP_table_test  # Adjust path for Gitpod
pytest tests/ -v
print_status "Tests completed."
