# Cap Table Management Backend

## Overview

This project implements a robust backend for a Corporate OS platform, focused on managing a company's **capitalization table (Cap Table)** and issuing shares. The backend is built with **FastAPI**, leveraging its asynchronous capabilities and automatic API documentation. It adheres to the **Clean Architecture** principle to ensure a strong separation of concerns, promoting **maintainability, testability, and extensibility**.

### Key Architectural Decisions 🏗️

  * **Clean Architecture**: The project is structured into distinct layers:
      * **Domain Layer**: Contains the core business logic, including entities (User, Shareholder, ShareIssuance) and use cases (e.g., AuthenticateUser, CreateIssuance). This layer is independent of any frameworks.
      * **Adapters Layer**: Interfaces with external components. This includes **repositories** (using **SQLAlchemy** for PostgreSQL) for data persistence and **controllers** (FastAPI endpoints) for handling API requests.
      * **Infrastructure Layer**: Manages external services like database connections, PDF generation with **ReportLab**, and caching with **Redis**.
  * **Authentication**: Implements a secure **JWT-based authentication** system with **role-based access control** (admin vs. shareholder). It uses **bcrypt** for robust password hashing, **rate limiting** with `slowapi`, and validates JWT claims for enhanced security.
  * **Database**: Utilizes **PostgreSQL** for its reliability and relational data integrity, with connection pooling for better performance.
  * **Scalability**: The application is designed for scalability with support for multi-worker deployment via Uvicorn/Gunicorn. **Redis caching** is implemented for read-heavy operations to reduce database load (this setup is **optional** but recommended for production).
  * **Security Fixes**: Key vulnerabilities have been addressed by using environment variables for secrets, secure password hashing, and implementing HTTPS support via **Nginx** in the Docker setup.
  * **Bonus Features**: Includes an audit trail feature using an `AuditEvent` model, advanced data validation (e.g., preventing negative share issuances), and simulated email notifications via console logs.
  * **Containerization**: The entire application is **Dockerized** to provide an isolated and easily scalable environment.

-----

## Prerequisites

Before setting up the project, ensure you have the following installed.

  * **Python 3.10+**
  * **PostgreSQL 14+**
  * **Redis 7+** (Optional but recommended for caching)
  * **Git**
  * **Docker** and **Docker Compose** (Recommended for the containerized setup)

-----

## Setup and Run Locally

You have three options for running the application: a direct local setup using scripts, a manual local setup, or the recommended Dockerized setup.

### Option 1: Automated Local Setup with Scripts (Recommended)

This is the fastest way to get the application running on your local machine. The provided scripts automate most of the setup process.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/joelinator/_CAP_table_test.git
    cd _CAP_table_test
    ```
2.  **Configure Environment Variables**:
      * Create a `.env` file by copying the provided `.env.example` file:
        ```bash
        cp .env.example .env
        ```
      * Open the new `.env` file and fill in your database credentials and a secure `JWT_SECRET`. The script uses these variables to create the `DATABASE_URL` and connect to your database.
        ```ini
        DB_USER=your_postgres_username
        DB_PASSWORD=your_postgres_password
        DB_NAME=captable_db
        JWT_SECRET=a_super_secret_key
        REDIS_HOST=localhost # Optional, but required if you use Redis
        ```
3.  **Ensure Services Are Running**:
      * **PostgreSQL**: Make sure your PostgreSQL server is running.
      * **Redis**: If you plan to use caching, ensure your Redis server is running as well.
4.  **Run the Script**:
      * **On macOS/Linux**, use the bash script `run_app.sh`:
        ```bash
        chmod +x run_app.sh
        ./run_app.sh
        ```
      * **On Windows**, use the batch script `run_app.bat`:
        ```bat
        run_app.bat
        ```
    The script will create a virtual environment, install dependencies, create the PostgreSQL database (if it doesn't exist), and then start the application automatically.

-----

### Option 2: Without Scripts (Manual Local Setup)

This option requires you to have PostgreSQL and Redis running directly on your machine.

1.  **Clone the Repository and Navigate to the Project Directory**:
    ```bash
    git clone https://github.com/joelinator/_CAP_table_test.git
    cd _CAP_table_test
    ```
2.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    pip install python-dotenv
    ```
4.  **Configure Environment Variables**:
      * Create a `.env` file by copying the provided `.env.example` file:
        ```bash
        cp .env.example .env
        ```
      * Open `.env` and fill in your database credentials and a secure `JWT_SECRET`. A new `DATABASE_URL` will be created from the provided variables. For example:
        ```ini
        DB_USER=your_postgres_username
        DB_PASSWORD=your_postgres_password
        DB_NAME=captable_db
        JWT_SECRET=a_super_secret_key
        REDIS_HOST=localhost # Optional
        ```
5.  **Set Up PostgreSQL and Redis**:
      * **PostgreSQL**: Ensure your PostgreSQL server is running, and create the database specified in your `.env` file. The application will automatically create all necessary tables on startup.
        ```bash
        psql -c "CREATE DATABASE captable_db"
        ```
      * **Redis**: If you're using Redis for caching, ensure it is running on the default port `6379`.
6.  **Run the Application**:
      * Set the **`DATABASE_URL`** environment variable in your terminal session. Replace the credentials with your own:
        ```bash
        export DATABASE_URL="postgresql://your_postgres_username:your_postgres_password@localhost/captable_db"
        ```
      * Run the application using the `dotenv` command to load all environment variables:
        ```bash
        dotenv run -- uvicorn app.main:app --host "0.0.0.0" --port 8000 --workers 4
        ```
      * Alternatively, you can manually set all environment variables and then run the application:
        ```bash
        # (Example for bash/zsh)
        export DB_USER=your_postgres_username
        export DB_PASSWORD=your_postgres_password
        # ... and so on for all variables in .env
        uvicorn app.main:app --host "0.0.0.0" --port 8000 --workers 4
        ```

-----

### Option 3: With Docker (Recommended for Isolation and Scalability)

This is the recommended approach as it sets up a fully isolated environment with PostgreSQL, Redis, and an Nginx proxy.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/joelinator/_CAP_table_test.git
    cd https://github.com/joelinator/_CAP_table_test.git
    ```
2.  **Set Up Environment Variables**:
    Create a `.env` file in the root directory with at least a secure `JWT_SECRET`. Other variables like `DATABASE_URL` are configured within the `docker-compose.yml` file.
3.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
      * This command orchestrates the startup of the backend, PostgreSQL, Redis, and Nginx containers.
      * The API will be accessible via **Nginx** at `http://localhost:8000`.
      * To stop the services, run `docker-compose down`.

-----

## Accessing the Application

Once the application is running, you can access it as follows:

  * **API URL**: `http://localhost:8000`
  * **API Docs**: `http://localhost:8000/docs`
  * **Default Seeded Credentials** (if `SEED_DATA` is true):
      * **Admin**: username `admin`, password `adminpass`
      * **Shareholder**: username `shareholder1`, password `shpass`

-----

## Primary AI Tools Used

This project was developed with significant assistance from the following AI tools:

  * **GitHub Copilot**: Used for code completions and contextual suggestions.
-----

## Key Prompts Used 🗣️

The following prompts were instrumental in accelerating the project's development:

  * "Generate a Python backend using FastAPI and Clean Architecture for a cap table management system. Include entities for User, Shareholder, ShareIssuance; use cases for authentication, listing shareholders, issuing shares; repositories with SQLAlchemy for PostgreSQL; and API controllers. Follow this API contract: [pasted spec]."
  * "How to implement JWT authentication in FastAPI with role-based access, including token creation and validation with issuer and audience claims?"
  * "Add bcrypt password hashing to this User creation and authentication code: [pasted code snippet]."
  * "Implement Redis caching for a list endpoint in FastAPI to cache shareholder data, including cache invalidation on mutations."
  * "Write unit tests using pytest for validation logic in a share issuance use case, checking for negative shares and non-existent shareholders."
  * "Create a Dockerfile and docker-compose.yml for a FastAPI app with PostgreSQL, Redis, and Nginx for HTTPS, including environment variable handling."
