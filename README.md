I will improve the provided `README.md` file by updating it for clarity, better organization, and improved highlighting of key information.

Here is the updated and improved `README.md` file.

# Cap Table Management Backend

## Overview

This project implements a robust backend for a Corporate OS platform, focused on managing a company's **capitalization table (Cap Table)** and issuing shares.  The backend is built with **FastAPI**, leveraging its asynchronous capabilities and automatic API documentation. It adheres to the **Clean Architecture** principle to ensure a strong separation of concerns, promoting **maintainability, testability, and extensibility**.

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

  * **Python 3.10+** (for non-Docker setup)
  * **PostgreSQL 14+**
  * **Redis 7+** (Optional but recommended for caching)
  * **Docker** and **Docker Compose** (Recommended for the containerized setup)
  * **Git**

-----

## Setup and Run Locally

You have two options for running the application: a direct local setup or the recommended Dockerized setup.

### Option 1: Without Docker (Direct Local Setup)

This option requires you to have PostgreSQL and Redis running directly on your machine.

1.  **Clone the Repository**:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**:
    Create a `.env` file in the root directory by copying the provided `.env.example` file. You must set the following variables:

    ```ini
    DATABASE_URL=postgresql://user:password@localhost:5432/captable_db
    JWT_SECRET=your_strong_random_secret_key_here
    REDIS_HOST=localhost
    # By default, SEED_DATA is set to 'true' to add initial users.
    SEED_DATA=true
    ```

    🚨 **Important:** The `SEED_DATA=true` setting is enabled by default for easy local testing. This automatically creates an admin user and a sample shareholder. Remember to set this to `false` in any production environment.

5.  **Set Up PostgreSQL and Redis**:

      * **PostgreSQL**: Create the database by running `createdb captable_db`. The application will automatically create all necessary tables on startup.
      * **Redis**: Ensure Redis is running on the default port `6379`.

6.  **Run the Application**:

    ```bash
    python app/main.py
    ```

      * The API will be available at `http://localhost:8000`.
      * To access the API documentation, visit `http://localhost:8000/docs`.
      * **Default Seeded Credentials** (if `SEED_DATA` is true):
          * **Admin**: username `admin`, password `adminpass`
          * **Shareholder**: username `shareholder1`, password `shpass`

-----

### Option 2: With Docker (Recommended for Isolation and Scalability)

This is the recommended approach as it sets up a fully isolated environment with PostgreSQL, Redis, and an Nginx proxy.

1.  **Clone the Repository**:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
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

## Primary AI Tools Used

This project was developed with significant assistance from the following AI tools:

  * **GitHub Copilot**: Used for code completions and contextual suggestions.
  * **Cursor's Chat**: Aided in generating boilerplate code and debugging complex issues.
  * **Gemini Advanced**: Provided crucial architectural advice on implementing Clean Architecture and ensuring security best practices.

-----

## Key Prompts Used 🗣️

The following prompts were instrumental in accelerating the project's development:

  * "Generate a Python backend using FastAPI and Clean Architecture for a cap table management system. Include entities for User, Shareholder, ShareIssuance; use cases for authentication, listing shareholders, issuing shares; repositories with SQLAlchemy for PostgreSQL; and API controllers. Follow this API contract: [pasted spec]."
  * "How to implement JWT authentication in FastAPI with role-based access, including token creation and validation with issuer and audience claims?"
  * "Add bcrypt password hashing to this User creation and authentication code: [pasted code snippet]."
  * "Implement Redis caching for a list endpoint in FastAPI to cache shareholder data, including cache invalidation on mutations."
  * "Write unit tests using pytest for validation logic in a share issuance use case, checking for negative shares and non-existent shareholders."
  * "Create a Dockerfile and docker-compose.yml for a FastAPI app with PostgreSQL, Redis, and Nginx for HTTPS, including environment variable handling."
