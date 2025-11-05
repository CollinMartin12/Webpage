---
noteId: "5698b700ba3411f08f27abef19fb4acc"
tags: []

---

# Microblog Docker Setup

This project uses Docker Compose to set up a MariaDB database and Flask web application.

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web application: http://localhost:5000
   - MariaDB: localhost:3306

## Database Configuration

The setup creates a MariaDB container with the following configuration:
- **Database:** `microblog_db`
- **User:** `microblog_user`
- **Password:** `microblog_password`
- **Root Password:** `rootpassword`

## Features

- **Automatic Database Initialization:** The database is created and initialized every time the containers start
- **Table Creation:** Flask models are automatically converted to database tables
- **Health Checks:** The web application waits for the database to be ready before starting
- **Persistent Data:** Database data is stored in a Docker volume

## Development Commands

- **Start containers in background:**
  ```bash
  docker-compose up -d
  ```

- **View logs:**
  ```bash
  docker-compose logs -f
  ```

- **Stop containers:**
  ```bash
  docker-compose down
  ```

- **Remove all data (including database volume):**
  ```bash
  docker-compose down -v
  ```

- **Rebuild containers:**
  ```bash
  docker-compose up --build
  ```

## File Structure

- `Dockerfile` - Flask application container configuration
- `docker-compose.yml` - Multi-container orchestration
- `wait-for-db.sh` - Database readiness check script
- `init-db/01-init.sql` - Database initialization script
- `create_tables.py` - Flask application table creation

## Environment Variables

The following environment variables are used in the Docker setup:

### Web Container
- `FLASK_APP=microblog`
- `FLASK_ENV=development`
- `DB_HOST=mariadb`
- `DB_PORT=3306`
- `DB_USER=microblog_user`
- `DB_PASSWORD=microblog_password`
- `DB_NAME=microblog_db`

### Database Container
- `MYSQL_ROOT_PASSWORD=rootpassword`
- `MYSQL_DATABASE=microblog_db`
- `MYSQL_USER=microblog_user`
- `MYSQL_PASSWORD=microblog_password`

## Troubleshooting

1. **Database connection issues:**
   - Check if MariaDB container is running: `docker-compose ps`
   - View database logs: `docker-compose logs mariadb`

2. **Table creation issues:**
   - Check web application logs: `docker-compose logs web`
   - Manually create tables: `docker-compose exec web python create_tables.py`

3. **Reset everything:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```
