
Built by https://www.blackbox.ai

---

# TaskFlow Backend

## Project Overview
TaskFlow is a task management application that provides users with the capability to create boards, lists, and cards to organize their tasks efficiently. This application is built with Flask and adheres to RESTful API principles. It supports user registration, authentication via JWT, and features collaborative board management.

## Installation

To set up the development environment for the TaskFlow backend, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd taskflow-backend
   ```

2. **Install Docker and Docker Compose:**  
   Make sure you have Docker and Docker Compose installed on your machine. You can download it from [Docker's official website](https://docs.docker.com/get-docker/).

3. **Build and start the application:**
   Using Docker Compose, you can build and run the application with the following command:
   ```bash
   docker-compose up
   ```

   This will start both the backend application and a PostgreSQL database.

## Usage

After starting the application, you can access the API Documentation via Swagger UI by navigating to [http://localhost:5000/apidocs](http://localhost:5000/apidocs).

To interact with the API, you can use tools like Postman or curl for testing the endpoints. The default Flask server runs at `http://localhost:5000` by default.

### Example API Calls
- **Register a User:**
  ```bash
  POST /api/auth/register
  {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword"
  }
  ```

- **Login:**
  ```bash
  POST /api/auth/login
  {
    "username": "testuser",
    "password": "testpassword"
  }
  ```

## Features

- User registration and authentication via JWT.
- Create, read, update, and delete boards, lists, and cards.
- Collaborative features (adding and removing members from boards).
- Built-in API documentation through Swagger UI.
- Environment-based configuration (development, production, testing).

## Dependencies

The project uses the following libraries (check `Dockerfile` for complete list):
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Requests (for testing)

## Project Structure

Here is a high-level overview of the project structure:

```
.
├── docker-compose.yml       - Docker configuration for services
├── run.py                   - Entry point for the Flask application
└── config.py                - Configuration settings for Flask application
└── test_api_endpoints.py    - Script for testing API endpoints
```

### Configuration File
- `config.py`: Contains configurations for various environments (Development, Production, Testing), including secret keys, database connections, and JWT settings.

### Docker Compose File
- The `docker-compose.yml` file defines the services required to run the application, including the backend application and a PostgreSQL database, along with their respective environment variables and health checks.

## License
This project is licensed under the MIT License.