# Cap Table Management Backend

## Overview
This project implements a backend for a Corporate OS platform focused on managing a company's capitalization table (Cap Table) and issuing shares. The technical approach uses FastAPI as the web framework for its async capabilities, performance, and automatic API documentation. We followed the Clean Architecture principle to ensure separation of concerns: 
- **Domain Layer**: Contains core business entities (e.g., User, Shareholder, ShareIssuance) and use cases (e.g., AuthenticateUser, CreateIssuance) for pure business logic, independent of external frameworks.
- **Adapters Layer**: Includes repositories (e.g., UserRepository using SQLAlchemy for PostgreSQL) for data persistence and controllers (API endpoints) to interface with the outside world.
- **Infrastructure Layer**: Handles external concerns like database connections, PDF generation with ReportLab, and caching with Redis.

Architectural decisions:
- Authentication: JWT-based with role-based access control (admin vs. shareholder). Enhanced security with bcrypt for password hashing, rate limiting via slowapi, CORS middleware, and validated JWT claims (issuer, audience).
- Database: PostgreSQL for relational data, with connection pooling for better performance.
- Scalability: Added Redis caching for query-heavy operations (e.g., shareholder lists) to reduce DB load. The app supports multi-worker deployment via Uvicorn/Gunicorn.
- PDF Generation: On-the-fly using ReportLab with watermarks.
- Bonus Features: Audit trail with an AuditEvent model, advanced validations (e.g., positive shares, existent shareholders), and simulated email notifications (console logs).
- Testing: Unit tests for use cases (e.g., validation logic) and integration tests for API endpoints using pytest and FastAPI's TestClient.
- Security Fixes: Addressed vulnerabilities like weak hashing, hardcoded secrets (now env-loaded), and added HTTPS support via Nginx in Docker Compose for production-like setups.
- Scalability Enhancements: Dockerized for easy horizontal scaling, with async potential (sync for simplicity, but extensible to asyncpg).

This design promotes testability, maintainability, and extensibility while meeting the spec's API contract.

## Prerequisites
- Python 3.10 or higher (for local non-Docker setup).
- PostgreSQL 14+ installed and running locally.
- Redis 7+ installed and running locally (for caching).
- Docker and Docker Compose (recommended for containerized setup, handles dependencies automatically).
- Git for cloning the repository.

## Setup and Run Locally

### Option 1: Without Docker (Direct Local Setup)
1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables: Create a `.env` file in the root directory with the following:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/captable_db
   JWT_SECRET=your_strong_random_secret_key_here  # Generate a secure key, e.g., using openssl rand -hex 32
   REDIS_HOST=localhost
   SEED_DATA=true  # Set to 'true' to seed initial data (admin and sample shareholder); set to 'false' in production
   ```
you can use the `.env.example` file provided in the repo, rename it as .env and modify to set the correct values of the variables.

5. Set up PostgreSQL:
   - Start PostgreSQL if not running.
   - Create the database: `createdb captable_db` (or use psql: `psql -c "CREATE DATABASE captable_db;"`).
   - The app will automatically create tables on startup.

6. Set up Redis: Ensure Redis is running on localhost:6379 (default).

7. Run the application:
   ```
   python app/main.py
   ```
   - The API will be available at `http://localhost:8000`.
   - For multi-worker mode (better scalability): `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`.
   - Access API docs at `http://localhost:8000/docs`.
   - Seeded credentials (if SEED_DATA=true): Admin (username: admin, password: adminpass), Shareholder (username: shareholder1, password: shpass).

### Option 2: With Docker (Recommended for Isolation and Scalability)
1. Clone the repository (as above).

2. Set up environment variables: Create or update `.env` with at least `JWT_SECRET=your_strong_random_secret_key_here`. Other vars like DATABASE_URL are handled in docker-compose.yml.

3. Build and run:
   ```
   docker-compose up --build
   ```
   - This starts the backend (FastAPI), PostgreSQL, Redis, and Nginx (for HTTPS proxy in production simulation).
   - The API will be available at  `http://localhost:8000` (or `http://localhost` `https://localhost` HTTPS via Nginx on port 443 if certs are mounted).
   - Mount SSL certs in `./certs` for full HTTPS (e.g., using Let's Encrypt; for local, self-signed certs work).
   - To seed data, set SEED_DATA=true in the backend service environment in docker-compose.yml or .env.
   - Stop with `docker-compose down`.

Note: For local testing, use tools like Postman or curl to interact with endpoints (e.g., POST /api/token/ for login). The app runs on localhost only; no deployment to Vercel/etc. as per instructions.

## Primary AI Tools Used
- GitHub Copilot: For code completions and suggestions during implementation.
- Cursor's Chat: For generating boilerplate code structures and debugging assistance.
- Gemini Advanced: For architectural advice on Clean Architecture implementation and security best practices.

## Key Prompts Used
- "Generate a Python backend using FastAPI and Clean Architecture for a cap table management system. Include entities for User, Shareholder, ShareIssuance; use cases for authentication, listing shareholders, issuing shares; repositories with SQLAlchemy for PostgreSQL; and API controllers. Follow this API contract: [pasted spec]."
- "How to implement JWT authentication in FastAPI with role-based access, including token creation and validation with issuer and audience claims?"
- "Add bcrypt password hashing to this User creation and authentication code: [pasted code snippet]."
- "Implement Redis caching for a list endpoint in FastAPI to cache shareholder data, including cache invalidation on mutations."
- "Write unit tests using pytest for validation logic in a share issuance use case, checking for negative shares and non-existent shareholders."
- "Create a Dockerfile and docker-compose.yml for a FastAPI app with PostgreSQL, Redis, and Nginx for HTTPS, including environment variable handling."

(These prompts significantly accelerated structuring the layers, securing the app, and containerizing it.)
