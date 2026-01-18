# Quiz Engine API

A robust and scalable backend for a Quiz Management System built with **FastAPI**. This engine allows users to create categories, design complex quizzes with multiple-choice questions, and take attempts with real-time scoring.

### Key Features:
* **User Authentication**: Secure signup and login using JWT (JSON Web Tokens).
* **Quiz Management**: Full CRUD for quizzes, questions, and answer choices.
* **Timed Attempts**: Track when a user starts and finishes a quiz, with built-in time limit support.
* **Automated Scoring**: Instant calculation of quiz results upon submission.
* **Database Migrations**: Managed by Alembic for easy schema updates.


## Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python web framework)
* **Database:** [PostgreSQL](https://www.postgresql.org/) (Primary relational database)
* **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Modern style with type hinting)
* **Data Validation:** [Pydantic V2](https://docs.pydantic.dev/) (Fast and strict schema enforcement)
* **Authentication:** [Python-jose](https://python-jose.readthedocs.io/) (JWT tokens) and [Passlib](https://passlib.readthedocs.io/) (Bcrypt hashing)
* **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
* **Testing:** [Pytest](https://docs.pytest.org/) and [HTTPX](https://www.python-httpx.org/) (Asynchronous testing)


## Installation & Setup

Follow these steps to get the project running on your local machine:

### 1. Clone the repository
```bash
git clone https://github.com/Allcode-1/quiz-engine-fastapi
cd qwiz_pp
```

### 2. Set up a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
### create a .env file in the root directory and add your configuration:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
SECRET_KEY=your_very_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run database migrations
```bash
alembic upgrade head
```

### 6. Start the application
```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000. Check out the interactive documentation (Swagger) at http://127.0.0.1:8000/docs.

## Running Tests

The project uses Pytest with an isolated SQLite database for testing.
```bash
python -m pytest
```

## Docker Deployment
You can run the entire project (API + Database) using Docker:
```bash
docker-compose up --build
```